import bpy


# panels

class GENERIC_panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NSBMD"


class NSBMD_PT_Texture(GENERIC_panel, bpy.types.Panel):
    bl_label = "NSBMD Textures"

    @classmethod
    def poll(cls, context):
        if context.object is not None and context.object.type == "ARMATURE":
            if bpy.context.active_object and bpy.context.active_object.mode == "OBJECT":
                return True
        return False

    def draw(self, context):
        layout = self.layout
        if context.object.type == "ARMATURE":
            obj = context.object
            layout.prop(obj.data, "nsbmd_texture_count")
            layout.operator("operator.nsbmd_get_textures")
            for i in obj.data.nsbmd_textures:
                layout.prop(i, "texture", text="")
                layout.prop(i, "image_compression", text="")
