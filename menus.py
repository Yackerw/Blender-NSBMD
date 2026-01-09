import bpy
from .nodes import classes


class NSBMD_MT_Node_Add(bpy.types.Menu):
    bl_label = "NSBMD"

    def draw(self, context):
        layout = self.layout
        for cla in classes:
            var = layout.operator("node.add_node_nsbmd", text=cla.bl_label)
            var.type = cla.bl_idname
            var.use_transform = True
        layout.operator("node.nsbmd_operator", text="Setup Nodes")


def nsbmd_node_menu(self, context):
    if context.area.ui_type == 'ShaderNodeTree':
        layout = self.layout
        layout.separator()
        layout.menu("NSBMD_MT_Node_Add")

