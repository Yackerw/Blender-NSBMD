import bpy


def custom_reg():
    bpy.types.Armature.nsbmd_texture_count = bpy.props.IntProperty(name="Texture Count", default=0, min=0, max=255, update=update_texture_count)
    bpy.types.Armature.nsbmd_textures = bpy.props.CollectionProperty(type=NSBMDTexture)


def custom_unreg():
    del bpy.types.Armature.nsbmd_texture_count
    del bpy.types.Armature.nsbmd_textures


def update_texture_count(self, context):
    while context.object.data.nsbmd_texture_count > len(context.object.data.nsbmd_textures):
        context.object.data.nsbmd_textures.add()
    while context.object.data.nsbmd_texture_count < len(context.object.data.nsbmd_textures):
        context.object.data.nsbmd_textures.remove(len(context.object.data.nsbmd_textures)-1)


class NSBMDTexture(bpy.types.PropertyGroup):
    texture: bpy.props.PointerProperty(name="Texture", type=bpy.types.Image)
    image_compression: bpy.props.EnumProperty(
        name="Compression", description="Texture Compression Type",
        items=(
            ('1', '3 bit alpha, 5 bit color palette', ""),
            ('2', '2 bit color palette', ""),
            ('3', '4 bit color palette', ""),
            ('4', '8 bit color palette', ""),
            ('5', '3bpp compressed', ""),
            ('6', '5 bit alpha, 3 bit color palette', ""),
            ('7', '16 bit color', ""),
        ))
