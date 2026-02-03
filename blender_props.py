import bpy


def custom_reg():
    bpy.types.Mesh.nsbtx_path = bpy.props.StringProperty(name='NSBTX path', description="File Path to the NSBTX file to assign to this model", options=set())
    bpy.types.Mesh.nsbtx_index = bpy.props.FloatProperty(name='NSBMD index', description="Model index in file", options=set())


def custom_unreg():
    del bpy.types.Mesh.nsbtx_path
    del bpy.types.Mesh.nsbtx_index
