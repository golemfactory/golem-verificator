import os
from unittest import TestCase

from generate_stats import generate_stats


class TestGenerateStats(TestCase):
    def test_values(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        img1 = os.path.join(dir_path, "bleh1.exr")
        img2 = os.path.join(dir_path, "bleh2.exr")
        assert os.path.isfile(img1)
        assert os.path.isfile(img2)
        stats = generate_stats(img1, img2)
        assert round(stats["ssim"], 2) == 0.17
        assert round(stats["mse"], 2) == 0.07
        assert stats["norm_mse"] < 4.15e-11
        assert round(stats["psnr"], 2) == 59.96
        assert round(stats["mse_bw"], 2) == 3640.71
