import bpy


def custom_reg():
    bpy.types.Mesh.nsbtx_path = bpy.props.StringProperty(name='NSBTX path', description="File Path to the NSBTX file to assign to this model", options=set())


def custom_unreg():
    del bpy.types.Mesh.nsbtx_path
