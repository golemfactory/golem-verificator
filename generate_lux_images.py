import argparse
import sys

from lux.gen_file import generate_luximage, generate_img_with_params


def gen_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("scene_file", help="path to lux render scene (.lxs)")
    parser.add_argument('--output', help="absolute path to output image")
    parser.add_argument('--xres', help="number of pixels in the xdirection",
                        type=int)
    parser.add_argument('--yres', help="number of pixel in the ydirection",
                        type=int)
    parser.add_argument('--haltspp', help="samples per pixel", type=int)
    parser.add_argument('--crop', help="list(float(4)) render region that "
                                       "range from min (0) to max (1) "
                                       "in order xmin, xmax, ymin,ymax. (0,0) "
                                       "is top left."
                                       " Values should be separated "
                                       "only by a comma, eg. 0.1,0.2,0.1,0.2")
    parser.add_argument('--writeinterval', help="interval in seconds between"
                                                "image writes", type=int)
    parser.add_argument('--output_format', help="output image extension, "
                                                "eg. 'png'")

    return parser


def main():
    parser = gen_parser()
    args = parser.parse_args()
    kwargs = {}
    if args.xres:
        kwargs['xres'] = args.xres
    if args.yres:
        kwargs['yres'] = args.yres
    if args.haltspp:
        kwargs['haltspp'] = args.haltspp
    if args.crop:
        try:
            kwargs['crop'] = [float(v) for v in args.crop.split(",")]
            assert len(kwargs['crop']) == 4
        except (ValueError, IndexError, AssertionError):
            print("Crop values should be represented as four floats "
                  "separeted by comma, eg. 0.1,0.2,0.0,0.1")
            sys.exit(-1)
    if args.writeinterval:
        kwargs['writeinterval'] = args.writeinterval
    if args.output_format:
        kwargs['output_format'] = args.output_format
    if len(kwargs) > 0:
        generate_img_with_params(args.scene_file, output=args.output, **kwargs)
    else:
        generate_luximage(args.scene_file, args.output)

main()
