import cv2
import numpy as np
from skimage.measure import compare_ssim as ssim

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
def compare_images(imageA, imageB):
    structualSimilarity = 0
    meanSquaredError = mean_squared_error(cv2.cvtColor(
        imageA, cv2.COLOR_BGR2GRAY), cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY))
    structualSim = ssim(cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY),
                        cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY))
    return structualSim, meanSquaredError


# MSE and SSIM metric from crop windows with transform
def compare_images_transformed(imageA, imageB):
    meanSquaredError = mean_squared_error(imageA, imageB)
    structualSim = ssim(imageA, imageB)
    return structualSim, meanSquaredError