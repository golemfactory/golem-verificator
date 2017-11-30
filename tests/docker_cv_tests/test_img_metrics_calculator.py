import os
from unittest import TestCase

from Docker_CV.scripts.img_metrics_calculator import \
    compare_crop_window

from Docker_CV.scripts.imgmetrics import ImgMetrics

import shlex
import subprocess
from subprocess import PIPE



class TestImgMetricsCalculator(TestCase):
    def setUp(self):

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.scene_dir = os.path.join(self.dir_path, "files_for_tests")

        self.real_rendered_scene = os.path.join(self.scene_dir,
                                                "good_image0001.png")

        self.real_cropped_img = os.path.join(self.scene_dir,
                                             "10001.png")
        self.res_x = 73
        self.res_y = 62

        self.temp_file_path = 'path'

        self.params_file_path = os.path.join(self.scene_dir, "params.py")

    def remove_files(self):
        if os.path.isfile(self.temp_file_path):
            os.remove(self.temp_file_path)

        if os.path.isfile(self.params_file_path):
            pass
            # os.remove(self.params_file_path)

    def tearDown(self):
        self.remove_files()

    def test_compare_crop_window(self):
        assert not os.path.isfile(self.temp_file_path)
        self.temp_file_path = compare_crop_window(
            cropped_img_path=self.real_cropped_img,
            rendered_scene_path=self.real_rendered_scene,
            xres=self.res_x, yres=self.res_y)

        img_metrics = ImgMetrics.load_from_file(self.temp_file_path)

        assert img_metrics.imgCorr == 0.27154471544715447
        assert img_metrics.SSIM_normal == 0.9996764809235005
        assert img_metrics.MSE_normal == 0.2222222222222222
        assert img_metrics.SSIM_canny == 0.8935528811475285
        assert img_metrics.MSE_canny == 2408.3333333333335
        assert img_metrics.SSIM_wavelet == 0.9285589552179234
        assert img_metrics.MSE_wavelet == 1300.61
        assert img_metrics.crop_resolution == "9x9"

    def test_docker_img_metric_task(self):
        parameters = {
            "cropped_img_path": "/golem/resources/10001.png",
            "rendered_scene_path": "/golem/resources/good_image0001.png",
            "xres": self.res_x,
            "yres": self.res_y,
        }

        with open(self.params_file_path, "wb") as params_file:
            for key, value in parameters.items():
                line = "{} = {}\n".format(key, repr(value))
                params_file.write(bytearray(line, encoding='utf-8'))

        try:
            cmd =  "docker run -i --rm " \
                   "--mount type=bind," \
                   "source=" + self.scene_dir + ",target=/golem/resources " \
                   "--mount type=bind," \
                   "source=" + self.params_file_path + ",target=/golem/work/params.py " \
                   "golemfactory/img_metrics"

            process = subprocess.run(
                shlex.split(cmd),
                stdin=PIPE, stdout=PIPE, stderr=PIPE, check=True)

            stdout = process.stdout.decode()
            print(stdout)

            assert process.returncode == 0
        except subprocess.CalledProcessError as e:
            print(str(e))
            print(str(e.stdout.decode()))
            print(str(e.stderr.decode()))
            assert False
