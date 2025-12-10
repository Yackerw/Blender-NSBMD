import bpy

class NSBMDDataVert():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.normx = 0
        self.normy = 0
        self.normz = 0
        self.u = 0
        self.v = 0
        self.colr = 0
        self.colg = 0
        self.colb = 0
        self.cola = 0
        self.targetMatrix = 0

class NSBMDModelData():
    def __init__(self):
        self.NSBCommands = []
        self.modelVerts = []
        self.offsX = 0
        self.offsY = 0
        self.offsZ = 0
        self.scaleX = 4096
        self.scaleY = 4096
        self.scaleZ = 4096
        self.usesColor = False

def ConvertVerts(verts, useVertColors, textureResolutionX, textureResolutionY, maintainMatrix, materialInd, meshInd):
    data = NSBMDModelData()
    
    data.usesColor = useVertColors
    
    vert_maxX = -99999999
    vert_maxY = -99999999
    vert_maxZ = -99999999
    vert_minX = 99999999
    vert_minY = 99999999
    vert_minZ = 99999999
    
    i = 0
    while (i < len(verts)):
        curr_v = verts[i]
        if (vert_maxX < curr_v.x):
            vert_maxX = curr_v.x
        if (vert_minX > curr_v.x):
            vert_minX = curr_v.x
        if (vert_maxY < curr_v.y):
            vert_maxY = curr_v.y
        if (vert_minY > curr_v.y):
            vert_minY = curr_v.y
        if (vert_maxZ < curr_v.z):
            vert_maxZ = curr_v.z
        if (vert_minZ > curr_v.z):
            vert_minZ = curr_v.z
        
        i = i + 1
    vert_centerX = (vert_maxX+vert_minX)/2
    vert_centerY = (vert_maxY+vert_minY)/2
    vert_centerZ = (vert_maxZ+vert_minZ)/2
    
    recenterX = 0
    recenterY = 0
    recenterZ = 0
    rescaleX = 1
    rescaleY = 1
    rescaleZ = 1
    
    max_pos = 32767/8
    min_pos = -8
    
    if vert_maxX > max_pos or vert_minX < min_pos:
        recenterX = -vert_centerX
        vert_maxX += recenterX 
    if vert_maxY > max_pos or vert_minY < min_pos:
        recenterY = -vert_centerY
        vert_maxY += recenterY
    if vert_maxZ > max_pos or vert_minZ < min_pos:
        recenterZ = -vert_centerZ
        vert_maxZ += recenterZ
    
    if vert_maxX > max_pos:
        rescaleX = vert_maxX / max_pos
    if vert_maxY > max_pos:
        rescaleY = vert_maxY / max_pos
    if vert_maxZ > max_pos:
        rescaleZ = vert_maxZ / max_pos
    
    data.offsX = -round(recenterX*4096)
    data.offsY = -round(recenterY*4096)
    data.offsZ = -round(recenterZ*4096)
    data.scaleX = round(rescaleX*4096)
    data.scaleY = round(rescaleY*4096)
    data.scaleZ = round(rescaleZ*4096)
    
    # maybe do something about UVs?
    
    # convert verts
    
    i = 0
    while i < len(verts):
        newVert = NSBMDDataVert()
        cVert = verts[i]
        if (useVertColors):
            newVert.colr = round((cVert.colr / 255) * 31)
            newVert.colg = round((cVert.colg / 255) * 31)
            newVert.colb = round((cVert.colb / 255) * 31)
            newVert.cola = round((cVert.cola / 255) * 31)
        else:
            newVert.normx = round(cVert.normx * 511)
            newVert.normy = round(cVert.normy * 511)
            newVert.normz = round(cVert.normz * 511)
        newVert.x = round(((cVert.x + recenterX) / rescaleX) * 4096)
        newVert.y = round(((cVert.y + recenterY) / rescaleY) * 4096)
        newVert.z = round(((cVert.z + recenterZ) / rescaleZ) * 4096)
        
        newVert.u = round(cVert.u * 16 * textureResolutionX)
        newVert.v = round(cVert.u * 16 * textureResolutionY)
        
        data.modelVerts.append(newVert)
        
        # TODO: WEIGHTS
    
    self.NSBCommands.append(4)
    self.NSBCommands.append(materialInd)
    self.NSBCommands.append(2)
    self.NSBCommands.append(materialInd)
    self.NSBCommands.append(0xB)
    self.NSBCommands.append(0x5)
    self.NSBCommands.append(meshInd)
    self.NSBCommands.append(1) # END: TODO: handle this when writing so we cover all meshes
    
    return data