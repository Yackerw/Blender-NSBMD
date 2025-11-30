import bpy


class GetNSBMDTexture(bpy.types.Operator):
    """Get Textures from this armature's materials"""
    bl_idname = "operator.nsbmd_get_textures"
    bl_label = "Get Textures"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.object
        if obj.id_type != 'OBJECT' and obj.data != 'ARMATURE':
            return {'FINISHED'}
        materials = set()
        images = set()
        scene_ob = set(context.scene.objects[:])
        mesh_list = [a for a in obj.children if a.type == "MESH" and a in scene_ob]
        for child in mesh_list:
            for m_slot in child.material_slots:
                materials.add(m_slot.material)
        for material in list(materials):
            if material.node_tree:
                for node in material.node_tree.nodes:
                    node_n = node.bl_idname
                    if node_n == 'ShaderNodeTexImage':
                        images.add(node.image)

        while len(images) > len(context.object.data.nsbmd_textures):
            context.object.data.nsbmd_textures.add()
        while len(images) < len(context.object.data.nsbmd_textures):
            context.object.data.nsbmd_textures.remove(len(context.object.data.nsbmd_textures) - 1)

        for img, tex in zip(list(images), obj.data.nsbmd_textures):
            tex.texture = img

        return {'FINISHED'}
