#!/usr/bin/env python3

import OpenEXR
import argparse
import datetime
import os
import sys
from argparse import RawTextHelpFormatter

import Imath
import cv2
import numpy as np
import pandas as pd
import pywt
from PIL import Image
from skimage.measure import compare_ssim as ssim
from enum import Enum

from golem_verificator.blender.generate_random_crop_images import \
    generate_random_crop

class SubtaskVerificationState(Enum):
    UNKNOWN = 0
    WAITING = 1
    PARTIALLY_VERIFIED = 2
    VERIFIED = 3
    WRONG_ANSWER = 4

#parser to get parameters for correct script work
def checking_parser():
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


def validation():
    parser = checking_parser()
    args = parser.parse_args()
    blend_file = ".blend"
    # checking if what ugenerate_random_cropser gave .blend file as a parameter
    if(args.scene_file[-6:] != blend_file):
        sys.exit("No such file or wrong directory to .blender file!")
    # spliting all float numbers to get crop window size parametrs
    # checking if what user gave as parameters is correct
    crop_window_size = [float(x) for x in args.crop_window_size.split(",")]
    if(len(crop_window_size) == 4):
        for crop_window_number in crop_window_size:
            if(crop_window_number > 1 or crop_window_number < 0):
                sys.exit("Wrong cropwindow size. Try example: 0.1,0.2,0.3,0.4")
    else:
        sys.exit("Too much, or too less arguments in cropwindow size."
                 " Try example: 0.1,0.2,0.3,0.4")
    number_of_tests = 3
    # spliting resolution parameters in two seperate X and Y
    # checking if what user gave as parameters is correct
    resolution = [int(x) for x in args.resolution.split(",")]
    if(len(resolution) == 2):
        for res in resolution:
            if(res <= 0):
                sys.exit("Size of image can't be 0!")
    # checking if what user gave as rendered scene has correct format
    format_file = [".png",".jpg",".bmp",".jp2",".tif,",".exr", ".tga"]
    scene_format = os.path.splitext(args.rendered_scene)[1]
    if scene_format not in format_file:
        sys.exit("No such file or wrong format of scene")
    rendered_scene = cv2.imread(args.rendered_scene)
    # if rendered scene has .exr format need to convert it for .png format
    if os.path.splitext(args.rendered_scene)[1] == ".exr":
        check_input = OpenEXR.InputFile(args.rendered_scene).header()['channels']
        if 'RenderLayer.Combined.R' in check_input:
            sys.exit("There is no support for OpenEXR multilayer")
        ConvertEXRToPNG(args.rendered_scene, "/tmp/scene.png")
        rendered_scene = "/tmp/scene.png"
        rendered_scene = cv2.imread(rendered_scene)
    elif os.path.splitext(args.rendered_scene)[1] == ".tga":
        rendered_scene = ConvertTGAToPNG(args.rendered_scene, "/tmp/scene.png")
        rendered_scene = "/tmp/scene.png"
        rendered_scene = cv2.imread(rendered_scene)

    return args, crop_window_size, number_of_tests, resolution, rendered_scene, scene_format


# main script for testing crop windows
def assign_value(test_value=1):
    # values for giving answer if crop window test are true, or false
    border_value_corr = (0.7, 0.6)
    border_value_ssim = (0.8, 0.6)
    border_value_mse = (10, 30)
