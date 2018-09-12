from unittest import TestCase
from PIL import Image
from golem_verificator.docker.blender.images.scripts.img_metrics_calculator import default_compare_images

class TestCompare_images(TestCase):
    def test_compare_images(self):
        # folder_path = os.path.join("tests", "pilcrop_vs_cropwindow_test")
        # image_path = os.path.join(folder_path, '0.209 0.509 0.709 0.909.png')
        image = Image.open( "tests\\pilcrop_vs_cropwindow_test\\0.209 0.509 0.709 0.909.png")
        result = default_compare_images( image, image )
        assert result
