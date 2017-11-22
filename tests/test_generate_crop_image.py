import os
from unittest import TestCase

import cv2

from golem_verificator.blender.gen_file import generate_img_with_params
from golem_verificator.blender.generate_random_crop_images import \
    generate_random_crop

from golem_verificator.scripts.validation import compare_crop_window
import random

# unit tests for correct script working

class TestGenerateBlenderCropImage(TestCase):
    def setUp(self):
        random.seed(0)

        test_dir_path = os.path.dirname(os.path.realpath(__file__))
        self.scene_dir = os.path.join(
            test_dir_path, "files_for_tests","blender")

        self.scene_file_path = os.path.join(self.scene_dir, "bmw27_cpu.blend")

        self.out_file_path_without_suffix = os.path.join(
            test_dir_path,self.scene_dir, 'img_to_check')

        self.blender_suffix = "0001.png"

    def remove_files(self):
        tmp_script_path = os.path.join(self.scene_dir, "tmp.py")

        if os.path.isfile(tmp_script_path):
            os.remove(tmp_script_path)

        blendered_file_path = self.out_file_path_without_suffix + self.blender_suffix
        if os.path.isfile(blendered_file_path):
            os.remove(blendered_file_path)

    def tearDown(self):
        self.remove_files()

    def test_generate_random_crop_image(self):

        scene_format = ".png"
        crop_window = (0.2, 0.5, 0.7, 0.9)
        resolution = (150,150)

        generate_img_with_params(
            self.scene_file_path, xres=resolution[0], yres=resolution[1],
            crop=crop_window, output=self.out_file_path_without_suffix)

        blendered_file_path = self.out_file_path_without_suffix + self.blender_suffix
        assert os.path.isfile(blendered_file_path)
        rendered_img = cv2.imread(blendered_file_path)

        crop_res, crop_output, crop_percentages = \
            generate_random_crop(scene_file=self.scene_file_path,
                                crop_scene_size=crop_window,
                                crop_count=3,
                                resolution=resolution,
                                rendered_scene=rendered_img,
                                scene_format=scene_format,
                                test_number=1)
        xress,yress = crop_res[0]

        imgCorr, SSIM_normal, MSE_normal, SSIM_canny, SSIM_wavelet,MSE_wavelet=\
            compare_crop_window(crop_output[0],rendered_img,
                                xress, yress,crop_percentages[0],resolution)

        # test one of the metrics
        assert MSE_normal == 1.0987654320987654