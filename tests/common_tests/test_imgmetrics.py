import os

from golem_verificator.common.imgmetrics import ImgMetrics
from unittest import TestCase

class TestGenerateBlenderImage(TestCase):
    def setUp(self):
        self.data = {
            "imgCorr": 1,
            "SSIM_normal": 2,
            "MSE_normal": 3,
            "SSIM_wavelet": 4,
            "MSE_wavelet": 5,
            "SSIM_canny": 6,
            "MSE_canny": 7,
            "crop_resolution": 'NxN',
        }

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.file_path = os.path.join(self.dir_path, 'data.txt')

    def remove_files(self):
        os.remove(self.file_path)

    def tearDown(self):
        self.remove_files()

    def test_imgmetrics_io(self):
        img_metrics1 = ImgMetrics(self.data)
        path = img_metrics1.write_to_file(self.file_path)

        img_metrics2 = ImgMetrics.load_from_file(path)

        for k1, k2 in zip(img_metrics1.__dict__, img_metrics2.__dict__):
            v1 = img_metrics1.__dict__.get(k1)
            v2 = img_metrics2.__dict__.get(k2)
            assert v1 == v2