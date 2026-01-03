import bpy
import nodeitems_utils
from bpy.props import *
from bpy.types import ShaderNodeCustomGroup


# blender crashing after reloading script is an issue with custom nodes
#  https://projects.blender.org/blender/blender/issues/72833


class CustomNodetreeNodeBaseNN:
    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        for prop in self.bl_rna.properties:
            if prop.is_runtime and not prop.is_readonly:
                if prop.type == "ENUM":
                    text = ""
                else:
                    text = prop.name
                layout.prop(self, prop.identifier, text=text)


class CustomNodetreeNodeBaseNNExpandLink:
    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        has_link = False
        for link in self.id_data.links:
            if link.to_socket == self.inputs["Specular"]:
                has_link = True
                break
        if not has_link:
            for prop in self.bl_rna.properties:
                if prop.is_runtime and not prop.is_readonly:
                    if prop.name == "Find Init":
                        layout.prop(self, prop.identifier, text=prop.name, expand=True)
                    elif prop.type == "ENUM":
                        layout.prop(self, prop.identifier, text="")
                    else:
                        layout.prop(self, prop.identifier, text=prop.name)

        else:
            for prop in self.bl_rna.properties:
                if prop.is_runtime and not prop.is_readonly:
                    if prop.name == "Find Init":
                        continue
                    elif prop.type == "ENUM":
                        layout.prop(self, prop.identifier, text="")
                    else:
                        layout.prop(self, prop.identifier, text=prop.name)


def _get_material(self):
    data_path = repr(self.id_data)
    if data_path.endswith('evaluated>'):  # you know i had to do it to em
        tree_name = self.id_data.get_output_node("ALL").outputs
        # bpy.data.materials['Material'].node_tree.nodes["Material Output"].outputs
        material_name = repr(tree_name).split("].node_tree")[0].split("bpy.data.materials[")[1][1:-1]
    else:
        material_name = repr(self.id_data)[20:-12]
    return bpy.data.materials[material_name]


def _shader_ui_common(self, ignore, layout, pad_ind):
    if self.advanced:  # if show advanced settings
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="", icon='DOWNARROW_HLT')
        row.prop(self, 'advanced', emboss=False)
        index = 0
        for prop in self.bl_rna.properties:
            if prop.is_runtime and not prop.is_readonly and prop.name not in ignore:
                if prop.type == "ENUM":
                    text = ""
                else:
                    text = prop.name
                layout.prop(self, prop.identifier, text=text)
                if index in pad_ind:
                    layout.separator(factor=0.15)
                index += 1
    else:
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="", icon='RIGHTARROW')
        row.prop(self, 'advanced', emboss=False)
    layout.separator(factor=0.3)


class ShaderNodeNSBMDShader(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NSBMD Shader"
    bl_idname = "ShaderNodeNSBMDShader"
    bl_width_default = 180

    def lighting_modes(self, context):
        blend_types = (
            ('.NSBMD_SHADER_MULTI', "Multiply", ""),
            ('.NSBMD_SHADER_DECAL', "Decal", ""),
            ('.NSBMD_SHADER_TOON', "Toon / Highlight", "Depends on the game"),
            ('.NSBMD_SHADER_MULTI', "Shadow", ""),
        )
        return blend_types

    def update_lighting_modes(self, context):
        if not self.lighting_mode:
            self.lighting_mode = self.lighting_modes(context)[0][0]

        self.node_tree = bpy.data.node_groups[self.lighting_mode]

    def update_facing(self, context):
        curr_mat = _get_material(self)
        if self["backface"] and self["frontface"] or self["backface"]:
            curr_mat.use_backface_culling = False
        elif self["frontface"]:
            curr_mat.use_backface_culling = True
        else:
            curr_mat.use_backface_culling = False

    def draw_buttons(self, context, layout):
        ignore = {'Advanced', 'Lighting Mode', 'Draw Backface', 'Draw Frontface', 'Polygon ID'}
        _shader_ui_common(self, ignore, layout, {5, 8})

        row = layout.row(align=True)

        layout.prop(self, 'lighting_mode', text="")
        layout.prop(self, 'backface')
        layout.prop(self, 'frontface')
        layout.prop(self, 'polygon_id')

    light1: BoolProperty(name="Light 1", default=True, options=set())
    light2: BoolProperty(name="Light 2", default=False, options=set())
    light3: BoolProperty(name="Light 3", default=False, options=set())
    light4: BoolProperty(name="Light 4", default=False, options=set())

    lighting_mode: EnumProperty(name="Lighting Mode", update=update_lighting_modes, items=lighting_modes, options=set()) # LATER
    backface: BoolProperty(name="Draw Backface", default=False, options=set(), update=update_facing)
    frontface: BoolProperty(name="Draw Frontface", default=True, options=set(), update=update_facing)
    polygon_id: IntProperty(name='Polygon ID', default=0, min=0, max=63)

    write_depth_transparent: BoolProperty(name="Write Depth Transparent", default=False, options=set())
    far_plane_clip: BoolProperty(name="Render if Clip FarPlane", default=True, options=set())
    one_dot_polygons: BoolProperty(name="Render if occupies <1 pixel", default=False, options=set())
    depth_test_equals: BoolProperty(name="Depth test as equals", default=False, options=set())
    fog_enabled: BoolProperty(name="Enable Fog", default=False, options=set())

    advanced: BoolProperty(name="Advanced", default=False, options=set())

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.NSBMD_SHADER_MULTI']
        self.lighting_mode = self.lighting_modes(context)[0][0]
        self["backface"] = False
        self["frontface"] = True


classes = (
    ShaderNodeNSBMDShader,
)