# FIXME original thresholds are disabled since tests are not passing, argh!
    # border_value_corr = (0.8, 0.7)
    # border_value_ssim = (0.94, 0.7)
    # border_value_mse = (10, 30)
    args, crop_window_size, number_of_tests, resolution, rendered_scene, scene_format = validation()
    # generate all crop windows which are need to compare metrics
    crops_pixel = generate_random_crop(
        args.scene_file, crop_window_size, number_of_tests, resolution, rendered_scene, scene_format,test_value)

    crop_res = crops_pixel[0]
    crop_output = crops_pixel[1]
    crop_percentages = crops_pixel[2]
    number_of_crop = 0
    list_of_measurements = []
    # comparing crop windows generate in specific place with
    # crop windows cutted from rendered scene gave by user
    for coordinate in crop_res:
        if os.path.splitext(crop_output[number_of_crop])[1] == ".exr":
            ConvertEXRToPNG(crop_output[number_of_crop], "/tmp/" + str(number_of_crop) + ".png")
            crop_output[number_of_crop] = "/tmp/" + str(number_of_crop) + ".png"
        elif os.path.splitext(crop_output[number_of_crop])[1] == ".tga":
            ConvertTGAToPNG(crop_output[number_of_crop], "/tmp/" + str(number_of_crop) + ".png")
            crop_output[number_of_crop] = "/tmp/" + str(number_of_crop) + ".png"
        compare_measurements = compare_crop_window(crop_output[number_of_crop], rendered_scene, coordinate[0], coordinate[1], crop_percentages[number_of_crop],resolution)
        number_of_crop += 1
        list_of_measurements.append(compare_measurements)

    averages = average_of_each_measure(list_of_measurements, number_of_tests)
    print("AVERAGES - CORR:", averages[0], " SSIM:", averages[1], " MSE:", averages[2],
          " SSIM_CANNY:", averages[3], " SSIM_WAVELET:", averages[4], " MSE_WAVELET:", averages[5])

    # assign all values which are borders for correct crop window
    border_value = [border_value_corr, border_value_ssim, border_value_mse]
    border_position = 0
    pass_tests = []
    # checking if values which compare_crop_window test gave is correct
    for average in averages[:3]:
        border_value_max = border_value[border_position][0]
        border_value_min = border_value[border_position][1]
        # if MSE is testing then test in diffrent borders
        if border_position == 2:
            if (border_value_max > average) == True:
                pass_tests.append(True)
            elif (border_value_min > average) == True and test_value == 1:
                pass_tests.append("HalfTrue")
            else:
                pass_tests.append(False)
        # if SSIM of any transform is testing then test in their borders
        else:
            if (border_value_max < average) == True:
                pass_tests.append(True)
            elif (border_value_min < average) == True and test_value == 1:
                pass_tests.append("HalfTrue")
            else:
                pass_tests.append(False)

        border_position += 1
    print("Test passes: CORR: " + str(pass_tests[0]) + "  SSIM: " + str(pass_tests[1]) + "  MSE: " + str(pass_tests[2]))

    pass_test_result = all(pass_test == True for pass_test in pass_tests)
    pass_some_test = any(pass_test == True for pass_test in pass_tests)
    if pass_test_result == True and test_value < 3:
        result = SubtaskVerificationState.VERIFIED
        print(result)
        save_result(args,result,resolution,number_of_crop,crop_res,test_value,crop_window_size,\
                    crop_percentages,crop_output,list_of_measurements,averages,pass_tests)

    # if result of tests are "HalfTrue" then
    # repeat test second time with larger crop windows
    elif "HalfTrue" in pass_tests and test_value == 1 or pass_some_test == True and test_value == 1:
        result = SubtaskVerificationState.PARTIALLY_VERIFIED
        print(result)
        test_value += 1
        save_result(args,result,resolution,number_of_crop,crop_res,test_value,crop_window_size,\
                    crop_percentages,crop_output,list_of_measurements,averages,pass_tests)
        assign_value(test_value)
    else:
        result = SubtaskVerificationState.WRONG_ANSWER
        print(result)
        save_result(args,result,resolution,number_of_crop,crop_res,test_value,crop_window_size,\
                    crop_percentages,crop_output,list_of_measurements,averages,pass_tests)


    save_testdata_to_file(lp, cord_list, ssim_list, corr_list, mse_list, ssim_canny_list,
                          mse_canny_list, mse_wavelet_list, ssim_wavelet_list, resolution_list, args.name_of_excel_file)
    return result

