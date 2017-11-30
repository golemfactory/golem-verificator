#!/usr/bin/env python

# THIS FILE IS FOR TESTS

import os
import shlex
import subprocess
from subprocess import PIPE

# you may need to: $ chmod +x ./validation_parser_runner.py
# you may need to: $ chmod +x ./generate_blender_images.py


try:
    cmd = "./scripts/validation_parser_runner.py " \
    "../benchmark_blender/bmw27_cpu.blend " \
    "--crop_window_size 0,1,0,1 " \
    "--resolution 150,150 " \
    "--rendered_scene " \
    "../benchmark_blender/bad_image0001.png " \
    "--name_of_excel_file wynik_liczby"  # noqa

    process = subprocess.run(
        shlex.split(cmd),
        stdin=PIPE, stdout=PIPE, stderr=PIPE, check=True)

    stdout = process.stdout.decode()
    print("SubtaskVerificationState.VERIFIED process return code:"
          + str(process.returncode))
    print(stdout)
except subprocess.CalledProcessError as e:
    print(" --- Error --- ")
    print(str(e))
    print(str(e.stdout.decode()))
    print(str(e.stderr.decode()))


print(" --- End --- ")
