#!/usr/bin/env python

# THIS FILE IS FOR TESTS

import os
import shlex
import subprocess
from subprocess import PIPE

# you may need to: $ chmod +x ./validation.py
# you may need to: $ chmod +x ./generate_blender_images.py


# subprocess.run(shlex.split("./generate_blender_images.py "
#                             "../benchmark_blender/bmw27_cpu.blend "
#                             "--output good_image "
#                             "--xres 150 "
#                             "--yres 150"))

try:
    c = subprocess.run(shlex.split("./scripts/validation.py "
                                   "../benchmark_blender/bmw27_cpu.blend "
                                   "--crop_window_size 0,1,0,1 "
                                   "--resolution 150,150 "
                                   "--rendered_scene "
                                   "../benchmark_blender/bad_image0001.png "
                                   "--name_of_excel_file wynik_liczby"),
                       stdin=PIPE, stdout=PIPE, stderr=PIPE, check=True)
    stdout = c.stdout.decode()
    # result = stdout.split()
    print("SubtaskVerificationState.VERIFIED process return code:"
          + str(c.returncode))
    print(stdout)
except subprocess.CalledProcessError as e:
    print(e.stderr.decode())
    print(e.stdout.decode())

print(" --- Happy End --- ")
