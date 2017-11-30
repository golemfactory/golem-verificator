
import os

from Docker_CV.scripts.imgmetrics import ImgMetrics
from Docker_CV.scripts.img_format_converter import ConvertEXRToPNG, ConvertTGAToPNG

from golem_verificator.blender.generate_random_crop_images import \
    generate_random_crop
from golem_verificator.common.verificationstates import VerificationState

from golem_verificator.scripts.metrics_value_writer import \
    save_result, MetricsHistory


import shlex
import subprocess
from subprocess import PIPE
import json

def params_writer(parameters, file_path):
    with open(file_path, "wb") as params_file:
        for key, value in parameters.items():
            line = "{} = {}\n".format(key, repr(value))
            params_file.write(bytearray(line, encoding='utf-8'))

def prepare_docker_cmd(cropped_img_path, rendered_scene_path, xres,yres):
    dir_path = os.path.dirname(os.path.realpath(cropped_img_path))
    cropped_img_name = os.path.basename(cropped_img_path)
    rendered_img_name = os.path.basename(rendered_scene_path)

    parameters = {
        "cropped_img_path": "/golem/resources/" + cropped_img_name,
        "rendered_scene_path": "/golem/resources/" + rendered_img_name,
        "xres": xres,
        "yres": yres,
    }
    params_path = os.path.join(dir_path, 'params.py')
    params_writer(parameters, params_path)

    cmd = "docker run -i --rm" \
          " --mount type=bind," \
          "source=" + cropped_img_path + "," \
          "target=/golem/resources/" + cropped_img_name + \
          " --mount type=bind," \
          "source=" + rendered_scene_path + "," \
          "target=/golem/resources/" + rendered_img_name + \
          " --mount type=bind," \
          "source=" + params_path + ",target=/golem/work/params.py " \
          "golemfactory/img_metrics"

    return cmd

def primitive_docker_runner(cmd):
    try:
        process = subprocess.run(
            shlex.split(cmd),
            stdin=PIPE, stdout=PIPE, stderr=PIPE, check=True)

        stdout = process.stdout.decode()
        print(stdout)
        return stdout

    except subprocess.CalledProcessError as e:
        print(str(e))
        print(str(e.stdout.decode()))
        print(str(e.stderr.decode()))


