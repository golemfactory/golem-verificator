import unittest
from golem_verificator.docker.blender.images.scripts.redundancy.subtask import Rectangle

class TestRectangle(unittest.TestCase):

    def setUp(self):
        self.rectangle = Rectangle(0, 400, 0, 600)

    def test_intersect_contain(self):
        other = Rectangle(0, 100, 0, 100 )

        result = self.rectangle.intersect(other)
        assert result.to_vec() ==  (0,0,100,100)

    def test_intersect_not_contain(self):
        other = Rectangle(400, 402, 600, 602 )
        
        result = self.rectangle.is_intersect(other)
        assert result == False