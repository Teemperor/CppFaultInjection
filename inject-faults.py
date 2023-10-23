#!/usr/bin/env python3

import json
import os
import sys
import argparse
import glob
import subprocess as sp
from pathlib import Path

original_path = os.path.dirname(os.path.abspath(sys.argv[0])) + "/"

def get_compilation_cmd(src_file):
    paths = glob.glob('compile_commands.json', recursive=True)
    for db in paths:
        f = open(db, "r")
        j = json.load(f)
        for info in j:
            file_path = info["file"]
            if os.path.abspath(file_path) == src_file:
                print(info["command"])
                info["command"] += " -I " + original_path + "/include"
                return info
    raise RuntimeError("Can't find compilation cmd for " + src_file)

def get_ast(info):
    cmd = info["command"] + " -fno-color-diagnostics -Xclang -ast-dump=json "
    res = sp.run(cmd, cwd=info["directory"], shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return json.loads(res.stdout.decode("utf-8"))

def compile_file(info):
    try:
        sp.check_call(info["command"], cwd=info["directory"], shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        return True
    except Exception as e:
        print(e)
        return False

class ReplaceData:
    Integer = 1
    InsertBreak = 2

def get_replace_data(node, surrounding_func, in_loop):
    # Don't replace things from included files.
    if "loc" in node.keys():
        if 'includedFrom' in node["loc"].keys():
            return None
    if "range" in node.keys():
        begin_keys = node["range"]["begin"].keys()
        if 'expansionLoc' in begin_keys:
            return None
        if 'includedFrom' in begin_keys:
            return None
        if not "offset" in begin_keys:
            return None
        
    if "kind" in node.keys():
        kind = node["kind"]
        if kind == "IntegerLiteral":
            return [ReplaceData.Integer, node]
    return None

def find_nodes_to_instrument(ast, surrounding_func = None, in_loop = False):
    result = []

    replace_data = get_replace_data(ast, surrounding_func, in_loop)
    if replace_data:
        result.append(replace_data)

    if "kind" in ast.keys():
        if ast["kind"] in ["CXXMethodDecl", "FunctionDecl"]:
            surrounding_func = ast
        if ast["kind"] in ["WhileStmt", "ForStmt", "CXXForRangeStmt"]:
            in_loop = True

    if 'inner' in ast.keys():
        for subnode in ast["inner"]:
            result += find_nodes_to_instrument(subnode, surrounding_func, in_loop)

    return result

def inject_macro_in_text(text, node_data):
    node = node_data[1]
    offset = node["range"]["begin"]["offset"]
    offsetEnd = offset + node["range"]["begin"]["tokLen"]

    result = text[:offset]
    result += "FAULT_INT("
    result += text[offset:offsetEnd]
    result += ")"
    result += text[offsetEnd:]

    return result

def inject_macro_in_file(src_file, node):
    with open(src_file, "r") as f:
        content = f.read()
    
    content = inject_macro_in_text(content, node)

    with open(src_file, "w") as f:
        f.write(content)

def instrument_file(src_file):
    src_file = os.path.realpath(src_file)
    print("Finding compilation args...")
    info = get_compilation_cmd(src_file)
    print("Parsing AST...")
    ast = get_ast(info)

    if not compile_file(info):
        print("Failed to compile initial file")
        sys.exit(1)

    print("Finding nodes to replace...")
    nodes = find_nodes_to_instrument(ast)

    nodes.reverse()

    for node in nodes:
        print(node[1])
        inject_macro_in_file(src_file, node)

instrument_file(sys.argv[1])