import OpenEXR
import os
import sys

import cv2
import numpy as np
import pywt
from skimage.measure import compare_ssim as ssim
from skimage.measure import compare_psnr as psnr

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
    path_to_metrics = img_metrics.write_to_file(output_filename_path)

    return path_to_metrics


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
        rendered_scene = cv2.imread(file_name)
    elif os.path.splitext(rendered_scene_path)[1] == ".tga":
        file_name = "/tmp/scene.png"
        ConvertTGAToPNG(rendered_scene_path, file_name)
        rendered_scene = cv2.imread(file_name)
    else:
        rendered_scene = cv2.imread(rendered_scene_path)

    cropped_img = cv2.imread(cropped_img_path)
    (crop_height, crop_width) = cropped_img.shape[:2]

    scene_crop = rendered_scene[
                 yres:yres + crop_height,
                 xres:xres + crop_width]

    cv2.imwrite('scene_crop.png', scene_crop,(cv2.IMWRITE_PNG_COMPRESSION, 0))

    return cropped_img, scene_crop


def compare_images(image_a, image_b) -> ImgMetrics:
    """
    This the entry point for calculating metrics between image_a, image_b
    once they are cropped to the same size.
    :param image_a:
    :param image_b:
    :return: ImgMetrics
    """

    """imageA/B are images read by: cv2.imread(img.png)"""
    (crop_height, crop_width) = image_a.shape[:2]
    crop_resolution = str(crop_height) + "x" + str(crop_width)

    imageA_canny = cv2.Canny(image_a, 0, 0)
    imageB_canny = cv2.Canny(image_b, 0, 0)

    imageA_wavelet, imageB_wavelet = images_to_wavelet_transform(
        image_a, image_b, mode='db1')

    histograms_correlation = compare_histograms(image_a, image_b)
    SSIM_normal, MSE_normal = compare_mse_ssim(image_a, image_b)

    SSIM_canny, MSE_canny = compare_images_transformed(
        imageA_canny, imageB_canny)

    SSIM_wavelet, MSE_wavelet = compare_images_transformed(
        imageA_wavelet, imageB_wavelet)

    PSNR_value = psnr(image_a, image_b)

    data = {
        "PSNR": PSNR_value,
        "histograms_correlation": histograms_correlation,
        "SSIM_normal": SSIM_normal,
        "MSE_normal": MSE_normal,
        "SSIM_canny": SSIM_canny,
        "MSE_canny": MSE_canny,
        "MSE_wavelet": MSE_wavelet,
        "SSIM_wavelet": SSIM_wavelet,
        "crop_resolution": crop_resolution,
    }

    imgmetrics = ImgMetrics(data)
    return imgmetrics


# comparing histograms
def get_number_of_channels(image):
    if len(image.shape) == 3:
        return image.shape[2]
    else:
        return 2


def get_bit_depth(image):
    dtype = str(image.dtype)
    if "uint" in dtype:
        return int(dtype[4:])
    else:
        raise Exception("Unexpected type found when trying to recognize bit depth")


def get_max_pixel_value_plus_one(image):
    return 2 ** get_bit_depth(image)


def get_number_of_pixels(image):
    height, width = image.shape[:2]
    return height * width


def calculate_normalized_histogram(image):
    # TODO if the crop is really small, number of bins should depend on the number of pixels in the image.
    # 4 is an arbitrary constant and will be replaced with a value determined in research
    number_of_bins = min(get_number_of_pixels(image) // 4, 256)
    channels_number = get_number_of_channels(image)
    histogram = cv2.calcHist([image],
                             range(channels_number),
                             None,
                             [number_of_bins] * channels_number,
                             [0, get_max_pixel_value_plus_one(image)] * channels_number)
    cv2.normalize(histogram, histogram, 0, 256, cv2.NORM_MINMAX)
    return histogram


def compare_histograms(image_a, image_b):
    histogram_a = calculate_normalized_histogram(image_a)
    histogram_b = calculate_normalized_histogram(image_b)
    result = cv2.compareHist(histogram_a, histogram_b, cv2.HISTCMP_CORREL)
    return result


# MSE metric
def mean_squared_error(image_a, image_b):
    mse = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    mse /= float(image_a.shape[0] * image_a.shape[1])
    return mse


# MSE and SSIM metric for crop windows without any transform
def compare_mse_ssim(image_a, image_b):
    meanSquaredError = mean_squared_error(
        cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY))

    structualSim = ssim(
        cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY))

    return structualSim, meanSquaredError

# MSE and SSIM metric from crop windows with transform
def compare_images_transformed(image_a, image_b):
    meanSquaredError = mean_squared_error(image_a, image_b)
    structualSim = ssim(image_a, image_b)

    return structualSim, meanSquaredError


# converting crop windows to wavelet transform
def images_to_wavelet_transform(image_a, image_b, mode='db1'):
    image_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
    image_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
    image_a = np.float32(image_a)
    image_b = np.float32(image_b)
    image_a /= 255
    image_b /= 255
    coeffs = pywt.dwt2(image_a, mode)
    coeffs2 = pywt.dwt2(image_b, mode)
    coeffs_H = list(coeffs)
    coeffs_H2 = list(coeffs2)
    coeffs_H[0] *= 0
    coeffs_H2[0] *= 0
    imArray_H = pywt.idwt2(coeffs_H, mode)
    imArray_H *= 255
    imArray_H = np.uint8(imArray_H)
    imArray_H2 = pywt.idwt2(coeffs_H2, mode)
    imArray_H2 *= 255
    imArray_H2 = np.uint8(imArray_H2)
    return imArray_H, imArray_H2
