#!/usr/bin/env python3

import argparse
import os
import sys
from argparse import RawTextHelpFormatter
from golem_verificator.blender.validator import Validator as BlenderValidator
from golem_verificator.common.verificationstates import SubtaskVerificationState

# parser to get parameters for correct script work
def create_parser():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("scene_file", help="path to blender scene (.blend)")
    parser.add_argument("--crop_window_size", help="region of rendered window\n"
                                                   "range from 0-1\n"
                                                   "in order xmin, xmax, ymin, ymax\n"
                                                   "example: 0.1,0.2,0.3,0.4\n")
    parser.add_argument("--resolution", help="resolution of whole image\n"
                                             "in order xress, yress\n"
                                             "example: 1920,1080")
    parser.add_argument("--rendered_scene", help="path to comparison scene")
    parser.add_argument("--name_of_excel_file")
    return parser

def validate_parser_input(parser: argparse.ArgumentParser):
    args = parser.parse_args()
    blend_file = ".blend"
    # checking if what ugenerate_random_cropser gave .blend file as a parameter
    if (args.scene_file[-6:] != blend_file):
        sys.exit("No such file or wrong directory to .blender file!")
    # spliting all float numbers to get crop window size parametrs
    # checking if what user gave as parameters is correct
    crop_window_size = [float(x) for x in args.crop_window_size.split(",")]
    if (len(crop_window_size) == 4):
        for crop_window_number in crop_window_size:
            if (crop_window_number > 1 or crop_window_number < 0):
                sys.exit("Wrong cropwindow size. Try example: 0.1,0.2,0.3,0.4")
    else:
        sys.exit("Too much, or too less arguments in cropwindow size."
                 " Try example: 0.1,0.2,0.3,0.4")
    number_of_tests = 3
    # spliting resolution parameters in two seperate X and Y
    # checking if what user gave as parameters is correct
    resolution = [int(x) for x in args.resolution.split(",")]
    if (len(resolution) == 2):
        for res in resolution:
            if (res <= 0):
                sys.exit("Size of image can't be 0!")
    # checking if what user gave as rendered scene has correct format
    format_file = [".png", ".jpg", ".bmp", ".jp2", ".tif,", ".exr", ".tga"]
    scene_format = os.path.splitext(args.rendered_scene)[1]
    if scene_format not in format_file:
        sys.exit("No such file or wrong format of scene")

    rendered_scene_path = args.rendered_scene
    if not os.path.isfile(rendered_scene_path):
        sys.exit("Cannot find rendered_scene file")

    return args.scene_file, crop_window_size, number_of_tests, resolution, rendered_scene_path, scene_format


if __name__ == "__main__":

    parser = create_parser()
    scene_file, crop_window_size, number_of_tests, \
        resolution, rendered_scene_path, scene_format \
             = validate_parser_input(parser)

    blender_validator = BlenderValidator()
    result = blender_validator.validate(
        scene_file, crop_window_size, number_of_tests,
                resolution, rendered_scene_path, scene_format)

    if result == SubtaskVerificationState.VERIFIED.value:
        sys.exit(0)
    else:
        sys.exit(-1)
