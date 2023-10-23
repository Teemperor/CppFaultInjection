#!/usr/bin/env python3

import json
import os
import sys
import argparse
import glob
import subprocess as sp
from pathlib import Path

parser = argparse.ArgumentParser(description="Performs fault injection")
parser.add_argument("--verbose", dest="verbose", action="store_true", default=None)
parser.add_argument("files", nargs="+")

args = parser.parse_args()

verbose = args.verbose

original_path = os.path.dirname(os.path.abspath(sys.argv[0])) + "/"


def get_compilation_cmd(src_file):
    paths = glob.glob("compile_commands.json", recursive=True)
    for db in paths:
        f = open(db, "r")
        j = json.load(f)
        for info in j:
            file_path = info["file"]
            if os.path.abspath(file_path) == src_file:
                # Add the include path to our fault header.
                info["command"] += " -I " + original_path + "/include"
                return info
    raise RuntimeError("Can't find compilation cmd for " + src_file)


def get_ast(info):
    cmd = info["command"] + " -fno-color-diagnostics -Xclang -ast-dump=json "
    res = sp.run(cmd, cwd=info["directory"], shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return json.loads(res.stdout.decode("utf-8"))


def compile_file(info):
    try:
        sp.check_call(
            info["command"],
            cwd=info["directory"],
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        return True
    except Exception as e:
        print(e)
        return False


class ReplaceData:
    Integer = 1
    Prepend = 2


def is_void_func(func):
    if not "type" in func.keys():
        return False

    return "'void (" in str(func["type"])


def is_int_func(func):
    if not "type" in func.keys():
        return False

    types = ["int", "long", "unsigned int", "unsigned long", "std::size_t", "size_t"]
    for type in types:
      if "'" + type + " (" in str(func["type"]):
          return True
    return False

def is_bool_func(func):
    if not "type" in func.keys():
        return False

    return "'bool (" in str(func["type"])

def can_make_stmt_conditional(stmt):
    if not "kind" in stmt.keys():
        return False
    kind = stmt["kind"]

    bad_kinds = ["DeclStmt", "ReturnStmt", "ForStmt", "WhileStmt", "CXXForRangeStmt"]
    return not kind in bad_kinds

def get_replace_data(node, parent, surrounding_func, in_loop):
    # Don't replace things from included files.
    if "loc" in node.keys():
        if "includedFrom" in node["loc"].keys():
            return []
    if "range" in node.keys():
        begin_keys = node["range"]["begin"].keys()
        if "expansionLoc" in begin_keys:
            return []
        if "includedFrom" in begin_keys:
            return []
        if not "offset" in begin_keys:
            return []

    result = []

    if "kind" in parent.keys() and parent["kind"] == "CompoundStmt":
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
        if kind == "IntegerLiteral":
            result.append([ReplaceData.Integer, node])

    return result


def find_nodes_to_instrument(ast, parent=None, surrounding_func=None, in_loop=False):
    result = []

    result += get_replace_data(ast, parent, surrounding_func, in_loop)

    if "kind" in ast.keys():
        if ast["kind"] in ["CXXMethodDecl", "FunctionDecl"]:
            surrounding_func = ast
        if ast["kind"] in ["WhileStmt", "ForStmt", "CXXForRangeStmt"]:
            in_loop = True

    if "inner" in ast.keys():
        for subnode in ast["inner"]:
            result += find_nodes_to_instrument(subnode, ast, surrounding_func, in_loop)

    return result


def inject_macro_in_text(text, node_data):
    node_kind = node_data[0]
    node = node_data[1]
    offset = node["range"]["begin"]["offset"]

    result = text[:offset]
    if node_kind == ReplaceData.Integer:
        offsetEnd = offset + node["range"]["begin"]["tokLen"]
        result += "FAULT_INT("
        result += text[offset:offsetEnd]
        result += ")"
        result += text[offsetEnd:]
    elif node_kind == ReplaceData.Prepend:
        result += node_data[2] + " " + text[offset:]

    return result


def inject_macro_in_file(src_file, node, compile_info):
    with open(src_file, "r") as f:
        original_content = f.read()

    content = inject_macro_in_text(original_content, node)

    with open(src_file, "w") as f:
        f.write(content)

    if not compile_file(compile_info):
        with open(src_file, "w") as f:
            f.write(original_content)
        return False
    return True



def instrument_file(src_file):
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

    for node in nodes:
        node_str = str(node[1])
        node_str = node_str[0:80] + " []...]"
        print("  -> Replacing: " + node_str)
        replaced = inject_macro_in_file(src_file, node, info)
        if replaced:
            print("   ✅ Replaced node")
        else:
            print("   ❌ Failed to replace node")


for f in args.files:
    print("Processing " + f)
    instrument_file(f)
