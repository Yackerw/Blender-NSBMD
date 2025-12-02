import bpy


class ExportModel:
    def __init__(self, context, filepath, settings):
        pass

    def execute(self):
        # code to get armatures if people selected meshes
        arma_list = []
        selected_obj = set(bpy.context.selected_objects)
        while selected_obj:
            obj = selected_obj.pop()
            while obj.type != "ARMATURE":
                if obj.parent:
                    obj = obj.parent
                else:
                    break
            if obj.type == "ARMATURE":
                arma_list.append(obj)
            selected_obj = selected_obj - set(obj.children)
        arma_list = tuple(set(arma_list))

        if not arma_list:
            def draw(self, context):
                self.layout.label(text="No valid models were selected!")

            bpy.context.window_manager.popup_menu(draw_func=draw, title="NSBMD Exporter", icon="ERROR")
            return {'FINISHED'}

        for armature in arma_list:
            pass  # do actual work in here

        return{'FINISHED'}
