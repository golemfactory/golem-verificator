import os
from unittest import TestCase

from golem_verificator.lux.generate_lux_stats import generate_stats


# FIXME get rid of golem-PIL-helpers switch to opencv
class TestGenerateStats(TestCase):
    def test_values(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir_path, "files_for_tests")
        img1 = os.path.join(path, "bleh1.exr")
        img2 = os.path.join(path, "bleh2.exr")
        assert os.path.isfile(img1)
        assert os.path.isfile(img2)
        stats = generate_stats(img1, img2)
        assert round(stats["ssim"], 2) == 0.17
        assert round(stats["mse"], 2) == 0.07
        assert stats["norm_mse"] < 4.15e-11
        assert round(stats["psnr"], 2) == 59.96
        assert round(stats["mse_bw"], 2) == 3640.71
