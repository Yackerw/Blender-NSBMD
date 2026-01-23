import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
import textwrap
from . import export
from .node_groups import MakeGroups


class ExportNSBMD(bpy.types.Operator, ExportHelper):
    """Export an NSBMD Model archive"""
    bl_idname = "export.nsbmd"
    bl_label = "Export NSBMD Model"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ".nsbmd"
    filter_glob: StringProperty(
        default=".nsbmd",
        options={'HIDDEN'},
        maxlen=255)

    # idk if you want any toggles
    
    pack_tex: BoolProperty(
        name="Pack textures",
        description="Packs textures from nsbtx into nsbmd.",
        default=True)

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
        layout.row().prop(self, "pack_tex")
        #box.row().prop(self, "setting_i_suppose")

    def execute(self, context):
        # preferences = bpy.context.preferences.addons[__package__.partition(".")[0]].preferences
        settings = {}
        return export.ExportModel(context, self.filepath, settings, self.pack_tex).execute()


def menu_func_export(self, context):  # add to dynamic menu
    self.layout.operator(ExportNSBMD.bl_idname, text="Export NSBMD Model")


class NSBMDNodeAdd(bpy.types.Operator):
    """Spawn in an NSBMD node"""
    bl_idname = "node.add_node_nsbmd"
    bl_label = "Node Add NSBMD Operator"

    use_transform: BoolProperty(
    )

    type: StringProperty(
    )

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'ShaderNodeTree'

    def execute(self, context):
        MakeGroups().execute()
        bpy.ops.node.add_node(use_transform=self.use_transform, type=self.type)
        return {'FINISHED'}


class NodeNSBMDSetup(bpy.types.Operator):
    """Spawn in a NSBMD node set up"""
    bl_idname = "node.nsbmd_operator"
    bl_label = "NSBMD Node Operator"

    @classmethod
    def poll(cls, context):
        return context.area.ui_type == 'ShaderNodeTree'

    def execute(self, context):
        tree = context.space_data.node_tree
        context.object.active_material.blend_method = "BLEND"
        context.object.active_material.use_backface_culling = True
        context.object.active_material.show_transparent_back = False

        MakeGroups().execute()
        existing_diffuse = False

        node = tree.nodes.get("Image Texture")  # blender wants node name w/e
        if node and node.image:
            existing_diffuse = node.image
        else:
            for node in tree.nodes:
                if node.bl_idname == "ShaderNodeTexImage" and node.image:
                    existing_diffuse = node.image
        for node in tree.nodes:
            tree.nodes.remove(node)

        shader = tree.nodes.new('ShaderNodeNSBMDShader')
        shader.location = (10, 310)

        node = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(node.inputs[0], shader.outputs[0])
        node.location = (300, 300)

        tree.links.new(node.inputs[0], shader.outputs[0])

        image = tree.nodes.new(type="ShaderNodeTexImage")
        image.location = (-400, 250)

        vector = tree.nodes.new(type='ShaderNodeNSBMDVector')
        vector.location = (-700, 200)
        tree.links.new(image.inputs[0], vector.outputs[0])

        tree.links.new(shader.inputs["Texture Color"], image.outputs[0])
        tree.links.new(shader.inputs["Texture Alpha"], image.outputs[1])

        if existing_diffuse:
            image.image = existing_diffuse
        return {'FINISHED'}


class NSBMDSetTextureFile(bpy.types.Operator, ImportHelper):
    """Assign a NSBTX file to this model"""
    bl_idname = "operator.nsbmd_assign_nsbtx"
    bl_label = "Assign NSBTX file"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    filename_ext = "*.nsbtx"
    filter_glob: StringProperty(
        default="*.nsbtx",
        options={'HIDDEN'},
        maxlen=255)

    def execute(self, context):
        context.object.data.nsbtx_path = self.filepath
        return {'FINISHED'}
