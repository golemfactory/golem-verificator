import os
import shlex
import subprocess

# you may need to: $ chmod +x ./validation.py
# you may need to: $ chmod +x ./generate_blender_images.py


subprocess.call(shlex.split("./generate_blender_images.py benchmark_blender/bmw27_cpu.blend "
                            "--output good_image "
                            "--xres 150 "
                            "--yres 150"))

subprocess.call(shlex.split("./validation.py benchmark_blender/bmw27_cpu.blend "
                            "--crop_window_size 0,1,0,1 "
                            "--resolution 150,150 "
                            "--rendered_scene benchmark_blender/good_image0001.png "
                            "--name_of_excel_file wynik_liczby"))

# python3 ./generate_blender_images.py benchmark_blender/bmw27_cpu.blend --output good_image --xres 150 --yres 150

# python3 ./validation.py benchmark_blender/bmw27_cpu.blend --crop_window_size 0,1,0,1 --resolution 150,150 --rendered_scene benchmark_blender/good_image0001.png --name_of_excel_file wynik_liczby
