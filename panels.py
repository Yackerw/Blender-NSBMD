import bpy
import addon_utils
import requests

# noinspection PyArgumentList
user_ver = [addon.bl_info.get('version') for addon in addon_utils.modules()
            if addon.bl_info['name'] == "Blender NSBMD"][0]

try:
    latest_ver = requests.get("https://github.com/Yackerw/Blender-NSBMD/releases/latest").url.rsplit("/")[-1]
    if "." in latest_ver:
        latest_ver = tuple(int(a) for a in latest_ver.split("."))
    else:
        latest_ver = "No Releases."
except (requests.ConnectionError, requests.Timeout) as exception:
    latest_ver = "No Connection."


# panels

class GENERIC_panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NSBMD"


class NSBMD_PT_About(GENERIC_panel, bpy.types.Panel):
    bl_label = "NSBMD About"

    def draw(self, context):
        layout = self.layout
        layout.operator("export.nsbmd", text="Export nsbmd Model")

        layout.label(text="Tools Version: " + str(user_ver))
        if latest_ver == user_ver:
            layout.label(text="You're on the latest version.")
        elif "No" in latest_ver:
            layout.label(text=latest_ver)
        else:
            layout.label(text="You're not on the latest version!", icon="ERROR")
            layout.operator("wm.url_open", text="Latest Release Link: " + str(latest_ver)).url = \
                "https://github.com/Yackerw/Blender-NSBMD/releases/latest"
        blender_version = (4, 1, 1)
        if bpy.app.version != blender_version:
            layout.label(text='Please use Blender version ' + str(blender_version), icon='ERROR')


class NSBMD_PT_Texture(GENERIC_panel, bpy.types.Panel):
    bl_label = "NSBMD Textures"

    @classmethod
    def poll(cls, context):
        if context.object is not None and context.object.type == "MESH":
            if bpy.context.active_object:
                return True
        return False

    def draw(self, context):
        layout = self.layout
        if context.object.type == "MESH":
            obj = context.object
            layout.operator("operator.nsbmd_assign_nsbtx")
            layout.prop(obj.data, "nsbtx_path")
