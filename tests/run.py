#!/usr/bin/env python3

import shutil
import sys
import os
import subprocess as sp

tmp_path = "/tmp/fault-injection-tmp"

project_path = os.path.realpath(os.path.join(os.getcwd(), ".."))
fault_script = os.path.join(project_path, "inject-faults.py")

def run_test(name):
    shutil.rmtree(tmp_path, ignore_errors=True)
    shutil.copytree(name, tmp_path)

    compile_db = tmp_path + "/compile_commands.json"
    with open(compile_db, "w") as f:
        f.write("""[
  {
    "directory": \"""" + tmp_path + """\",
    "command": "/usr/bin/clang++ main.cpp -o main.o",
    "file": "main.cpp"
  }
]
""")

    sp.run([fault_script, "main.cpp"], cwd=tmp_path)

    #shutil.rmtree(tmp_path)

run_test("test1")