import cv2
import numpy as np
from skimage.measure import compare_ssim as ssim




# def compare_images(imageA_path, imageB_path):
#     cropped_img = cv2.imread(path_to_cropped_img)
#     (crop_height, crop_width) = cropped_img.shape[:2]
#
#     print("crop hight and width:", crop_height, crop_width)
#     scene_crop = scene[yres:yres + crop_height, xres:xres + crop_width]
#     print(xres, xres + crop_width, yres, yres + crop_height)
#
#
#     crop_canny = cv2.Canny(cropped_img, 0, 0)
#     scene_crop_canny = cv2.Canny(scene_crop, 0, 0)
#
#     crop_wavelet, scene_wavelet = images_to_wavelet_transform(
#         cropped_img, scene_crop, mode='db1')
#
#     # GG todo: move this to cv_docker
#     imgCorr = compare_histograms(cropped_img, scene_crop)
#     SSIM_normal, MSE_normal = compare_mse_ssim(cropped_img, scene_crop)
#
#     SSIM_canny, MSE_canny = compare_images_transformed(
#         crop_canny, scene_crop_canny)
#
#     SSIM_wavelet, MSE_wavelet = compare_images_transformed(
#         crop_wavelet, scene_wavelet)
#
#     return imgCorr, SSIM_normal, MSE_normal, SSIM_canny, MSE_canny, \
#            SSIM_wavelet, MSE_wavelet

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