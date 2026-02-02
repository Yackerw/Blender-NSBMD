import bpy
from . import util
import mathutils


class NSBMaterial():
    def __init__(self):
        self.DIF_AMB = 0
        self.SPE_EMI = 0
        self.POLY_ATTR_OR = 0
        self.POLY_ATTR_MASK = 0x3F1FF8FF
        self.TEXIMAGE_PARAMS = 0
        self.tex_width = 0
        self.tex_height = 0
        self.name = "Material"
        self.use_vcol = False
        self.texture_name = "Texture"
        self.billboard_mode = 0
        self.palette_override = ""
        self.tex_ind = 0
        self.pal_ind = -1
        self.matrix = (0, 0, 0)
        self.scale = (1.0,1.0,1.0)
        self.offs = (0,0,0)
        self.rot = (0,1.0)


def GetMaterialInfo(model, texs):
    retValue = []
    for mat in model.materials:
        def get_list(node_input):
            node_to_work_on = to_socket_from_socket.get(node_input, node_input)
            return node_to_work_on.default_value[::]

        def get_value(node_input):
            node_to_work_on = to_socket_from_socket.get(node_input, node_input)
            return node_to_work_on.default_value

        from_socket_to_socket = dict([[link.from_socket, link.to_socket] for link in mat.node_tree.links])
        to_socket_from_socket = dict([[link.to_socket, link.from_socket] for link in mat.node_tree.links])
        shader_node = False
        texture_node = False
        vector_node = False

        for node in mat.node_tree.nodes[::]:
            if node.bl_idname == "ShaderNodeNSBMDShader":
                shader_node = node
                break
        if not shader_node:
            raise ReferenceError("Can't find NSBMD Shader Node in material " + mat.name)
        texture_node = to_socket_from_socket.get(shader_node.inputs[5])
        if not texture_node:
            raise ReferenceError("Can't find Texture Node in material " + mat.name)
        texture_node = texture_node.node
        vector_node = to_socket_from_socket.get(texture_node.inputs[0])
        if not vector_node:
            raise ReferenceError("Can't find Vector Node in material " + mat.name)
        vector_node = vector_node.node

        newMat = NSBMaterial()
        lightEnable = {}
        lightEnable[0] = int(shader_node.light1)
        lightEnable[1] = int(shader_node.light2)
        lightEnable[2] = int(shader_node.light3)
        lightEnable[3] = int(shader_node.light4)
        lightingMode = int(shader_node.lighting_mode)  # multiply, decal, toon/highlight, shadow
        backFaceOn = int(shader_node.backface)
        frontFaceOn = int(shader_node.frontface)
        writeDepthTransparent = int(shader_node.write_depth_transparent)
        farPlaneClip = int(shader_node.far_plane_clip) # probably not necessary as this kinda sucks when turned off
        oneDotPolygons = int(shader_node.one_dot_polygons) # whether a polygon should render if it would occupy < 1 pixel
        depthTestEquals = int(shader_node.depth_test_equals) # when set to 1 depth will be an equals check instead of less. no you can't turn off depth test entirely
        fogEnabled = int(shader_node.fog_enabled)
        alpha = get_value(shader_node.inputs['Material Alpha']) # 31 = 1.0, 0 = wireframe rendering
        polygonId = int(shader_node.polygon_id) # 0-0x3F: used as a stencil as well as for outline edge marking
        
        newMat.POLY_ATTR_OR = lightEnable[0] | (lightEnable[1] << 1) | (lightEnable[2] << 2) | (lightEnable[3] << 3)
        newMat.POLY_ATTR_OR |= (lightingMode << 4) | (backFaceOn << 6) | (frontFaceOn << 7)
        newMat.POLY_ATTR_OR |= (writeDepthTransparent << 11) | (farPlaneClip << 12) | (oneDotPolygons << 13)
        newMat.POLY_ATTR_OR |= (depthTestEquals << 14) | (fogEnabled << 15) | (alpha << 16) | (polygonId << 24)

        rgba = get_list(shader_node.inputs['Material Color'])
        ambrgba = get_list(shader_node.inputs['Ambient'])
        specrgba = get_list(shader_node.inputs['Specular'])
        emirgba = get_list(shader_node.inputs['Emission'])

        diffR = int(rgba[0]*255)
        diffG = int(rgba[1]*255)
        diffB = int(rgba[2]*255)
        ambR = int(ambrgba[0]*255)
        ambG = int(ambrgba[1]*255)
        ambB = int(ambrgba[2]*255)
        
        diffDS = (diffR >> 3) | ((diffG >> 3) << 5) | ((diffB >> 3) << 10)
        ambDS = (ambR >> 3) | ((ambG >> 3) << 5) | ((ambB >> 3) << 10)
        
        newMat.DIF_AMB = diffDS | (ambDS << 16)
        
        specR = int(specrgba[0]*255)
        specG = int(specrgba[1]*255)
        specB = int(specrgba[2]*255)
        emiR = int(emirgba[0]*255)
        emiG = int(emirgba[1]*255)
        emiB = int(emirgba[2]*255)

        newMat.use_vcol = get_value(shader_node.inputs['Use Vertex Color'])
        newMat.billboard_mode = int(shader_node.billboard_mode)
        newMat.palette_override = shader_node.palette_override
        
        useSpecTable = int(shader_node.use_spec_table)
        
        specDS = (specR >> 3) | ((specG >> 3) << 5) | ((specB >> 3) << 10)
        emiDS = (emiR >> 3) | ((emiG >> 3) << 5) | ((emiB >> 3) << 10)
        
        newMat.SPE_EMI = specDS | (emiDS << 16) | (useSpecTable << 15)

        if not texture_node.image:
            raise ReferenceError("Please add Image to Texture Node in material " + mat.name)
        newMat.texture_name = texture_node.image.name.rsplit('.', 1)[0]
        
        texRepeatModeU = int(vector_node.u_type) # clamp, repeat, mirror
        texRepeatModeV = int(vector_node.v_type)
        
        repeatModeUDS = texRepeatModeU
        repeatModeVDS = texRepeatModeV
        if texRepeatModeU == 2:
            repeatModeUDS = 5
        if texRepeatModeV == 2:
            repeatModeVDS = 5
        
        texTransformMode = int(vector_node.transform_mode) # none, UV, normal, position

        newMat.matrix = mathutils.Matrix.LocRotScale(
            get_list(vector_node.inputs["UV Offset"]), mathutils.Euler(get_list(vector_node.inputs["UV Rotation"])), get_list(vector_node.inputs["UV Scale"]))
        
        newMat.offs = get_list(vector_node.inputs["UV Offset"])
        newMat.scale = get_list(vector_node.inputs["UV Scale"])
        rot = get_list(vector_node.inputs["UV Rotation"])
        newMat.rot = (math.sin(rot[2]), math.cos(rot[2]))
        
        newMat.TEXIMAGE_PARAMS = (repeatModeUDS << 16) | (repeatModeVDS << 17) | (texTransformMode << 30)
        
        newMat.name = mat.name
        
        if not (newMat.texture_name in texs.texNames):
            print(texs.texNames[0])
            print(newMat.texture_name)
            util.show_tex_not_found("NSBMD Exporter", newMat.texture_name)
            return None
        
        newMat.tex_ind = texs.texNames.index(newMat.texture_name)
        
        # no palette involved for direct color!
        if (texs.texFormats[newMat.tex_ind] != 7):
        
            if (newMat.palette_override == ""):
                newMat.palette_override = newMat.texture_name + "_pl"
            
            if not (newMat.palette_override in texs.paletteNames):
                util.show_pal_not_found("NSBMD Exporter", newMat.palette_override)
                return None
            
            newMat.pal_ind = texs.paletteNames.index(newMat.palette_override)
        
        #newMat.tex_width, newMat.tex_height = texture_node.image.size
        newMat.tex_width = texs.texSizesX[newMat.tex_ind]
        newMat.tex_height = texs.texSizesY[newMat.tex_ind]
        
        retValue.append(newMat)
    return retValue