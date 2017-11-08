import os
import subprocess

from .change_scene import generate_blender_crop_file

BLENDER = "blender"


def exec_cmd(cmd):
    pc = subprocess.Popen(cmd)
    return pc.wait()


def generate_blenderimage(scene_file, output=None, script_file=None, frame=1):
    """
    Generate image from Blender scene file (.blend)
    :param string scene_file: path to blender scene file (.blend)
    :param string|None output: path to output image. If set to None than
    default name will be set
    :param string|None script_file|None: add path to blender script that
    defines potential modification of scene
    :param int frame: number of frame that should be render. Default is set to 1
    """
    cmd = [BLENDER, "-b", scene_file, "-y"]
    previous_wd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(scene_file)))
    if script_file:
        cmd.append("-P")
        cmd.append(script_file)
    if output:
        outbase, ext = os.path.splitext(output)
        cmd.append("-o")
        cmd.append(output)
        print(ext)
        print(ext[1:])
        if ext:
            cmd.append("-F")
            cmd.append(ext[1:].upper())
    cmd.append("-noaudio")
    cmd.append("-f")
    cmd.append(str(frame))
    print(cmd)
    exec_cmd(cmd)
    os.chdir(previous_wd)


def generate_img_with_params(scene_file, script_name="tmp.py", xres=800,
                             yres=600, crop=None, use_compositing=False,
                             output=None, frame=1):
    """
    Generate image from blender scene file(.blend) with changed parameters
    :param string scene_file: path to blender scene file (.blend)
    :param string script_name: name of the new script file that will be used
     for scene modification. It should be just name of the file and not path,
     because it will be saved in main scene file directory.
    :param int xres: new resolution in pixels
    :param int yres: new resolution in pixels
    :param list|None crop: values describing render region that range from
    min (0) to max (1) in order xmin, xmax, ymin,ymax. (0,0) is bottom left. If
    is set to None then full window will be rendered
    :param string output: path to final saved image. If this value
    is set to None, then default value will be used.
    """

    if crop is None:
        crop = [0, 1, 0, 1]

    crop_file_src = generate_blender_crop_file([xres, yres], [crop[0], crop[1]],
                                           [crop[2], crop[3]], use_compositing)

    scene_dir = os.path.dirname(os.path.abspath(scene_file))
    new_scriptpath = os.path.join(scene_dir, script_name)

    with open(new_scriptpath, 'w') as f:
        f.write(crop_file_src)

    generate_blenderimage(scene_file, output, new_scriptpath, frame)
