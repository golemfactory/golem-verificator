import os
from unittest import TestCase

from blender.gen_file import generate_blenderimage, generate_img_with_params
from imgs.imgrepr import load_img


class TestGenerateBlenderImage(TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.scene_dir = "blendertestdata"
        self.scene_file = os.path.join(self.dir_path, self.scene_dir,
                                       "scene-Helicopter-27-cycles.blend")
        self.out_file = os.path.join(self.dir_path, self.scene_dir,
                                      "myimage_###.png")
        self.real_out_file1 = os.path.join(self.dir_path, self.scene_dir,
                                           "myimage_001.png")
        self.real_out_file3 = os.path.join(self.dir_path, self.scene_dir,
                                          "myimage_003.png")

    def remove_files(self):
        if os.path.isfile(self.real_out_file1):
            os.remove(self.real_out_file1)
        if os.path.isfile(self.real_out_file3):
            os.remove(self.real_out_file3)

    def tearDown(self):
        self.remove_files()

    def test_generate_blender_image(self):
        generate_blenderimage(self.scene_file, output=self.out_file)
        assert os.path.isfile(self.real_out_file1)
        img_repr = load_img(self.real_out_file1)
        assert img_repr.get_size() == (1920, 1080)

        generate_blenderimage(self.scene_file, output=self.out_file,
                              frame=3)
        assert os.path.isfile(self.real_out_file3)

    def test_generate_blender_image_with_params(self):
        generate_img_with_params(self.scene_file, output=self.out_file)
        assert os.path.isfile(self.real_out_file1)
        img_repr = load_img(self.real_out_file1)
        assert img_repr.get_size() == (800, 600)

        generate_img_with_params(self.scene_file, xres=1000, yres=400,
                                 crop=[0, 0.25, 0.75, 1], use_compositing=True,
                                 output=self.out_file, frame=3)
        assert os.path.isfile(self.real_out_file3)
        img_repr = load_img(self.real_out_file3)
        assert img_repr.get_size() == (250, 100)
