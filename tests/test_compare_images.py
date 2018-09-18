from unittest import TestCase
from PIL import Image
from golem_verificator.docker.blender.images.scripts import img_metrics_calculator
import numpy
import os

class TestCompare_images(TestCase):
    def test_compare_images(self):
        # folder_path = os.path.join("tests", "pilcrop_vs_cropwindow_test")
        # image_path = os.path.join(folder_path, '0.209 0.509 0.709 0.909.png')
        img_metrics_calculator.TREE_PATH = os.path.normpath("golem_verificator/docker/blender/images/scripts/tree35_[crr=87.71][frr=0.92].pkl") 
        image = Image.open(os.path.normpath("tests/pilcrop_vs_cropwindow_test/0.209 0.509 0.709 0.909.png"))
        result = img_metrics_calculator.default_compare_images( image, image )
        assert result == 'TRUE'

        image2 = Image.new( "RGB", image.size ) # Image.fromarray( numpy.zeros( image.size ) )
        result = img_metrics_calculator.default_compare_images( image, image2 )
        assert result == 'FALSE'