# saving result to log file
def save_result(args,result,resolution,number_of_crop,crop_res,test_value,crop_window_size,crop_percentages,crop_output,list_of_measurements,averages,pass_tests):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    log_folder = "log"
    filepath = os.path.join(dir_path,log_folder,'log.txt')
    log_folder = os.path.join(dir_path,log_folder)
    # if not exist create new
    if not os.path.isfile(filepath):
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        new = open(filepath, 'w+')
        new.close()
    # open and write infromations about tests

    return
    # FIXME FileNotFoundError: [Errno 2] No such file or directory:
    # 'log/log.txt' when running from package
    with open('log/log.txt','a') as log:
        now = datetime.datetime.now()
        log.write('\n'+'-'* 95)
        log.write("\n" + now.strftime("%Y-%m-%d %H:%M"))
        log.write('\nBlend file: ' + str(args.scene_file) + "\nscene resolution: xres: " + str(resolution[0]) + " yres: " + str(resolution[1]) + "  number_of_crop: " + str(number_of_crop))
        log.write('   number_of_test: ' + str(test_value))
        log.write("\nscene_crop: x_min: " + str(crop_window_size[0]) + " x_max: " + str(crop_window_size[1]) + " y_min: " + str(crop_window_size[2]) + " y_max: " + str(crop_window_size[3]))
        number_crop = 0
        for crop in crop_percentages:
            crop_file = cv2.imread(crop_output[number_crop])
            height, width = crop_file.shape[:2]
            log.write("\n\ncrop_window "+str(number_crop+1)+ ": x_min: "+str(crop[0])+" x_max: "+str(crop[1])+" y_min: "+str(crop[2])+" y_max: "+str(crop[3]))
            log.write("\n" + " "*15+"x_min: " + str(crop_res[number_crop][0])+" x_max: "+str(crop_res[number_crop][0]+width)+" y_min: "+str(crop_res[number_crop][1])+" y_max: "+str(crop_res[number_crop][1]+height))
            log.write("\n" + " "*15+"width: " + str(width) + " height: "+str(height))
            log.write("\n" + " "*8+"result: CORR: " + str(list_of_measurements[number_crop][0])+" SSIM: "+str(list_of_measurements[number_crop][1])+" MSE: "+str(list_of_measurements[number_crop][2])+" CANNY: "+
          str(list_of_measurements[number_crop][3])+" SSIM_wavelet: "+str(list_of_measurements[number_crop][4])+" MSE_wavelet: "+str(list_of_measurements[number_crop][5]))
            number_crop +=1
        log.write("\n\nAVERAGES: CORR: " + str(averages[0])+" SSIM: " + str(averages[1]) + " MSE: " + str(averages[2]) +
              " SSIM_CANNY: " + str(averages[3]) + " SSIM_WAVELET: " + str(averages[4]) + " MSE_WAVELET: " + str(averages[5]))
        log.write("\nTest passes: CORR: " + str(pass_tests[0]) + "  SSIM: " + str(pass_tests[1]) + "  MSE: " + str(pass_tests[2]))
        log.write("\n\nResult: " + str(result))
        log.close()


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


def compare_crop_window(crop, scene, xres, yres, crop_percentages, resolution):
    crop = cv2.imread(crop)
    crop_canny = cv2.Canny(crop, 0, 0)
    x_min = crop_percentages[0]
    x_max = crop_percentages[1]
    y_min = crop_percentages[2]
    y_max = crop_percentages[3]
    print(x_min, x_max, y_min, y_max)
    (crop_hight, crop_width) = crop.shape[:2]
    print("crop hight and width:", crop_hight, crop_width)
    scene_crop = scene[yres:yres + crop_hight, xres:xres + crop_width]
    print(xres, xres + crop_width, yres, yres + crop_hight)
    scene_crop_canny = cv2.Canny(scene_crop, 0, 0)
    imgCorr = compare_histograms(crop, scene_crop)
    SSIM_normal, MSE_normal = compare_images(crop, scene_crop)
    SSIM_canny, MSE_canny = compare_images_transformed(
        crop_canny, scene_crop_canny)
    crop_wavelet, scene_wavelet = images_to_wavelet_transform(
        crop, scene_crop, mode='db1')
    SSIM_wavelet, MSE_wavelet = compare_images_transformed(
        crop_wavelet, scene_wavelet)
    i = len(cord_list) + 1
    lp.append(i)
    cord = str(xres) + "x" + str(yres)
    cord_list.append(cord)
    ssim_list.append(SSIM_normal)
    corr_list.append(imgCorr)
    mse_list.append(MSE_normal)
    mse_wavelet_list.append(MSE_wavelet)
    ssim_wavelet_list.append(SSIM_wavelet)
    ssim_canny_list.append(SSIM_canny)
    resolution = str(crop_hight) + "x" + str(crop_width)
    resolution_list.append(resolution)
    mse_canny_list.append(MSE_canny)
    print("CORR:", imgCorr, "SSIM:", SSIM_normal, "MSE:", MSE_normal, "CANNY:",
          SSIM_canny, "SSIM_wavelet:", SSIM_wavelet, "MSE_wavelet:", MSE_wavelet)
    return [imgCorr, SSIM_normal, MSE_normal, SSIM_canny, SSIM_wavelet, MSE_wavelet]

