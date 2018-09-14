from unittest import TestCase

from golem_verificator.docker.blender.images.scripts.redundancy.subtask import Subtask
from golem_verificator.docker.blender.images.scripts.redundancy.subtask import Rectangle
from PIL import Image

class TestSubtask(TestCase):
    def test_find_intersection(self):
        image = Image.open( "tests\\pilcrop_vs_cropwindow_test\\0.209 0.509 0.709 0.909.png")
        width, height = image.size
        rect = Rectangle( 0, width, 0, height )
        task1 = Subtask( rect, image )

        task1.find_intersection( task1 )
