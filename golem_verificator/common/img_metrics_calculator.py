import cv2
import pywt
import numpy as np
import OpenEXR
import os,sys
from skimage.measure import compare_ssim as ssim


from golem_verificator.common.imgmetrics import ImgMetrics

from golem_verificator.common.img_format_converter import \
    ConvertTGAToPNG, ConvertEXRToPNG


def compare_crop_window(cropped_img_path,
                        rendered_scene_path,
                        xres, yres):

    cropped_img, scene_crop = \
        _load_and_prepare_img_for_comparison(
                cropped_img_path,
                rendered_scene_path,
                xres, yres)

    img_metrics = compare_images(cropped_img, scene_crop)
    path_to_metrics = img_metrics.write_to_file('metrics.txt')

    return path_to_metrics


def _load_and_prepare_img_for_comparison(cropped_img_path,
                                         rendered_scene_path,
                                         xres, yres):

    cropped_img = cv2.imread(cropped_img_path)

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

    (crop_height, crop_width) = cropped_img.shape[:2]
    print("crop hight and width:", crop_height, crop_width)
    scene_crop = rendered_scene[yres:yres + crop_height, xres:xres + crop_width]
    print(xres, xres + crop_width, yres, yres + crop_height)

    return cropped_img, scene_crop

def compare_images(imageA, imageB) -> ImgMetrics:
    """imageA/B are images read by: cv2.imread(img.png)"""
    (crop_height, crop_width) = imageA.shape[:2]
    crop_resolution = str(crop_height) + "x" + str(crop_width)

    imageA_canny = cv2.Canny(imageA, 0, 0)
    imageB_canny = cv2.Canny(imageB, 0, 0)

    imageA_wavelet, imageB_wavelet = images_to_wavelet_transform(
        imageA, imageB, mode='db1')

    imgCorr = compare_histograms(imageA, imageB)
    SSIM_normal, MSE_normal = compare_mse_ssim(imageA, imageB)

    SSIM_canny, MSE_canny = compare_images_transformed(
        imageA_canny, imageB_canny)

    SSIM_wavelet, MSE_wavelet = compare_images_transformed(
        imageA_wavelet, imageB_wavelet)

    data = {
        "imgCorr": imgCorr,
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


# converting crop windows to histogram transfrom
def compare_histograms(imageA, imageB):
    color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    hist_item = 0
    hist_item1 = 0
    for ch, col in enumerate(color):
        hist_item = cv2.calcHist([imageA], [ch], None, [256], [0, 255])
        hist_item1 = cv2.calcHist([imageB], [ch], None, [256], [0, 255])
        cv2.normalize(hist_item, hist_item, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(hist_item1, hist_item1, 0, 255, cv2.NORM_MINMAX)
    result = cv2.compareHist(hist_item, hist_item1, cv2.HISTCMP_CORREL)
    return result


# MSE metric
def mean_squared_error(imageA, imageB):
    mse = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    mse /= float(imageA.shape[0] * imageA.shape[1])
    return mse


# MSE and SSIM metric for crop windows without any transform
def compare_mse_ssim(imageA, imageB):
    structualSimilarity = 0
    meanSquaredError = mean_squared_error(
        cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY))

    structualSim = ssim(
        cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY))

    return structualSim, meanSquaredError


# MSE and SSIM metric from crop windows with transform
def compare_images_transformed(imageA, imageB):
    meanSquaredError = mean_squared_error(imageA, imageB)
    structualSim = ssim(imageA, imageB)

    return structualSim, meanSquaredError


# converting crop windows to wavelet transform
def images_to_wavelet_transform(imageA, imageB, mode='db1'):
    imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    imageB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    imageA = np.float32(imageA)
    imageB = np.float32(imageB)
    imageA /= 255
    imageB /= 255
    coeffs = pywt.dwt2(imageA, mode)
    coeffs2 = pywt.dwt2(imageB, mode)
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
