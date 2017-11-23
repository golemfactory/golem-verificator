import os
import pandas as pd
import datetime
import cv2

# saving result to log file
def save_result(args, result, resolution, number_of_crop, crop_res, test_value,
                crop_window_size, crop_percentages, crop_output,
                list_of_measurements, averages, pass_tests, dir_path):

    log_folder = "log"
    filepath = os.path.join(dir_path, log_folder, 'log.txt')
    log_folder = os.path.join(dir_path, log_folder)
    # if not exist create new
    if not os.path.isfile(filepath):
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        new = open(filepath, 'w+')
        new.close()
    # open and write infromations about tests

    with open(filepath, 'a') as log:
        now = datetime.datetime.now()
        log.write('\n' + '-' * 95)
        log.write("\n" + now.strftime("%Y-%m-%d %H:%M"))
        log.write('\nBlend file: ' + str(
            args.scene_file) + "\nscene resolution: xres: " + str(
            resolution[0]) + " yres: " + str(
            resolution[1]) + "  number_of_crop: " + str(number_of_crop))
        log.write('   number_of_test: ' + str(test_value))
        log.write("\nscene_crop: x_min: " + str(
            crop_window_size[0]) + " x_max: " + str(
            crop_window_size[1]) + " y_min: " + str(
            crop_window_size[2]) + " y_max: " + str(crop_window_size[3]))
        number_crop = 0
        for crop in crop_percentages:
            crop_file = cv2.imread(crop_output[number_crop])
            height, width = crop_file.shape[:2]
            log.write(
                "\n\ncrop_window " + str(number_crop + 1) + ": x_min: " + str(
                    crop[0]) + " x_max: " + str(crop[1]) + " y_min: " + str(
                    crop[2]) + " y_max: " + str(crop[3]))
            log.write("\n" + " " * 15 + "x_min: " + str(
                crop_res[number_crop][0]) + " x_max: " + str(
                crop_res[number_crop][0] + width) + " y_min: " + str(
                crop_res[number_crop][1]) + " y_max: " + str(
                crop_res[number_crop][1] + height))
            log.write(
                "\n" + " " * 15 + "width: " + str(width) + " height: " + str(
                    height))
            log.write("\n" + " " * 8 + "result: CORR: " + str(
                list_of_measurements[number_crop][0]) + " SSIM: " + str(
                list_of_measurements[number_crop][1]) + " MSE: " + str(
                list_of_measurements[number_crop][2]) + " CANNY: " +
                      str(list_of_measurements[number_crop][
                              3]) + " SSIM_wavelet: " + str(
                list_of_measurements[number_crop][4]) + " MSE_wavelet: " + str(
                list_of_measurements[number_crop][5]))
            number_crop += 1
        log.write("\n\nAVERAGES: CORR: " + str(averages[0]) + " SSIM: " + str(
            averages[1]) + " MSE: " + str(averages[2]) +
                  " SSIM_CANNY: " + str(averages[3]) + " SSIM_WAVELET: " + str(
            averages[4]) + " MSE_WAVELET: " + str(averages[5]))
        log.write(
            "\nTest passes: CORR: " + str(pass_tests[0]) + "  SSIM: " + str(
                pass_tests[1]) + "  MSE: " + str(pass_tests[2]))
        log.write("\n\nResult: " + str(result))
        log.close()


# saving testing data to .xlsl file
def save_testdata_to_file(lp, cord, ssim, corr, mse, ssim_canny, mse_canny,
                          mse_wavelet, ssim_wavelet, resolution, name):
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
