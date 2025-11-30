import bpy


def custom_reg():
    bpy.types.Armature.nsbmd_textures = bpy.props.CollectionProperty(type=NSBMDTexture)


def custom_unreg():
    del bpy.types.Armature.nsbmd_textures


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
