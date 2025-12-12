import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ExportHelper
import textwrap
from . import export


class ExportNSBMD(bpy.types.Operator, ExportHelper):
    """Export an NSBMD Model archive"""
    bl_idname = "export.nsbmd"
    bl_label = "Export NSBMD Model"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ""
    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255)

    # idk if you want any toggles

    def draw(self, context):
        layout = self.layout
        # idk you dont need this stuff rn but you might want it later
        # preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        # layout.label(text="Exporter settings:", icon="KEYFRAME_HLT")
        box = layout.box()
        box.label(text="Important!!:")

        letter_count = int(context.region.width // 8)
        box.scale_y = 0.6
        info_text = "Please select the texture format in the NSBMD Tab in 3d view (with your object active)"
        wrapped_text = textwrap.TextWrapper(width=letter_count).wrap(text=info_text)
        [box.label(text=a) for a in wrapped_text]
        #box.row().prop(self, "setting_i_suppose")

    def execute(self, context):
        # preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        settings = {}
        return export.ExportModel(context, self.filepath, settings).execute()


def menu_func_export(self, context):  # add to dynamic menu
    self.layout.operator(ExportNSBMD.bl_idname, text="Export NSBMD Model")


class GetNSBMDTexture(bpy.types.Operator):
    """Get Textures from this meshes materials"""
    bl_idname = "operator.nsbmd_get_textures"
    bl_label = "Get Textures"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.type != 'MESH':
            return {'FINISHED'}
        materials = set()
        images = set()
        for m_slot in obj.material_slots:
            materials.add(m_slot.material)
        for material in list(materials):
            if material.node_tree:
                for node in material.node_tree.nodes:
                    node_n = node.bl_idname
                    if node_n == 'ShaderNodeTexImage':
                        images.add(node.image)
        context.object.data.nsbmd_texture_count = len(images)

        for img, tex in zip(list(images), obj.data.nsbmd_textures):
            tex.texture = img

        return {'FINISHED'}
