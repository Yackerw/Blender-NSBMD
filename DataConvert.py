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

class NSBMDVertList():
    def __init__(self):
        self.verts = []
        self.materialInd = 0
        self.matrixDeps = []
        self.tris = []
        self.quads = []
        self.vertConversion = {}

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
        self.vertCount = 0
        self.triCount = 0
        self.quadCount = 0
        self.boundsX = 0
        self.boundsY = 0
        self.boundsZ = 0
        self.boundsXWidth = 0
        self.boundsHeight = 0
        self.boundsZWidth = 0


def ConvertVerts(meshes, materials):
    data = NSBMDModelData()
    
    vert_maxX = -99999999
    vert_maxY = -99999999
    vert_maxZ = -99999999
    vert_minX = 99999999
    vert_minY = 99999999
    vert_minZ = 99999999
    
    for mesh in meshes:
        i = 0
        verts = mesh.verts
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
    
    max_pos = 32767/4096
    min_pos = -8
    
    """if vert_maxX > max_pos or vert_minX < min_pos:
        recenterX = -vert_centerX
        vert_maxX += recenterX 
    if vert_maxY > max_pos or vert_minY < min_pos:
        recenterY = -vert_centerY
        vert_maxY += recenterY
    if vert_maxZ > max_pos or vert_minZ < min_pos:
        recenterZ = -vert_centerZ
        vert_maxZ += recenterZ"""
    
    if vert_maxX > max_pos:
        rescaleX = vert_maxX / max_pos
    if vert_maxY > max_pos:
        rescaleY = vert_maxY / max_pos
    if vert_maxZ > max_pos:
        rescaleZ = vert_maxZ / max_pos
    
    rescaleX = max(rescaleX,rescaleY,rescaleZ)
    rescaleY = rescaleX
    rescaleZ = rescaleX
    
    #data.offsX = -round(recenterX*4096)
    #data.offsY = -round(recenterY*4096)
    #data.offsZ = -round(recenterZ*4096)
    data.scaleX = round(rescaleX*4096)
    data.scaleY = round(rescaleY*4096)
    data.scaleZ = round(rescaleZ*4096)
    
    data.boundsX = int(vert_centerX*rescaleX*4096)
    data.boundsY = int(vert_centerY*rescaleY*4096)
    data.boundsZ = int(vert_centerZ*rescaleZ*4096)
    data.boundsXWidth = int(max(abs(vert_centerX - vert_maxX), abs(vert_centerX - vert_minX))*rescaleX*4096)
    data.boundsHeight = int(max(abs(vert_centerY - vert_maxY), abs(vert_centerY - vert_minY))*rescaleY*4096)
    data.boundsZWidth = int(max(abs(vert_centerZ - vert_maxZ), abs(vert_centerZ - vert_minZ))*rescaleZ*4096)
    
    
    # maybe do something about UVs?
    
    # convert verts
    
    weightMap = {}
    inverseWeightMap = []
    
    j = 0
    for mesh, mat in zip(meshes, materials):
        vertList = []
        verts = mesh.verts
        vertData = NSBMDVertList()
        vertData.tris = mesh.tris
        vertData.quads = mesh.quads
        vertData.materialInd = j
        i = 0
        while i < len(verts):
            newVert = NSBMDDataVert()
            cVert = verts[i]
            if (mat.use_vcol):
                newVert.colr = round((cVert.colr / 255) * 31)
                newVert.colg = round((cVert.colg / 255) * 31)
                newVert.colb = round((cVert.colb / 255) * 31)
                newVert.cola = round((cVert.cola / 255) * 31)
            else:
                newVert.normx = round(cVert.normx * 511)
                newVert.normy = round(cVert.normy * 511)
                newVert.normz = round(cVert.normz * 511)
            newVert.x = int(round(((cVert.x + recenterX) / rescaleX) * 4096))
            newVert.y = int(round(((cVert.y + recenterY) / rescaleY) * 4096))
            newVert.z = int(round(((cVert.z + recenterZ) / rescaleZ) * 4096))
            
            newVert.u = int(round(cVert.u * 16 * mat.tex_width))
            newVert.v = int(round(cVert.v * 16 * mat.tex_height))
            
            if not cVert.weights in weightMap:
                weightMap[cVert.weights] = len(inverseWeightMap)
                inverseWeightMap.append(cVert.weights)
            
            newVert.targetMatrix = weightMap[cVert.weights]
            
            if not newVert.targetMatrix in vertData.matrixDeps:
                vertData.matrixDeps.append(newVert.targetMatrix)
            
            vertList.append(newVert)
            
            i += 1
        
        vertData.verts = vertList
        # split if >30 weights
        if (len(vertData.matrixDeps) > 30):
            vertDatas = []
            for i in range(0,len(vertData.tris),3):
                v1 = vertData.verts[vertData.tris[i]]
                v2 = vertData.verts[vertData.tris[i+1]]
                v3 = vertData.verts[vertData.tris[i+2]]
                vertsAsArray = []
                vertsAsArray.append(v1)
                vertsAsArray.append(v2)
                vertsAsArray.append(v3)
                foundExisting = False
                # check if vert combo already exists
                for vData in vertDatas:
                    if (v1.targetMatrix in vData.matrixDeps) and (v2.targetMatrix in vData.matrixDeps) and (v3.targetMatrix in vData.matrixDeps):
                        foundExisting = True
                        for k in range(0,3):
                            if (vertData.tris[i+k] in vData.vertConversion):
                                vData.tris.append(vData.vertConversion[vertData.tris[i+k]])
                            else:
                                vData.tris.append(len(vData.verts))
                                vData.vertConversion[vertData.tris[i+k]] = len(vData.verts)
                                vData.verts.append(vertsAsArray[k])
                if (foundExisting):
                    continue
                # check for partial match
                closestMatch = -1
                closestMatchCount = 0
                for k in range(0,len(vertDatas)):
                    vData = vertDatas[k]
                    currMatchCount = 0
                    for v in vertsAsArray:
                        if v.targetMatrix in vData.matrixDeps:
                            currMatchCount += 1
                    if (len(vData.matrixDeps)+(3-currMatchCount)<=30) and (currMatchCount > closestMatchCount):
                        closestMatch = k
                        closestMatchCount = currMatchCount
                
                if closestMatch == -1:
                    newVertData = NSBMDVertList()
                    newVertData.materialInd = vertData.materialInd
                    closestMatch = len(vertDatas)
                    vertDatas.append(newVertData)
                
                vData = vertDatas[closestMatch]
                for k in range(0,3):
                    if (vertData.tris[i+k] in vData.vertConversion):
                        vData.tris.append(vData.vertConversion[vertData.tris[i+k]])
                    else:
                        vData.tris.append(len(vData.verts))
                        vData.vertConversion[vertData.tris[i+k]] = len(vData.verts)
                        vData.verts.append(vertsAsArray[k])
                        if (not vertsAsArray[k].targetMatrix in vData.matrixDeps):
                            vData.matrixDeps.append(vertsAsArray[k].targetMatrix)
            
            for i in range(0,len(vertData.quads),4):
                v1 = vertData.verts[vertData.quads[i]]
                v2 = vertData.verts[vertData.quads[i+1]]
                v3 = vertData.verts[vertData.quads[i+2]]
                v4 = vertData.verts[vertData.quads[i+3]]
                vertsAsArray = []
                vertsAsArray.append(v1)
                vertsAsArray.append(v2)
                vertsAsArray.append(v3)
                vertsAsArray.append(v4)
                foundExisting = False
                # check if vert combo already exists
                for vData in vertDatas:
                    if (v1.targetMatrix in vData.matrixDeps) and (v2.targetMatrix in vData.matrixDeps) and (v3.targetMatrix in vData.matrixDeps) and (v4.targetMatrix in vData.matrixDeps):
                        foundExisting = True
                        for k in range(0,4):
                            if (vertData.quads[i+k] in vData.vertConversion):
                                vData.quads.append(vData.vertConversion[vertData.quads[i+k]])
                            else:
                                vData.quads.append(len(vData.verts))
                                vData.vertConversion[vertData.quads[i+k]] = len(vData.verts)
                                vData.verts.append(vertsAsArray[k])
                if (foundExisting):
                    continue
                # check for partial match
                closestMatch = -1
                closestMatchCount = 0
                for k in range(0,len(vertDatas)):
                    vData = vertDatas[k]
                    currMatchCount = 0
                    for v in vertsAsArray:
                        if v.targetMatrix in vData.matrixDeps:
                            currMatchCount += 1
                    if (len(vData.matrixDeps)+(4-currMatchCount)<=30) and (currMatchCount > closestMatchCount):
                        closestMatch = k
                        closestMatchCount = currMatchCount
                
                if closestMatch == -1:
                    newVertData = NSBMDVertList()
                    newVertData.materialInd = vertData.materialInd
                    closestMatch = len(vertDatas)
                    vertDatas.append(newVertData)
                
                vData = vertDatas[closestMatch]
                for k in range(0,4):
                    if (vertData.quads[i+k] in vData.vertConversion):
                        vData.quads.append(vData.vertConversion[vertData.quads[i+k]])
                    else:
                        vData.quads.append(len(vData.verts))
                        vData.vertConversion[vertData.quads[i+k]] = len(vData.verts)
                        vData.verts.append(vertsAsArray[k])
                        if (not vertsAsArray[k].targetMatrix in vData.matrixDeps):
                            vData.matrixDeps.append(vertsAsArray[k].targetMatrix)
            
            for vData in vertDatas:
                data.modelVerts.append(vData)
        else:
            data.modelVerts.append(vertData)
        
        j += 1
    
    # TODO: split meshes with too many weights
    
    data.NSBCommands.append(2)
    data.NSBCommands.append(0)
    data.NSBCommands.append(1)
    data.NSBCommands.append(6)
    data.NSBCommands.append(0)
    data.NSBCommands.append(0)
    data.NSBCommands.append(0)
    data.NSBCommands.append(0xB)
    currMat = -1
    for i in range(0,len(data.modelVerts)):
        if (data.modelVerts[i].materialInd != currMat):
            currMat = data.modelVerts[i].materialInd
            data.NSBCommands.append(0x4)
            data.NSBCommands.append(currMat)
        data.NSBCommands.append(0x5)
        data.NSBCommands.append(i)
    data.NSBCommands.append(1) # END: TODO: handle this when writing so we cover all meshes
    
    return data