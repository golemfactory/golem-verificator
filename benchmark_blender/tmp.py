# This template is rendered by
# apps.blender.resources.scenefileeditor.generate_blender_crop_file(),
# written to tempfile and passed as arg to blender.
import bpy

class EngineWarning(bpy.types.Operator):
    bl_idname = "wm.engine_warning"
    bl_label = "Inform about not supported rendering engine"

    def execute(self, context):
        self.report({"ERROR"}, "Engine " + bpy.context.scene.render.engine + \
                               " not supported by Golem")
        return {"FINISHED"}

class ShowInformation(bpy.types.Operator):
    bl_idname = "wm.scene_information"
    bl_label = "Inform user about scene settings"


    def execute(self, context):
        self.report({"INFO"}, "Resolution: " +
                              str(bpy.context.scene.render.resolution_x) +
                               " x " +
                               str(bpy.context.scene.render.resolution_y))
        self.report({"INFO"}, "File format: " +
                               str(bpy.context.scene.render.file_extension))
        self.report({"INFO"}, "Filepath: " +
                              str(bpy.context.scene.render.filepath))
        self.report({"INFO"}, "Frames: " +
                              str(bpy.context.scene.frame_start) + "-" +
                              str(bpy.context.scene.frame_end) + ";" +
                              str(bpy.context.scene.frame_step))

        return {"FINISHED"}


bpy.utils.register_class(EngineWarning)
engine = bpy.context.scene.render.engine
if engine not in ("BLENDER_RENDER", "CYCLES"):
    bpy.ops.wm.engine_warning()

bpy.utils.register_class(ShowInformation)
bpy.ops.wm.scene_information()



for scene in bpy.data.scenes:

    if scene.render.image_settings.file_format == 'OPEN_EXR_MULTILAYER':
        scene.render.image_settings.file_format = 'OPEN_EXR'
    scene.render.tile_x = 0
    scene.render.tile_y = 0
    scene.render.resolution_x = 150
    scene.render.resolution_y = 150
    scene.render.resolution_percentage = 100
    scene.render.use_border = True
    scene.render.use_crop_to_border = True
    scene.render.border_max_x = 0.550
    scene.render.border_min_x = 0.490
    scene.render.border_min_y = 0.530
    scene.render.border_max_y = 0.590
    scene.render.use_compositing = bool(False)

#and check if additional files aren't missing
bpy.ops.file.report_missing_files()
