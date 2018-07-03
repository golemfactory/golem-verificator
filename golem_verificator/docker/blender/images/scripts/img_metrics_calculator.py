import OpenEXR
import os
import sys

from PIL import Image

from .img_format_converter import \
    ConvertTGAToPNG, ConvertEXRToPNG
from .imgmetrics import \
    ImgMetrics


def compare_crop_window(cropped_img_path,
                        rendered_scene_path,
                        xres, yres,
                        output_filename_path='metrics.txt'):
    """
    This is the entry point for calculation of metrics between the
    rendered_scene and the sample(cropped_img) generated for comparison.
    :param cropped_img_path:
    :param rendered_scene_path:
    :param xres: to match where the cropped_img is located comparing to the
    rendered_scene(full img)
    :param yres: as above
    :param output_filename_path:
    :return:
    """

    cropped_img, scene_crop = \
        _load_and_prepare_img_for_comparison(
            cropped_img_path,
            rendered_scene_path,
            xres, yres)

    img_metrics = compare_images(cropped_img, scene_crop)

    label = classify(img_metrics)

    img_metrics['Label'] = label

    path_to_metrics = ImgMetrics(img_metrics).write_to_file(output_filename_path)

    return path_to_metrics

def classify(metrics):
    # These are empirically measured, render on different machines can
    # cause single pixels to change its intensity and cause deviation.
    # We observe that in majority cases 0.990 is enough to count for this
    # deviation, but there are exceptions, scenes like BMW which deviates
    # more drops to 0.970.
    w_ssim = 0.920
    w_ssim_min = 0.900

    print("SSIM has %r" % metrics['SSIM_normal'])

    if metrics['SSIM_normal'] > w_ssim_min and \
        metrics['SSIM_normal'] < w_ssim:
        return "DONT_KNOW"
    elif metrics['SSIM_normal'] >= w_ssim:
        return "TRUE"
    else:
        return "FALSE"


def _load_and_prepare_img_for_comparison(cropped_img_path,
                                         rendered_scene_path,
                                         xres, yres):

    """
    This function prepares (i.e. crops) the rendered_scene so that it will
    fit the sample(cropped_img) generated for comparison.

    :param cropped_img_path:
    :param rendered_scene_path:
    :param xres: to match where the cropped_img is located comparing to the
    rendered_scene(full img)
    :param yres: as above
    :return:
    """
    rendered_scene = None
    # if rendered scene has .exr format need to convert it for .png format
    if os.path.splitext(rendered_scene_path)[1] == ".exr":
        check_input = OpenEXR.InputFile(rendered_scene_path).header()[
            'channels']
        if 'RenderLayer.Combined.R' in check_input:
            sys.exit("There is no support for OpenEXR multilayer")
        file_name = "/tmp/scene.png"
        ConvertEXRToPNG(rendered_scene_path, file_name)
        rendered_scene = Image.open(file_name)
    elif os.path.splitext(rendered_scene_path)[1] == ".tga":
        file_name = "/tmp/scene.png"
        ConvertTGAToPNG(rendered_scene_path, file_name)
        rendered_scene = Image.open(file_name)
    else:
        rendered_scene = Image.open(rendered_scene_path)

    cropped_img = Image.open(cropped_img_path)
    (crop_height, crop_width) = cropped_img.size

    scene_crop = rendered_scene.crop((xres, yres, xres + crop_width, yres + crop_height))

    scene_crop.save('scene_crop.png')

    return cropped_img, scene_crop


def compare_images(image_a, image_b) -> ImgMetrics:
    """
    This the entry point for calculating metrics between image_a, image_b
    once they are cropped to the same size.
    :param image_a:
    :param image_b:
    :return: ImgMetrics
    """

    """imageA/B are images read by: PIL.Image.open(img.png)"""
    (crop_height, crop_width) = image_a.size
    crop_resolution = str(crop_height) + "x" + str(crop_width)

    data = {"crop_resolution": crop_resolution}

    for metric_class in ImgMetrics.get_metric_classes():
        data = {**data, **metric_class.compute_metrics(image_a, image_b)}


    return ImgMetrics(data)
