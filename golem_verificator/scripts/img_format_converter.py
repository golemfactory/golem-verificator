import cv2
import numpy as np
import pandas as pd
import pywt
from PIL import Image
import OpenEXR

import Imath

# converting .exr file to .png if user gave .exr file as a rendered scene
def ConvertEXRToPNG(exrfile, pngfile):
    File = OpenEXR.InputFile(exrfile)
    PixType = Imath.PixelType(Imath.PixelType.FLOAT)
    DW = File.header()['dataWindow']
    Size = (DW.max.x - DW.min.x + 1, DW.max.y - DW.min.y + 1)
    rgb = [np.frombuffer(File.channel(c, PixType), dtype=np.float32) for c in
           'RGB']
    for i in range(3):
        rgb[i] = np.where(rgb[i] <= 0.0031308,
                          (rgb[i] * 12.92) * 255.0,
                          (1.055 * (rgb[i] ** (1.0 / 2.4)) - 0.055) * 255.0)
    rgb8 = [Image.frombytes("F", Size, c.tostring()).convert("L") for c in rgb]
    Image.merge("RGB", rgb8).save(pngfile, "PNG")

# converting .tga file to .png if user gave .tga file as a rendered scene
def ConvertTGAToPNG(tgafile, pngfile):
    img = Image.open(tgafile)
    img.save(pngfile)

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
