from unittest import TestCase

import os
import shlex
import subprocess
from subprocess import PIPE


class TestGenerateBlenderImage(TestCase):
    def setUp(self):

        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        tests_dir_path = \
            os.path.abspath(os.path.join(self.dir_path, os.pardir))

        self.golem_verificator_home_dir_path = \
            os.path.abspath(os.path.join(tests_dir_path, os.pardir))

        self.validation_script_path = os.path.join(
            self.golem_verificator_home_dir_path,
            'golem_verificator',
            'scripts', 'validation_parser_runner.py')

        self.blender_scene_path \
            = os.path.join(self.dir_path,
                           'files_for_tests',
                           'bmw27_cpu.blend')

        self.good_img_to_validate_path \
            = os.path.join(self.dir_path,
                          'files_for_tests',
                          'good_image0001.png')

        self.very_bad_img_to_validate_path \
            = os.path.join(self.dir_path,
                          'files_for_tests',
                          'very_bad_image0001.png')

    def test_validation_should_pass(self):
        try:
            cmd = shlex.split(
                self.validation_script_path + " " +
                self.blender_scene_path + " "
                "--crop_window_size 0,1,0,1 "
                "--resolution 150,150 "
                "--rendered_scene " +
                self.good_img_to_validate_path + " "
                "--name_of_excel_file wynik_liczby")

            process\
                = subprocess.run(cmd,
                    stdin=PIPE, stdout=PIPE, stderr=PIPE, check=True)

            stdout = process.stdout.decode()
            # result = stdout.split()
            print(stdout)
            assert process.returncode == 0  # valid img
        except subprocess.CalledProcessError as e:
            print(str(e))
            print(e.stderr.decode())
            print(e.stdout.decode())
            assert False

    def test_validation_should_fail(self):
        try:
            cmd = shlex.split(
                self.validation_script_path + " " +
                self.blender_scene_path + " "
                "--crop_window_size 0,1,0,1 "
                "--resolution 150,150 "
                "--rendered_scene " +
                self.very_bad_img_to_validate_path + " "
                "--name_of_excel_file wynik_liczby")

            process \
                = subprocess.run(cmd,
                    stdin=PIPE, stdout=PIPE, stderr=PIPE, check=True)

            stdout = process.stdout.decode()
            # result = stdout.split()
            print(stdout)
            assert process.returncode == 0  # valid img
        except subprocess.CalledProcessError as e:
            print(str(e))
            print(e.stderr.decode())
            print(e.stdout.decode())

            assert e.returncode == 255
