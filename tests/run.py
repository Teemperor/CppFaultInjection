#!/usr/bin/env python3

import argparse
import shutil
import sys
import os
import subprocess as sp


class COL:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


parser = argparse.ArgumentParser(description="Runs tests")
parser.add_argument("--keep", dest="keep", action="store_true", default=None)
parser.add_argument("--fix", dest="fix", action="store_true", default=None)
parser.add_argument("files", nargs="*")

args = parser.parse_args()

tmp_path = "/tmp/fault-injection-tmp"

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
main_dir = os.path.realpath(script_directory + "/..")
fault_script = os.path.join(main_dir, "inject-faults.py")


def run_test(name):
    shutil.rmtree(tmp_path, ignore_errors=True)
    shutil.copytree(name, tmp_path)

    compile_db = tmp_path + "/compile_commands.json"
    with open(compile_db, "w") as f:
        f.write(
            """[
  {
    "directory": \""""
            + tmp_path
            + """\",
    "command": "/usr/bin/clang++ input.cpp -c -o main.o",
    "file": "input.cpp"
  }
]
"""
        )

    sp.run([fault_script, "input.cpp"], cwd=tmp_path)

    if args.fix:
        shutil.copy(tmp_path + "/input.cpp", name + "/expected.cpp")
    else:
        sp.check_call(["diff", "-U3", "input.cpp", "expected.cpp"], cwd=tmp_path)

        if not args.keep:
            shutil.rmtree(tmp_path)


if len(args.files) == 0:
    print("Running all tests")
    args.files = []
    for x in os.listdir(script_directory):
        if os.path.isdir(x):
            args.files.append(x)

for x in args.files:
    print(COL.BOLD + "\n • Test " + x + COL.ENDC)
    try:
        run_test(x)
        print(COL.OKGREEN + " [ PASS ]" + COL.ENDC)
    except Exception as e:
        print(COL.FAIL + " [ FAIL ]" + COL.ENDC)
        print("Reason:" + str(e))
