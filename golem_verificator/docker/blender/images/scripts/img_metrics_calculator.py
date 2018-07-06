import os
import sys
import pickle

import numpy as np
import OpenEXR
from PIL import Image

from . import decision_tree
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

    cropped_img, scene_crops, rendered_scene = \
        _load_and_prepare_img_for_comparison(
            cropped_img_path,
            rendered_scene_path,
            xres, yres)

    path_to_metrics = ImgMetrics(img_metrics).write_to_file(output_filename_path)

    best_crop = None
    best_imag_metrics = None
    for crop in scene_crops:
        try:
            img_metrics = compare_images(cropped_img, crop)
            label = classify_with_tree(img_metrics)
            img_metrics['Label'] = label
        except Exception as e:
            print("There were error %r" % e, file=sys.stderr)
        if img_metrics['Label'] == "TRUE":
            best_imag_metrics = img_metrics
            best_crop = crop
            break

    cv2.imwrite('scene_crop.png', best_crop,(cv2.IMWRITE_PNG_COMPRESSION, 0))

    path_to_metrics = best_imag_metrics.write_to_file(output_filename_path)

    return path_to_metrics

def classify_with_tree(metrics):
    classifier = decision_tree.DecisionTree.load(
        '/golem/scripts/tree_first.pkl')
    
    feature_labels = ImgMetrics.get_feature_labels()

    classifier.set_features_labels(feature_labels)

    features = dict()
    for label in feature_labels:
        features[label] = metrics[label]

    results = classifier.classify_with_feature_vector(features, feature_labels)

    return results[0].decode('utf-8')

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
    (crop_width, crop_height) = cropped_img.size

    crops = get_crops(rendered_scene, xres, yres, crop_width, crop_height)

    return cropped_img, crops, rendered_scene


def get_crops(input, x, y, width, height):
    crops = []

    scene_crop = input[
                 y:y + height,
                 x:x + width]

    crops.append(scene_crop)

    scene_crop_left = input[
                      y:y + height,
                      x - 1:x + width - 1]

    crops.append(scene_crop_left)

    scene_crop_left_up = input[
                         y - 1:y + height - 1,
                         x - 1:x + width - 1]

    crops.append(scene_crop_left_up)

    scene_crop_up = input[
                    y - 1:y + height - 1,
                    x:x + width]

    crops.append(scene_crop_up)

    scene_crop_up_right = input[
                          y - 1:y + height - 1,
                          x + 1:x + width + 1]

    crops.append(scene_crop_up_right)

    scene_crop_right = input[
                       y:y + height,
                       x + 1:x + width + 1]

    crops.append(scene_crop_right)

    scene_crop_down_right = input[
                            y + 1:y + height + 1,
                            x + 1:x + width + 1]

    crops.append(scene_crop_down_right)

    scene_crop_down = input[
                      y + 1:y + height + 1,
                      x:x + width]

    crops.append(scene_crop_down)

    scene_crop_down_left = input[
                           y + 1:y + height + 1,
                           x - 1:x + width - 1]

    crops.append(scene_crop_down_left)

    return crops

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
        result = metric_class.compute_metrics(image_a, image_b)
        for key, value in result.items():
            data[key] = value

    return data