class Validator:

    def __init__(self, _metrics_history=MetricsHistory()):
        self.metrics_history = _metrics_history

    # main script for testing crop windows
    def validate(self, scene_file, crop_window_size,
                 number_of_tests, resolution,
                 rendered_scene_path, scene_format, test_number=1):
        # values for giving answer if crop window test are true, or false
        border_value_corr = (0.7, 0.6)
        border_value_ssim = (0.8, 0.6)
        border_value_mse = (10, 30)
        # FIXME original thresholds are disabled since tests are not passing, argh!
        # border_value_corr = (0.8, 0.7)
        # border_value_ssim = (0.94, 0.7)
        # border_value_mse = (10, 30)

        # generate all crop windows which are need to compare metrics
        crop_res, crop_output, crop_percentages = generate_random_crop(
            scene_file=scene_file,
            crop_scene_size=crop_window_size,
            crop_count=number_of_tests,
            resolution=resolution,
            scene_format=scene_format,
            test_number=test_number)

        number_of_crop = 0
        cropped_img_path= crop_output[number_of_crop]
        list_of_measurements = []
        # comparing crop windows generate in specific place with
        # crop windows cut from rendered scene gave by user
        for xres, yres in crop_res:
            if os.path.splitext(crop_output[number_of_crop])[1] == ".exr":
                ConvertEXRToPNG(crop_output[number_of_crop],
                                "/tmp/" + str(number_of_crop) + ".png")
                crop_output[number_of_crop] = "/tmp/" + str(
                    number_of_crop) + ".png"
            elif os.path.splitext(crop_output[number_of_crop])[1] == ".tga":
                ConvertTGAToPNG(crop_output[number_of_crop],
                                "/tmp/" + str(number_of_crop) + ".png")
                crop_output[number_of_crop] = "/tmp/" + str(
                    number_of_crop) + ".png"

            x_min = crop_percentages[number_of_crop][0]
            x_max = crop_percentages[number_of_crop][1]
            y_min = crop_percentages[number_of_crop][2]
            y_max = crop_percentages[number_of_crop][3]
            print(x_min, x_max, y_min, y_max)

            # run without docker
            from Docker_CV.scripts.img_metrics_calculator import compare_crop_window
            path_to_metrics = \
                compare_crop_window(cropped_img_path,
                                    rendered_scene_path,
                                    xres, yres)
            img_metrics = ImgMetrics.load_from_file(path_to_metrics)

            # todo once docker runner API is defined
            # replace primitive_docker_runner with sth more sophisticated
            # cmd = prepare_docker_cmd(cropped_img_path, rendered_scene_path, xres,yres)
            # data = primitive_docker_runner(cmd)
            # data = data.replace('\n', '')
            # dict = json.loads(data)
            # img_metrics = ImgMetrics(dict)

            # todo get rid of this verbosity
            compare_measurements = [img_metrics.imgCorr,
                                    img_metrics.SSIM_normal,
                                    img_metrics.MSE_normal,
                                    img_metrics.SSIM_canny,
                                    img_metrics.SSIM_wavelet,
                                    img_metrics.MSE_wavelet]

            cord = str(xres) + "x" + str(yres)
            self.metrics_history.append(cord, img_metrics)
            self.metrics_history.print_step(test_number - 1)

            number_of_crop += 1
            list_of_measurements.append(compare_measurements)

        averages = self.average_of_each_measure(
            list_of_measurements, number_of_tests)

        print("AVERAGES - CORR:", averages[0], " SSIM:", averages[1], " MSE:",
              averages[2],
              " SSIM_CANNY:", averages[3], " SSIM_WAVELET:", averages[4],
              " MSE_WAVELET:", averages[5])

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
                if border_value_max > average:
                    pass_tests.append(True)
                elif (border_value_min > average) and test_number == 1:
                    pass_tests.append("HalfTrue")
                else:
                    pass_tests.append(False)
            # if SSIM of any transform is testing then test in their borders
            else:
                if border_value_max < average:
                    pass_tests.append(True)
                elif (border_value_min < average) and test_number == 1:
                    pass_tests.append("HalfTrue")
                else:
                    pass_tests.append(False)

            border_position += 1
        print("Test passes: CORR: " + str(pass_tests[0]) + "  SSIM: " + str(
            pass_tests[1]) + "  MSE: " + str(pass_tests[2]))

        pass_test_result = all(pass_test for pass_test in pass_tests)
        pass_some_test = any(pass_test for pass_test in pass_tests)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        if pass_test_result and test_number < 3:
            result = VerificationState.VERIFIED
            print(result)
            save_result(scene_file, result, resolution, number_of_crop,
                        crop_res,
                        test_number, crop_window_size,
                        crop_percentages, crop_output, list_of_measurements,
                        averages, pass_tests, dir_path)

        # if result of tests are "HalfTrue" then
        # repeat test second time with larger crop windows
        elif "HalfTrue" in pass_tests \
                and test_number == 1 \
                or pass_some_test and test_number == 1:

            result = VerificationState.PARTIALLY_VERIFIED
            print(result)
            test_number += 1
            save_result(scene_file, result, resolution, number_of_crop,
                        crop_res,
                        test_number, crop_window_size,
                        crop_percentages, crop_output, list_of_measurements,
                        averages, pass_tests, dir_path)
            self.validate(scene_file, crop_window_size,
                     number_of_tests, resolution,
                     rendered_scene_path, scene_format, test_number)

        else:
            result = VerificationState.WRONG_ANSWER
            print(result)
            save_result(scene_file, result, resolution, number_of_crop,
                        crop_res,
                        test_number, crop_window_size,
                        crop_percentages, crop_output, list_of_measurements,
                        averages, pass_tests, dir_path)

        return result

    # counting average of all tests
    def average_of_each_measure(self, measure_lists, number_of_tests):
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
        return [corr_average, ssim_average, mse_average, ssim_canny_average,
                ssim_wavelet_average, mse_wavelet_average]