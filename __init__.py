bl_info = {
    "name": "Blender NSBMD",
    "description": "Plugin to Export NSBMD models",
    "author": "Yacker and Arg!!",
    "version": (0, 0, 0),
    "blender": (4, 1, 1),
    "location": "3d View > Sidebar",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/Yackerw/Blender-NSBMD/issues/new",
    "category": "Import-Export",
}

import sys

# https://blenderartists.org/t/how-to-reload-blender-addon-with-nested-modules-using-reload-scripts/1477986/2
if "bpy" in locals():
    if __name__ in sys.modules:
        del sys.modules[__name__]

    dotted = __name__ + "."
    for name in tuple(sys.modules):
        if name.startswith(dotted):
            del sys.modules[name]

import bpy
from bpy.app.handlers import persistent
from . import blender_ops  # look i have a suspicion operators will make python crash out
from . import blender_props
from . import panels


classes = [
    blender_props.NSBMDTexture,
    blender_ops.GetNSBMDTexture,
    panels.NSBMD_PT_About,
    panels.NSBMD_PT_Texture,
    blender_ops.ExportNSBMD,
]


# register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    #bpy.types.NODE_MT_add.append(menus.my_node_menu)
    bpy.types.TOPBAR_MT_file_export.append(blender_ops.menu_func_export)
    blender_props.custom_reg()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    #bpy.types.NODE_MT_add.remove(menus.my_node_menu)
    bpy.types.TOPBAR_MT_file_export.remove(blender_ops.menu_func_export)
    blender_props.custom_unreg()

# for when nodegroups are real
'''@persistent
def make_node_groups(scene):
    MakeGroups().execute()


bpy.app.handlers.load_post.append(make_node_groups)'''

