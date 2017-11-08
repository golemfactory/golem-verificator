import os
from unittest import TestCase

from lux.gen_file import generate_luximage, generate_img_with_params
from imgs.imgrepr import load_img


class TestGenerateLuxImage(TestCase):
    def remove_files(self):
        if os.path.isfile(self.out_file):
            os.remove(self.out_file)
        if os.path.isfile(self.out_file2):
            os.remove(self.out_file2)

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.scene_dir = "luxtestdata"
        self.out_file = os.path.join(self.dir_path, self.scene_dir,
                                     "LuxRender08_test_scene.Scene.00001.png")
        self.out_file2 = os.path.join(self.dir_path, self.scene_dir,
                                      "test_scene_1.png")
        self. lux_scene = os.path.join(self.dir_path, self.scene_dir,
                                       "schoolcorridor.lxs")
        self.remove_files()

    def tearDown(self):
        self.remove_files()

    def test_generate_lux_image(self):
        generate_luximage(self.lux_scene)
        assert os.path.isfile(self.out_file)

        generate_luximage(self.lux_scene, self.out_file2)

        assert os.path.isfile(self.out_file2)

    def test_generate_lux_image_with_changed_params(self):

        generate_img_with_params(self.lux_scene)
        assert os.path.isfile(os.path.join(self.dir_path, self.scene_dir,
                                           "tmp.lxs"))
        assert os.path.isfile(self.out_file)

        # generate left lower corner
        generate_img_with_params(self.lux_scene, crop=[0, 0.25, 0.75, 1],
                                 output=self.out_file2, xres=1000, yres=500,
                                 haltspp=5)
        assert os.path.isfile(self.out_file2)
        img_repr = load_img(self.out_file2)
        assert img_repr.get_size() == (1000, 500)
        assert img_repr.get_pixel((0, 0)) == [0, 0, 0]
        assert img_repr.get_pixel((0, 499)) != [0, 0, 0]
        assert img_repr.get_pixel((243, 480)) != [0, 0, 0]
        assert img_repr.get_pixel((250, 480)) == [0, 0, 0]





