#!/usr/bin/env python


import argparse
import sys

from blender.gen_file import generate_blenderimage, generate_img_with_params


def gen_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("scene_file", help="path to blender scene(.blend)")
    parser.add_argument('--output', help="absolute path to output image")
    parser.add_argument('--xres', help="number of pixels in the xdirection",
                        type=int)
    parser.add_argument('--yres', help="number of pixel in the ydirection",
                        type=int)
    parser.add_argument('--crop', help="render region that "
                                       "range from min (0) to max (1) "
                                       "in order xmin, xmax, ymin,ymax. (0,0) "
                                       "is top left." 
                                        " Values should be separated "
                                       "only by a comma, eg. 0.1,0.2,0.1,0.2")
    parser.add_argument('--frame', help="number of frame that should be "
                                        "rendered", type=int)
    parser.add_argument('--use_compositing', help="information if "
                                                  "postprocessing should "
                                                  "be run",
                        type=bool)

    return parser


def main():
    parser = gen_parser()
    args = parser.parse_args()
    kwargs = {}
    if args.xres:
        kwargs['xres'] = args.xres
    if args.yres:
        kwargs['yres'] = args.yres
    if args.crop:
        try:
            kwargs['crop'] = [float(v) for v in args.crop.split(",")]
            assert len(kwargs['crop']) == 4
        except (ValueError, IndexError, AssertionError):
            print("Crop values should be represented as four floats "
                  "separeted by comma, eg. 0.1,0.2,0.0,0.1")
            sys.exit(-1)
    if args.frame:
        kwargs['frame'] = args.frame
    if args.use_compositing:
        kwargs['use_compositing'] = args.use_compositing
    if len(kwargs) > 0:
        generate_img_with_params(args.scene_file, output=args.output, **kwargs)
    else:
        generate_blenderimage(args.scene_file, args.output)

main()
