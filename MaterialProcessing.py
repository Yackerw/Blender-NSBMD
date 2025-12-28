import bpy

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

def GetMaterialInfo(model):
    retValue = []
    for mat in model.materials:
        newMat = NSBMaterial()
        # TODO: put these in material
        lightEnable = {}
        lightEnable[0] = 0
        lightEnable[1] = 0
        lightEnable[2] = 0
        lightEnable[3] = 0
        lightingMode = 0 # multiply, decal, toon/highlight, shadow
        backFaceOn = 0
        frontFaceOn = 1
        writeDepthTransparent = 0
        farPlaneClip = 1 # probably not necessary as this kinda sucks when turned off
        oneDotPolygons = 0 # whether a polygon should render if it would occupy < 1 pixel
        depthTestEquals = 0 # when set to 1 depth will be an equals check instead of less. no you can't turn off depth test entirely
        fogEnabled = 0
        alpha = 31 # 31 = 1.0, 0 = wireframe rendering
        polygonId = 0 # 0-0x3F: used as a stencil as well as for outline edge marking
        
        newMat.POLY_ATTR_OR = lightEnable[0] | (lightEnable[1] << 1) | (lightEnable[2] << 2) | (lightEnable[3] << 3)
        newMat.POLY_ATTR_OR |= (lightingMode << 4) | (backFaceOn << 6) | (frontFaceOn << 7)
        newMat.POLY_ATTR_OR |= (writeDepthTransparent << 11) | (farPlaneClip << 12) | (oneDotPolygons << 13)
        newMat.POLY_ATTR_OR |= (depthTestEquals << 14) | (fogEnabled << 15) | (alpha << 16) | (polygonId << 24)
        
        diffR = 255
        diffG = 255
        diffB = 255
        ambR = 255
        ambG = 255
        ambB = 255
        
        diffDS = (diffR >> 3) | ((diffG >> 3) << 5) | ((diffB >> 3) << 10)
        ambDS = (ambR >> 3) | ((ambG >> 3) << 5) | ((diffB >> 3) << 10)
        
        newMat.DIF_AMB = diffDS | (ambDS << 16)
        
        specR = 255
        specG = 255
        specB = 255
        emiR = 255
        emiG = 255
        emiB = 255
        
        useSpecTable = 0
        
        specDS = (specR >> 3) | ((specG >> 3) << 5) | ((specB >> 3) << 10)
        emiDS = (emiR >> 3) | ((emiG >> 3) << 5) | ((emiB >> 3) << 10)
        
        newMat.SPE_EMI = specDS | (emiDS << 16) | (useSpecTable << 15)
        
        newMat.tex_width = 32
        newMat.tex_height = 32
        
        texRepeatModeU = 1 # clamp, repeat, mirror
        texRepeatModeV = 1
        
        repeatModeUDS = texRepeatModeU
        repeatModeVDS = texRepeatModeV
        if texRepeatModeU == 2:
            repeatModeUDS = 5
        if texRepeatModeV == 2:
            repeatModeVDS = 5
        
        texTransformMode = 1 # none, UV, normal, position
        
        newMat.TEXIMAGE_PARAMS = (repeatModeUDS << 16) | (repeatModeVDS << 17) | (texTransformMode << 30)
        
        newMat.name = mat.name
        
        retValue.append(newMat)
    return retValue