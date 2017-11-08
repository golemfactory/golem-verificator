import os
import subprocess

from lux.change_scene import regenerate_lux_file

LUXCMD = 'luxconsole'


def exec_cmd(cmd):
    pc = subprocess.Popen(cmd)
    return pc.wait()


def generate_luximage(scene_file, output=None):
    """
    Generate image from lux scene file (.lxs)
    :param string scene_file: path to lux scene file (.lxs)
    :param string|None output: path to output image. If set to None than
    default name will be set
    """
    cmd = [LUXCMD, scene_file]
    previous_wd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(scene_file)))
    if output:
        cmd.append("-o")
        cmd.append(output)
    exec_cmd(cmd)
    os.chdir(previous_wd)


def generate_img_with_params(scene_file, new_scene_file="tmp.lxs",
                             xres=800, yres=600, haltspp=1, crop=None,
                             writeinterval=60, output_format="png",
                             output=None):
    """
    Generate image from lux scene file (.lxs) with changed parameters
    :param string scene_file: path to lux scene file (.lxs)
    :param string new_scene_file: name of the new scene file (.lxs). It should
    be just name of the file and not path, because it will be saved in main
    scene file directory.
    :param int xres: new resolution in pixels
    :param int yres: new resolution in pixels
    :param int haltspp: how many samples per pixel should be generated
    :param list|None crop: values describing render region that range from
    min (0) to max (1) in order xmin, xmax, ymin,ymax. (0,0) is top left. If
    is set to None then full window will be rendered
    :param int writeinterval: interval in seconds between image writes
    :param string output_format: output image extension
    :param string output: path to final saved image. If this value
    is set to None, then default value will be used.
    """
    if crop is None:
        crop = [0, 1, 0, 1]

    with open(scene_file) as f:
        scene_src = f.read()

    new_scene_src = regenerate_lux_file(scene_src, xres, yres, 0, haltspp,
                                         writeinterval, crop, output_format)

    scene_dir = os.path.dirname(os.path.abspath(scene_file))
    new_scene_path = os.path.join(scene_dir, new_scene_file)
    with open(new_scene_path, 'w') as f:
        f.write(new_scene_src)

    generate_luximage(new_scene_path, output)