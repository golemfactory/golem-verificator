import cv2
import os
from imgs.imgrepr import load_img
from unittest import TestCase
from validation import compare_crop_window, validation
from generate_random_crop_images import generate_random_crop
from blender.gen_file import generate_blenderimage, generate_img_with_params

# unit tests for correct script working

class TestGenerateBlenderCropImage(TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.scene_dir = "crop_test"
        self.compare_dir = 'crop_test/crop_image_compare'
        self.scene_file = os.path.join(
            self.dir_path, self.scene_dir, "Ring_27.blend")
        self.compare_scene = os.path.join(
            self.dir_path, self.compare_dir, 'ring')
        self.out_file = os.path.join(
            self.dir_path, "/tmp/#0001.png")
        self.real_out_file1 = os.path.join(
            self.dir_path, '/tmp/10001.png')
        self.real_out_file2 = os.path.join(
            self.dir_path, '/tmp/20001.png')
        self.real_out_file3 = os.path.join(
            self.dir_path, '/tmp/30001.png')

    def remove_files(self):
        if os.path.isfile(self.real_out_file1):
            os.remove(self.real_out_file1)
        if os.path.isfile(self.real_out_file2):
            os.remove(self.real_out_file2)
        if os.path.isfile(self.real_out_file3):
            os.remove(self.real_out_file3)

    def tearDown(self):
        self.remove_files()

    def check_rendered_scene(self, file_name, resolution, crop_window):
        if os.path.isfile(os.path.join(self.dir_path, self.compare_dir, file_name)):
            return file_name
        else:
            generate_img_with_params(
                self.scene_file, xres=resolution[0], yres=resolution[1], crop=crop_window, output=self.compare_scene)

    def test_generate_random_crop_image(self):

        file_name = "ring0001.png"
        scene_format = ".png"
        crop_window = (0.2, 0.5, 0.7, 0.9)
        resolution = (1600, 915)
        check = self.check_rendered_scene(file_name, resolution, crop_window)
        print(check)
        file_path = self.dir_path + '/' + self.compare_dir + '/' + file_name
        file_path = cv2.imread(file_path)
        crop = generate_random_crop(self.scene_file, crop_window,
                             3, resolution, file_path, scene_format)
        assert os.path.isfile(self.real_out_file1)
        assert os.path.isfile(self.real_out_file2)
        assert os.path.isfile(self.real_out_file3)
        img_repr = load_img(self.real_out_file1)
        x, y = img_repr.get_size()
        assert x in [14, 15, 16, 17, 18] and y in [7, 8, 9, 10]
        img_repr2 = load_img(self.real_out_file2)
        x, y = img_repr2.get_size()
        assert x in [14, 15, 16, 17, 18] and y in [7, 8, 9, 10]
        img_repr3 = load_img(self.real_out_file3)
        x, y = img_repr3.get_size()
        assert x in [14, 15, 16, 17, 18] and y in [7, 8, 9, 10]
        crop_res, crop_output, crop_percentages = crop

        xress,yress = crop_res[0]
        compare_crop_window(crop_output[0],file_path, xress, yress, crop_percentages[0],resolution)
