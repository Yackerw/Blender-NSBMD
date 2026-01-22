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
            ('0', "Multiply", ""),
            ('1', "Decal", ""),
            ('2', "Toon / Highlight", "Depends on the game"),
            ('3', "Shadow", ""),
        )
        return blend_types

    def billboard_modes(self, context):
        mix_types = (
            ('0', "None", "Don't render as a Billboard"),
            ('1', "Billboard", ""),
            ('2', "Billboard on Y", "Only rotate Billboard left/right"),
        )
        return mix_types

    def update_lighting_modes(self, context):
        if not self.lighting_mode:
            self.lighting_mode = self.lighting_modes(context)[0][0]
        blend_types = {
            "0": '.NSBMD_SHADER_MULTI',
            "1": '.NSBMD_SHADER_DECAL',
            "2": '.NSBMD_SHADER_TOON',
            "3": '.NSBMD_SHADER_MULTI',
        }

        self.node_tree = bpy.data.node_groups[blend_types[self.lighting_mode]]

    def update_billboard(self, context):
        if not self.billboard_mode:
            self.billboard_mode = self.billboard_modes(context)[0][0]

    def update_facing(self, context):
        curr_mat = _get_material(self)
        if self["backface"] and self["frontface"] or self["backface"]:
            curr_mat.use_backface_culling = False
        elif self["frontface"]:
            curr_mat.use_backface_culling = True
        else:
            curr_mat.use_backface_culling = False

    def draw_buttons(self, context, layout):
        ignore = {'Advanced', 'Lighting Mode', 'Draw Backface', 'Draw Frontface', 'Polygon ID', 'Billboard Render'}
        _shader_ui_common(self, ignore, layout, {5, 8})

        layout.prop(self, 'lighting_mode', text="")
        layout.prop(self, 'billboard_mode', text="")
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

    use_spec_table: BoolProperty(name="Use Specular Table", default=False, options=set())
    write_depth_transparent: BoolProperty(name="Write Depth Transparent", default=False, options=set())
    far_plane_clip: BoolProperty(name="Render if Clip FarPlane", default=True, options=set())
    one_dot_polygons: BoolProperty(name="Render if occupies <1 pixel", default=False, options=set())
    depth_test_equals: BoolProperty(name="Depth test as equals", default=False, options=set())
    fog_enabled: BoolProperty(name="Enable Fog", default=False, options=set())

    billboard_mode: EnumProperty(name="Billboard Render", update=update_billboard, items=billboard_modes, options=set())
    palette_override: StringProperty(name="Palette Name", description="Name of palette to override default palette name", options=set())

    advanced: BoolProperty(name="Advanced", default=False, options=set())

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.NSBMD_SHADER_MULTI']
        self.lighting_mode = self.lighting_modes(context)[0][0]
        self.billboard_mode = self.billboard_modes(context)[0][0]
        self.palette_override = ""
        self["backface"] = False
        self["frontface"] = True


class ShaderNodeNSBMDVector(CustomNodetreeNodeBaseNN, ShaderNodeCustomGroup):
    bl_label = "NSBMD Vector"
    bl_idname = "ShaderNodeNSBMDVector"
    bl_width_default = 180

    def transform_modes(self, context):
        mix_types = (
            ('0', "UV Only", "UV Transform without a transform matrix"),
            ('1', "UV Matrix", ""),
            ('2', "Normal", ""),
            ('3', "Position", ""),
        )
        return mix_types

    def u_types(self, context):
        wrap_types = (
            ('0', "Clamp U", ""),
            ('1', "Repeat U", ""),
            ('2', "Mirror U", ""),
        )
        return wrap_types

    def v_types(self, context):
        wrap_types = (
            ('0', "Clamp V", ""),
            ('1', "Repeat V", ""),
            ('2', "Mirror V", ""),
        )
        return wrap_types

    def copy(self, node):
        self.node_tree = node.node_tree

    def free(self):
        pass  # defining this so blender doesn't try to remove the group

    def update_mode(self, context):
        if not self.transform_mode:
            self.transform_mode = self.transform_modes(context)[0][0]
        mix_types = {
            "0": '.NSBMD_VECTOR_UV_MATRIXLESS',
            "1": '.NSBMD_VECTOR_UV',
            "2": '.NSBMD_VECTOR_NORMAL',
            "3": '.NSBMD_VECTOR_POSITION',
        }
        self.node_tree = bpy.data.node_groups[mix_types[self.transform_mode]]

        if self.transform_mode == '0':
            self.inputs["UV Offset"].hide = True
            self.inputs["UV Rotation"].hide = True
            self.inputs["UV Scale"].hide = True
        else:
            self.inputs["UV Offset"].hide = False
            self.inputs["UV Rotation"].hide = False
            self.inputs["UV Scale"].hide = False

    def update_u(self, context):
        if not self.u_type:
            self.u_type = self.u_types(context)[1][0]

        self.inputs["U"].default_value = int(self.u_type)

    def update_v(self, context):
        if not self.v_type:
            self.v_type = self.v_types(context)[1][0]

        self.inputs["V"].default_value = int(self.v_type)

    u_type: EnumProperty(name="U Wrapping", update=update_u, items=u_types)
    v_type: EnumProperty(name="V Wrapping", update=update_v, items=v_types)
    transform_mode: EnumProperty(name="Transform Mode", update=update_mode, items=transform_modes)

    def init(self, context):
        self.node_tree = bpy.data.node_groups['.NSBMD_VECTOR_UV_MATRIXLESS']
        self.transform_mode = self.transform_modes(context)[0][0]
        self.u_type = self.u_types(context)[1][0]
        self.v_type = self.v_types(context)[1][0]
        self.inputs["U"].hide = True
        self.inputs["V"].hide = True


classes = (
    ShaderNodeNSBMDShader,
    ShaderNodeNSBMDVector,
)