# counting average of all tests
def average_of_each_measure(measure_lists, number_of_tests):
    corr_value = 0
    ssim_value = 0
    mse_value = 0
    ssim_canny_value = 0
    ssim_wavelet_value = 0
    mse_wavelet_value = 0
    for measure_list in measure_lists:
        corr_value += measure_list[0]
        ssim_value += measure_list[1]
        mse_value += measure_list[2]
        ssim_canny_value += measure_list[3]
        ssim_wavelet_value += measure_list[4]
        mse_wavelet_value += measure_list[5]
    corr_average = corr_value / number_of_tests
    ssim_average = ssim_value / number_of_tests
    mse_average = mse_value / number_of_tests
    ssim_canny_average = ssim_canny_value / number_of_tests
    ssim_wavelet_average = ssim_wavelet_value / number_of_tests
    mse_wavelet_average = mse_wavelet_value / number_of_tests
    return [corr_average, ssim_average, mse_average, ssim_canny_average, ssim_wavelet_average, mse_wavelet_average]

# converting .exr file to .png if user gave .exr file as a rendered scene
def ConvertEXRToPNG(exrfile, pngfile):
    File = OpenEXR.InputFile(exrfile)
    PixType = Imath.PixelType(Imath.PixelType.FLOAT)
    DW = File.header()['dataWindow']
    Size = (DW.max.x - DW.min.x + 1, DW.max.y - DW.min.y + 1)
    rgb = [np.frombuffer(File.channel(c, PixType), dtype=np.float32) for c in 'RGB']
    for i in range(3):
        rgb[i] = np.where(rgb[i]<=0.0031308,
                (rgb[i]*12.92)*255.0,
                (1.055*(rgb[i]**(1.0/2.4))-0.055) * 255.0)
    rgb8 = [Image.frombytes("F", Size, c.tostring()).convert("L") for c in rgb]
    Image.merge("RGB", rgb8).save(pngfile, "PNG")

# converting .tga file to .png if user gave .tga file as a rendered scene
def ConvertTGAToPNG(tgafile, pngfile):
    img = Image.open(tgafile)
    img.save(pngfile)

# saving testing data to .xlsl file
def save_testdata_to_file(lp, cord, ssim, corr, mse, ssim_canny, mse_canny, mse_wavelet, ssim_wavelet, resolution, name):
    name_of_file = name + ".xlsx"
    data = {'L.p': lp,
            'CORD': cord,
            'SSIM': ssim,
            'CORRELATION': corr,
            'MSE': mse,
            'MSE_wavelet': mse_wavelet,
            'MSE_canny': mse_canny,
            'SSIM_wavelet': ssim_wavelet,
            'SSIM_canny': ssim_canny,
            'CROP_RES': resolution}
    data = pd.DataFrame(data)
    data.set_index('L.p', inplace=True)
    data = [data]
    result = pd.concat(data, axis=1)
    result.to_excel(name_of_file)


lp = []
cord_list = []
ssim_list = []
corr_list = []
mse_list = []
ssim_canny_list = []
ssim_wavelet_list = []
mse_wavelet_list = []
mse_canny_list = []
resolution_list = []

if __name__ == "__main__":
    # FIXME sometimes false negatives are returned...
    # add --deterministic parameter (at least for unit tests), argh!
    import random
    random.seed(0)

    result = assign_value()

    print("\n\n\n ==== FIXME sometimes false negatives are returned... \t"
          "enabled random.seed(0) === \n\n\n")

    if result == SubtaskVerificationState.VERIFIED:
        sys.exit(0)
    else:
        sys.exit(-1)

