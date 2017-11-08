import os
import random
import math
import numpy as np
from blender.gen_file import generate_img_with_params

def generate_random_crop(scene_file, crop_scene_size, crop_count, resolution, rendered_scene, scene_format,test_number):
    # Get resolution from rendered scene
    # Get border limits from crop_scene_size
    resolution_y, resolution_x = rendered_scene.shape[:2]
    whole_scene_resolution_x, whole_scene_resolution_y = resolution
    crop_scene_xmin, crop_scene_xmax, crop_scene_ymin, crop_scene_ymax = crop_scene_size
    crop_size_x = 0
    crop_size_y = 0
    # check resolution, make sure that cropp is greather then 8px.
    while(crop_size_x * whole_scene_resolution_x < 8):
        crop_size_x += 0.01
    while(crop_size_y * whole_scene_resolution_y < 8):
        crop_size_y += 0.01
    blender_crops = []
    blender_crops_pixel = []

    # second test, with larger crop window
    if test_number == 2:
        crop_size_x += 0.01
        crop_size_y += 0.01


    # Randomisation cX and Y coordinate to render crop window
    # Blender cropping window from bottom left. Cropped window pixels 0,0 are in top left
    for crop in range(crop_count):
        x_difference = round((crop_scene_xmax - crop_size_x)*100, 2)
        x_min = random.randint(crop_scene_xmin * 100, x_difference) / 100
        x_max = round(x_min + crop_size_x, 2)
        y_difference = round((crop_scene_ymax - crop_size_y)*100, 2)
        y_min = random.randint(crop_scene_ymin * 100, y_difference) / 100
        y_max = round(y_min + crop_size_y, 2)
        blender_crop = x_min, x_max, y_min, y_max
        blender_crops.append(blender_crop)
        x_pixel_min = math.floor(np.float32(whole_scene_resolution_x) * np.float32(x_min))
        y_pixel_max = math.floor(np.float32(whole_scene_resolution_y) * np.float32(y_max))
        x_pixel_min = x_pixel_min - math.floor(np.float32(crop_scene_xmin) * np.float32(whole_scene_resolution_x))
        y_pixel_min = math.floor(np.float32(crop_scene_ymax) * np.float32(whole_scene_resolution_y)) - y_pixel_max
        crop_pixel = x_pixel_min, y_pixel_min
        blender_crops_pixel.append(crop_pixel)
        print(str(crop+1)+'.', x_min, x_max, y_min, y_max, x_pixel_min, y_pixel_min)

    blender_crops_path = []
    crop_count = 1
    # Rendering crop windows with all parametrs
    for blender_crop in blender_crops:
        output = "/tmp/" + str(crop_count)
        generate_img_with_params(
            scene_file=scene_file,
            xres=whole_scene_resolution_x,
            yres=whole_scene_resolution_y,
            crop=blender_crop,
            output=output
        )

        output += "0001" + str(scene_format)
        if not os.path.isfile(output):
            raise ValueError('Scene to compare have diffrent format then in .blend file!')
        blender_crops_path.append(output)
        crop_count += 1
    print("xress: " + str(whole_scene_resolution_x) + " yress: " + str(whole_scene_resolution_y) +
        " crop_size_x: " + str(crop_size_x) + ' crop_size_y ' + str(crop_size_y))
    return blender_crops_pixel, blender_crops_path, blender_crops
