#!/usr/bin/env python3

import json
import os
import sys
import argparse
import glob
import subprocess as sp
from pathlib import Path
from datetime import datetime


parser = argparse.ArgumentParser(description="Performs fault injection")
parser.add_argument("--verbose", dest="verbose", action="store_true", default=None)
parser.add_argument("files", nargs="+")

args = parser.parse_args()

verbose = args.verbose

original_path = os.path.dirname(os.path.abspath(sys.argv[0])) + "/"


def get_compilation_cmd(src_file):
    """
    Returns an object with the compilation database object for the given
    source file. See the compilation database spec for more information.
    """
    paths = glob.glob("./**/compile_commands.json", recursive=True)
    for db in paths:
        print("Searching " + db)
        f = open(db, "r")
        j = json.load(f)
        for info in j:
            file_path = info["file"]
            if os.path.abspath(file_path) == src_file:
                # Add the include path to our fault header.
                info["command"] += " -I " + original_path + "/include -Werror"
                return info
    raise RuntimeError("Can't find compilation cmd for " + src_file)


def get_ast(info):
    """
    Returns a JSON version of the parsed ASP for the given file.
    """
    cmd = info["command"] + " -fno-color-diagnostics -Xclang -ast-dump=json "
    res = sp.run(cmd, cwd=info["directory"], shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return json.loads(res.stdout.decode("utf-8"))


def compile_file(info):
    """
    Try compiling the file for the given compilation info
    (see get_compilation_cmd)/
    Returns true iff compilation was successful.
    """
    try:
        sp.check_call(
            info["command"],
            cwd=info["directory"],
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            timeout=10,
        )
        return True
    except Exception as e:
        if verbose:
            print("Error when compiling:\n" + str(e))
        return False


class ReplaceData:
    # Surround the token with the specified macro.
    Surround = 1
    # Prepend the token with the specified arg-less C macro.
    Prepend = 2


def is_void_func(func):
    if func is None or not "type" in func.keys():
        return False

    return "'void (" in str(func["type"])


int_types = [
    "int",
    "long",
    "unsigned int",
    "unsigned long",
    "size_t",
    "uint64_t",
    "int64_t",
    "int32_t",
    "uint32_t",
    "int16_t",
    "uint16_t",
]
for i in int_types[:]:
    if i.endswith("_t"):
        int_types.append("std::" + i)


def is_int_func(func):
    if func is None or not "type" in func.keys():
        return False

    for type in int_types:
        if "'" + type + " (" in str(func["type"]):
            return True
    return False


def is_bool_func(func):
    if func is None or not "type" in func.keys():
        return False

    return "'bool (" in str(func["type"])


def can_make_stmt_conditional(stmt):
    if not "kind" in stmt.keys():
        return False
    kind = stmt["kind"]

    bad_kinds = [
        "DeclStmt",
        "ReturnStmt",
        "ForStmt",
        "WhileStmt",
        "CXXForRangeStmt",
        "IfStmt",
    ]
    return not kind in bad_kinds


def is_valid_node(node):
    if not "kind" in node.keys():
        return False
    kind = node["kind"]

    bad_kinds = ["ParmVarDecl", "TemplateArgument"]
    return not kind in bad_kinds


def get_replace_data(node, parent, surrounding_func, in_loop):
    ignore_result = [[], True]
    # Don't replace things from included files.
    if "loc" in node.keys():
        if "includedFrom" in node["loc"].keys():
            return ignore_result
    if "range" in node.keys():
        begin_keys = node["range"]["begin"].keys()
        if "expansionLoc" in begin_keys:
            return ignore_result
        if "includedFrom" in begin_keys:
            return ignore_result
        if not "offset" in begin_keys:
            return ignore_result

    should_descend = True
    result = []

    in_compound = False
    if "kind" in parent.keys():
        if parent["kind"] == "CompoundStmt" or parent == surrounding_func:
            in_compound = True
        # As a special case, don't insert faults into static variables as
        # this causes linker errors if there is no mutex support available.
        # i.e., static int x = FAULT(0); requires a mutex and this breaks
        # compilation.
        if surrounding_func and parent["kind"] == "VarDecl":
            if "storageClass" in parent.keys():
                if parent["storageClass"] == "static":
                    should_descend = False
                    return [result, should_descend]

    if in_compound and is_valid_node(node):
        if is_void_func(surrounding_func):
            result.append([ReplaceData.Prepend, node, "FAULT_RETURN"])
        if is_int_func(surrounding_func):
            result.append([ReplaceData.Prepend, node, "FAULT_RETURN_INT"])
        if is_bool_func(surrounding_func):
            result.append([ReplaceData.Prepend, node, "FAULT_RETURN_BOOL"])
        if in_loop:
            result.append([ReplaceData.Prepend, node, "FAULT_BREAK"])
        if can_make_stmt_conditional(node):
            result.append([ReplaceData.Prepend, node, "FAULT_CONDITIONAL"])

    if "kind" in node.keys():
        kind = node["kind"]
        type = ""
        if "type" in node.keys():
            type = node["type"]["qualType"]
        if kind == "BinaryOperator" and type in int_types:
            result.append([ReplaceData.Surround, node, "FAULT_INT"])
        if kind == "IntegerLiteral":
            result.append([ReplaceData.Surround, node, "FAULT_INT"])
        if kind == "DeclRefExpr" and type in int_types:
            result.append([ReplaceData.Surround, node, "FAULT_INT"])

    return [result, should_descend]


def find_nodes_to_instrument(ast, parent=None, surrounding_func=None, in_loop=False):
    result = []

    replacements_and_should_descend = get_replace_data(
        ast, parent, surrounding_func, in_loop
    )
    result += replacements_and_should_descend[0]

    if "kind" in ast.keys():
        if ast["kind"] in ["CXXMethodDecl", "FunctionDecl"]:
            surrounding_func = ast
        if ast["kind"] in ["WhileStmt", "ForStmt", "CXXForRangeStmt"]:
            in_loop = True

    if "inner" in ast.keys() and replacements_and_should_descend[1]:
        for subnode in ast["inner"]:
            result += find_nodes_to_instrument(subnode, ast, surrounding_func, in_loop)

    return result


class TextReplacer:
    def __init__(self):
        self.done_insertions = []

    def __adjust_offset(self, offset):
        for adjustment in self.done_insertions:
            if offset > adjustment[0]:
                offset += adjustment[1]
        return offset

    def insertedText(self, pos, size):
        self.done_insertions.append([pos, size])

    def inject_macro_in_text(self, text, node_data):
        node_kind = node_data[0]
        node = node_data[1]
        macro_name = node_data[2]
        offset = self.__adjust_offset(node["range"]["begin"]["offset"])

        result = text[:offset]
        if node_kind == ReplaceData.Surround:
            offsetEnd = self.__adjust_offset(
                node["range"]["end"]["offset"] + node["range"]["end"]["tokLen"]
            )
            result += macro_name + "("
            result += text[offset:offsetEnd]
            result += ")"
            result += text[offsetEnd:]
            self.insertedText(offset, len(macro_name + "("))
            self.insertedText(offsetEnd, len(")"))

        elif node_kind == ReplaceData.Prepend:
            result += macro_name + " " + text[offset:]
            self.insertedText(offset, len(macro_name + " "))

        return result

    def inject_macro_in_file(self, src_file, node, compile_info):
        with open(src_file, "r") as f:
            original_content = f.read()

        prev_insertions = self.done_insertions[:]

        content = self.inject_macro_in_text(original_content, node)

        with open(src_file, "w") as f:
            f.write(content)

        if not compile_file(compile_info):
            with open(src_file, "w") as f:
                f.write(original_content)
            self.done_insertions = prev_insertions
            return False
        return True


def instrument_file(src_file):
    """
    Instruments the given file with faults.
    """
    src_file = os.path.realpath(src_file)
    print(" * Finding compilation args...")
    info = get_compilation_cmd(src_file)
    print(" * Parsing AST...")
    ast = get_ast(info)

    if verbose:
        print(json.dumps(ast, indent=2))

    if not compile_file(info):
        print("Failed to compile initial file")
        sys.exit(1)

    print(" * Finding nodes to replace...")
    nodes = find_nodes_to_instrument(ast)

    nodes.reverse()

    replacer = TextReplacer()

    total_len = len(nodes)
    current_i = 0
    for node in nodes:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        current_i += 1
        node_str = str(node[1])
        node_str = node_str[0:100] + " [...]"
        print(
            "  -> Replacing: "
            + str(node[0])
            + " "
            + node_str
            + f" ({current_i}/{total_len})  [{current_time}]"
        )
        try:
            replaced = replacer.inject_macro_in_file(src_file, node, info)
            if replaced:
                print("   ✅ Replaced node")
            else:
                print("   ❌ Failed to replace node")
        except Exception as e:
            print("   ❌ error: " + str(e))


for f in args.files:
    print("Processing " + f)
    instrument_file(f)
