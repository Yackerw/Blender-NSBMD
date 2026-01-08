import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from bpy_extras.io_utils import ExportHelper
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
