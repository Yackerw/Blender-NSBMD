import bpy
import mathutils
import math

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
        self.targetMatrix = 0
        self.sourceMatrix = 0

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

class NodeStackValue():
    def __init__(self):
        self.value = -1
        self.combo = False

class NodeContext():
    def __init__(self):
        self.curr_mtx = 0
        self.nodeStackPositions = []
        self.futureNodesUsed = []
        self.occupiedStack = []

def GetNodeIndex(name,nodes):
    for i in range(0,len(nodes)):
        if nodes[i].name == name:
            return i

def LoadNodeToStack(data, nodes, cVert, cVertInd, inverseWeightMap, nodeInd, isCombo, nodeCtx):
    # TODO: come up with a solution to indicate final rigs
    foundPos = FindNode(nodeCtx, nodeInd, isCombo)
    if foundPos == -1:
        # set up parents bone chain first thing so we don't wind up trying to use the same matrix position
        parentStackPos = 0
        parentIsCurrent = False
        if (isCombo == False and nodes[nodeInd].parent != -1):
            parentStackPos,parentIsCurrent = LoadNodeToStack(data, nodes, cVert, cVertInd, inverseWeightMap, nodes[nodeInd].parent, False, nodeCtx)
        stackPosFound = -1
        # first, try finding a free spot
        for k in range(1,31): # 0 is always reserved for base matrix
            if (nodeCtx.occupiedStack[k].value == -1):
                stackPosFound = k
                break
        if stackPosFound == -1:
            # that failed; prioritize a stale index
            for k in range(1,31):
                if nodeCtx.occupiedStack[k].combo == True:
                    matrixCombo = nodeCtx.occupiedStack[k].value
                    reliantOnMatrix = False
                    for dep in cVert.matrixDeps:
                        if dep == matrixCombo:
                            reliantOnMatrix = True
                            break
                    if reliantOnMatrix == True:
                        continue
                    stackPosFound = k
                    break
        if stackPosFound == -1:
            # that failed; prioritize a bone that's not necessary
            for k in range(1,31):
                if nodeCtx.occupiedStack[k].combo == False:
                    stackNode = nodeCtx.occupiedStack[k].value
                    stackIsRequired = False
                    for l in range(cVertInd, len(cVert.matrixDeps)): # don't bother keeping bones that are already used
                        dep = cVert.matrixDeps[l]
                        for depName,depWeight in inverseWeightMap[dep]:
                            depNodeInd = GetNodeIndex(depName, nodes)
                            if depNodeInd == stackNode:
                                stackIsRequired = True
                                break
                    if (data.scaleX == 4096):
                        for l in range(0,cVertInd): # we have to preserve 256 weight bones!
                            dep = cVert.matrixDeps[l]
                            for depName,depWeight in inverseWeightMap[dep]:
                                depNodeInd = GetNodeIndex(depName, nodes)
                                if depNodeInd == stackNode and depWeight == 256:
                                    stackIsRequired = True
                    if stackIsRequired == False:
                        stackPosFound = k
                        break
        # TODO: combos that are used later on but not now, and then parents of dependencies (anything that isn't a dependency)
        
        # stackPos should ALWAYS be found by now (and if it hasn't, that's a separate problem)
        
        if (stackPosFound == -1):
            print("Valid stack pos not found?")
            for i in range(0, 31):
                print(nodeCtx.occupiedStack[k].value)
                print(nodeCtx.occupiedStack[k].combo)
        
        if (isCombo == False):
            if parentIsCurrent == True:
                data.NSBCommands.append(0x26)
                data.NSBCommands.append(nodeInd)
                data.NSBCommands.append(max(nodes[nodeInd].parent,0))
                data.NSBCommands.append(0)
                data.NSBCommands.append(stackPosFound)
            else:
                data.NSBCommands.append(0x66)
                data.NSBCommands.append(nodeInd)
                data.NSBCommands.append(max(nodes[nodeInd].parent,0))
                data.NSBCommands.append(0)
                data.NSBCommands.append(stackPosFound)
                data.NSBCommands.append(parentStackPos)
            nodeCtx.nodeStackPositions[nodeInd] = stackPosFound
            nodeCtx.occupiedStack[stackPosFound].value = nodeInd
            nodeCtx.occupiedStack[stackPosFound].combo = False
            
            return stackPosFound,True
        else:
            # don't write anything, just reserve a slot
            nodeCtx.occupiedStack[stackPosFound].value = nodeInd
            nodeCtx.occupiedStack[stackPosFound].combo = True
            return stackPosFound,False
        
    return foundPos,False

def FindNode(nodeCtx, nodeInd, isCombo):
    for i in range(len(nodeCtx.occupiedStack)):
        if nodeCtx.occupiedStack[i].value == nodeInd and nodeCtx.occupiedStack[i].combo == isCombo:
            return i
    return -1

def ProcessNodes(data, nodes, inverseWeightMap, mats):
    data.NSBCommands.append(0x26) # set up first node; always parent most
    data.NSBCommands.append(len(nodes)-1)
    data.NSBCommands.append(len(nodes)-1)
    data.NSBCommands.append(0)
    data.NSBCommands.append(0)
    
    nodeCtx = NodeContext()
    nodeCtx.curr_mtx = len(nodes)-1
    for i in range(0,len(nodes)):
        nodeCtx.nodeStackPositions.append(-1)
        nodeCtx.futureNodesUsed.append(False)
    nodeCtx.nodeStackPositions[nodeCtx.curr_mtx] = 0
    nodeCtx.occupiedStack = []
    for i in range(0,31):
        nodeCtx.occupiedStack.append(NodeStackValue())
    nodeCtx.occupiedStack[0].value = len(nodes)-1 # -1 == not used
    
    currMat = -1
    for i in range(0,len(data.modelVerts)):
        cVert = data.modelVerts[i]
        for j in range(0,len(cVert.matrixDeps)):
            if (FindNode(nodeCtx, cVert.matrixDeps[j], True) == -1):
                if (len(inverseWeightMap[cVert.matrixDeps[j]]) == 0):
                    # do nothing, just use matrix 0 if not scaled
                    if data.scaleX > 4096:
                        targetInd,unused = LoadNodeToStack(data, nodes, cVert, 1, inverseWeightMap, cVert.matrixDeps[j], True, nodeCtx)
                        data.NSBCommands.append(0x3)
                        data.NSBCommands.append(0)
                        data.NSBCommands.append(0xB)
                        data.NSBCommands.append(0x26)
                        data.NSBCommands.append(len(nodes)-1)
                        data.NSBCommands.append(len(nodes)-1)
                        data.NSBCommands.append(0)
                        data.NSBCommands.append(targetInd)
                elif (len(inverseWeightMap[cVert.matrixDeps[j]]) == 1):
                    nodeInd=GetNodeIndex(inverseWeightMap[cVert.matrixDeps[j]][0][0],nodes)
                    targetInd,onStack = LoadNodeToStack(data, nodes, cVert, j, inverseWeightMap, nodeInd, False, nodeCtx)
                    if (data.scaleX > 4096):
                        if (onStack == False):
                            data.NSBCommands.append(0x3)
                            data.NSBCommands.append(targetInd)
                        data.NSBCommands.append(0xB)
                        data.NSBCommands.append(0x26)
                        data.NSBCommands.append(len(nodes)-1)
                        data.NSBCommands.append(len(nodes)-1)
                        data.NSBCommands.append(0)
                        targetInd,unused = LoadNodeToStack(data, nodes, cVert, 1, inverseWeightMap, cVert.matrixDeps[j], True, nodeCtx)
                        data.NSBCommands.append(targetInd)
                else:
                    for name,weight in inverseWeightMap[cVert.matrixDeps[j]]:
                        nodeInd=GetNodeIndex(name,nodes)
                        LoadNodeToStack(data, nodes, cVert, j, inverseWeightMap, nodeInd, False, nodeCtx)
                    targetInd,unused = LoadNodeToStack(data, nodes, cVert, j, inverseWeightMap, cVert.matrixDeps[j], True, nodeCtx)
                    if (targetInd == -1):
                        print("WHY")
                    data.NSBCommands.append(0x09)
                    data.NSBCommands.append(targetInd)
                    data.NSBCommands.append(len(inverseWeightMap[cVert.matrixDeps[j]]))
                    for name,weight in inverseWeightMap[cVert.matrixDeps[j]]:
                        nodeInd1 = GetNodeIndex(name,nodes)
                        nodeInd2 = FindNode(nodeCtx, nodeInd1, False)
                        data.NSBCommands.append(nodeInd2)
                        data.NSBCommands.append(nodeInd1) # inverse matrix
                        data.NSBCommands.append(weight)
                    if data.scaleX > 4096:
                        data.NSBCommands.append(0xB)
                        data.NSBCommands.append(0x26)
                        data.NSBCommands.append(len(nodes)-1)
                        data.NSBCommands.append(len(nodes)-1)
                        data.NSBCommands.append(0)
                        data.NSBCommands.append(targetInd)
        
        if (data.modelVerts[i].materialInd != currMat):
            currMat = cVert.materialInd
            data.NSBCommands.append(0x4)
            data.NSBCommands.append(currMat)
            if (((mats[currMat].TEXIMAGE_PARAMS & 0xC0000000) >> 30) == 2):
                data.NSBCommands.append(0xC)
                data.NSBCommands.append(currMat) # material
                data.NSBCommands.append(0) # ?
                nodeCtx.curr_mtx = -1 # just in case tbh idk
            
        data.NSBCommands.append(0x5)
        data.NSBCommands.append(i)
        
        for j in range(len(cVert.verts)):
            if (len(inverseWeightMap[cVert.verts[j].sourceMatrix]) == 1):
                if (data.scaleX > 4096):
                    cVert.verts[j].targetMatrix = FindNode(nodeCtx, cVert.verts[j].sourceMatrix, True)
                else:
                    nodeInd = GetNodeIndex(inverseWeightMap[cVert.verts[j].sourceMatrix][0][0], nodes)
                    cVert.verts[j].targetMatrix = FindNode(nodeCtx, nodeInd, False)
            elif (len(inverseWeightMap[cVert.verts[j].sourceMatrix]) == 0):
                if (data.scaleX > 4096):
                    cVert.verts[j].targetMatrix = FindNode(nodeCtx, cVert.verts[j].sourceMatrix, True)
                else:
                    cVert.verts[j].targetMatrix = 0
            else:
                preVert = cVert.verts[j].sourceMatrix
                cVert.verts[j].targetMatrix = FindNode(nodeCtx, cVert.verts[j].sourceMatrix, True)
        
    data.NSBCommands.append(1) # END

def ConvertVerts(meshes, materials, nodes):
    data = NSBMDModelData()
    all_verts = []
    for mesh in meshes:
        all_verts += mesh.verts
    all_x = [a.x for a in all_verts]
    all_y = [a.y for a in all_verts]
    all_z = [a.z for a in all_verts]
    vert_maxX = max(all_x)
    vert_minX = min(all_x)
    vert_maxY = max(all_y)
    vert_minY = min(all_y)
    vert_maxZ = max(all_z)
    vert_minZ = min(all_z)
    vert_centerX = (vert_maxX+vert_minX)/2
    vert_centerY = (vert_maxY+vert_minY)/2
    vert_centerZ = (vert_maxZ+vert_minZ)/2
    
    recenterX = 0
    recenterY = 0
    recenterZ = 0
    rescaleX = 1
    rescaleY = 1
    rescaleZ = 1
    
    """if vert_maxX > max_pos or vert_minX < min_pos:
        recenterX = -vert_centerX
        vert_maxX += recenterX 
    if vert_maxY > max_pos or vert_minY < min_pos:
        recenterY = -vert_centerY
        vert_maxY += recenterY
    if vert_maxZ > max_pos or vert_minZ < min_pos:
        recenterZ = -vert_centerZ
        vert_maxZ += recenterZ"""
    
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
    
    vert_maxX = -99999999999999
    vert_minX = 99999999999999
    vert_maxY = -99999999999999
    vert_minY = 99999999999999
    vert_maxZ = -99999999999999
    vert_minZ = 99999999999999
    
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
            else:
                newVert.normx = round(cVert.normx * 511)
                newVert.normy = round(cVert.normy * 511)
                newVert.normz = round(cVert.normz * 511)
            
            if (len(cVert.weights) == 1):
                nodeInd = GetNodeIndex(cVert.weights[0][0],nodes)
                new_pos = nodes[nodeInd].inverseMatrix @ mathutils.Vector((cVert.x,cVert.y,cVert.z,1.0))
                newVert.x = int(round(new_pos.x * 4096))
                newVert.y = int(round(new_pos.y * 4096))
                newVert.z = int(round(new_pos.z * 4096))
                new_norm = nodes[nodeInd].inverseMatrix.to_3x3().inverted().transposed() @ mathutils.Vector((cVert.normx,cVert.normy,cVert.normz))
                newVert.normx = int(round(new_norm.x*511))
                newVert.normy = int(round(new_norm.y*511))
                newVert.normz = int(round(new_norm.z*511)) # kinda redundant but w/e
            else:
                newVert.x = int(round(cVert.x * 4096))
                newVert.y = int(round(cVert.y * 4096))
                newVert.z = int(round(cVert.z * 4096))
            
            vert_maxX = max(vert_maxX, newVert.x)
            vert_minX = min(vert_minX, newVert.x)
            vert_maxY = max(vert_maxY, newVert.y)
            vert_minY = min(vert_minY, newVert.y)
            vert_maxZ = max(vert_maxZ, newVert.z)
            vert_minZ = min(vert_minZ, newVert.z)
            
            newVert.u = int(round(cVert.u * 16 * mat.tex_width))
            newVert.v = int(round(cVert.v * 16 * mat.tex_height))
            
            if not cVert.weights in weightMap:
                weightMap[cVert.weights] = len(inverseWeightMap)
                inverseWeightMap.append(cVert.weights)
            
            newVert.sourceMatrix = weightMap[cVert.weights]
            
            if not newVert.sourceMatrix in vertData.matrixDeps:
                vertData.matrixDeps.append(newVert.sourceMatrix)
            
            vertList.append(newVert)
            
            i += 1
        
        vertData.verts = vertList
        # split if >26 weights
        # explanation: maximum of 4 weights per vertex, plus 1 for parent, and last one is internal scratch
        if (len(vertData.matrixDeps) > 26):
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
                    if (v1.sourceMatrix in vData.matrixDeps) and (v2.sourceMatrix in vData.matrixDeps) and (v3.sourceMatrix in vData.matrixDeps):
                        foundExisting = True
                        for k in range(0,3):
                            if (vertData.tris[i+k] in vData.vertConversion):
                                vData.tris.append(vData.vertConversion[vertData.tris[i+k]])
                            else:
                                vData.tris.append(len(vData.verts))
                                vData.vertConversion[vertData.tris[i+k]] = len(vData.verts)
                                newVert = NSBMDDataVert()
                                newVert.x = vertsAsArray[k].x
                                newVert.y = vertsAsArray[k].y
                                newVert.z = vertsAsArray[k].z
                                newVert.normx = vertsAsArray[k].normx
                                newVert.normy = vertsAsArray[k].normy
                                newVert.normz = vertsAsArray[k].normz
                                newVert.u = vertsAsArray[k].u
                                newVert.v = vertsAsArray[k].v
                                newVert.colr = vertsAsArray[k].colr
                                newVert.colg = vertsAsArray[k].colg
                                newVert.colb = vertsAsArray[k].colb
                                newVert.sourceMatrix = vertsAsArray[k].sourceMatrix
                                vData.verts.append(newVert)
                if (foundExisting):
                    continue
                # check for partial match
                closestMatch = -1
                closestMatchCount = -1
                for k in range(0,len(vertDatas)):
                    vData = vertDatas[k]
                    currMatchCount = 0
                    for v in vertsAsArray:
                        if v.sourceMatrix in vData.matrixDeps:
                            currMatchCount += 1
                    if (len(vData.matrixDeps)+(3-currMatchCount)<=26) and (currMatchCount > closestMatchCount):
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
                        newVert = NSBMDDataVert()
                        newVert.x = vertsAsArray[k].x
                        newVert.y = vertsAsArray[k].y
                        newVert.z = vertsAsArray[k].z
                        newVert.normx = vertsAsArray[k].normx
                        newVert.normy = vertsAsArray[k].normy
                        newVert.normz = vertsAsArray[k].normz
                        newVert.u = vertsAsArray[k].u
                        newVert.v = vertsAsArray[k].v
                        newVert.colr = vertsAsArray[k].colr
                        newVert.colg = vertsAsArray[k].colg
                        newVert.colb = vertsAsArray[k].colb
                        newVert.sourceMatrix = vertsAsArray[k].sourceMatrix
                        vData.verts.append(newVert)
                        if (not vertsAsArray[k].sourceMatrix in vData.matrixDeps):
                            vData.matrixDeps.append(vertsAsArray[k].sourceMatrix)
            
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
                    if (v1.sourceMatrix in vData.matrixDeps) and (v2.sourceMatrix in vData.matrixDeps) and (v3.sourceMatrix in vData.matrixDeps) and (v4.sourceMatrix in vData.matrixDeps):
                        foundExisting = True
                        for k in range(0,4):
                            if (vertData.quads[i+k] in vData.vertConversion):
                                vData.quads.append(vData.vertConversion[vertData.quads[i+k]])
                            else:
                                vData.quads.append(len(vData.verts))
                                vData.vertConversion[vertData.quads[i+k]] = len(vData.verts)
                                newVert = NSBMDDataVert()
                                newVert.x = vertsAsArray[k].x
                                newVert.y = vertsAsArray[k].y
                                newVert.z = vertsAsArray[k].z
                                newVert.normx = vertsAsArray[k].normx
                                newVert.normy = vertsAsArray[k].normy
                                newVert.normz = vertsAsArray[k].normz
                                newVert.u = vertsAsArray[k].u
                                newVert.v = vertsAsArray[k].v
                                newVert.colr = vertsAsArray[k].colr
                                newVert.colg = vertsAsArray[k].colg
                                newVert.colb = vertsAsArray[k].colb
                                newVert.sourceMatrix = vertsAsArray[k].sourceMatrix
                                vData.verts.append(newVert)
                if (foundExisting):
                    continue
                # check for partial match
                closestMatch = -1
                closestMatchCount = -1
                for k in range(0,len(vertDatas)):
                    vData = vertDatas[k]
                    currMatchCount = 0
                    for v in vertsAsArray:
                        if v.sourceMatrix in vData.matrixDeps:
                            currMatchCount += 1
                    if (len(vData.matrixDeps)+(4-currMatchCount)<=26) and (currMatchCount > closestMatchCount):
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
                        newVert = NSBMDDataVert()
                        newVert.x = vertsAsArray[k].x
                        newVert.y = vertsAsArray[k].y
                        newVert.z = vertsAsArray[k].z
                        newVert.normx = vertsAsArray[k].normx
                        newVert.normy = vertsAsArray[k].normy
                        newVert.normz = vertsAsArray[k].normz
                        newVert.u = vertsAsArray[k].u
                        newVert.v = vertsAsArray[k].v
                        newVert.colr = vertsAsArray[k].colr
                        newVert.colg = vertsAsArray[k].colg
                        newVert.colb = vertsAsArray[k].colb
                        newVert.sourceMatrix = vertsAsArray[k].sourceMatrix
                        vData.verts.append(newVert)
                        if (not vertsAsArray[k].sourceMatrix in vData.matrixDeps):
                            vData.matrixDeps.append(vertsAsArray[k].sourceMatrix)
            
            for vData in vertDatas:
                data.modelVerts.append(vData)
        else:
            data.modelVerts.append(vertData)
        
        j += 1
    
    max_pos = (8*4096)-1
    min_pos = -8*4096
    
    if vert_maxX > max_pos:
        rescaleX = vert_maxX / max_pos
    if vert_minX < min_pos and abs(vert_minX) > vert_maxX:
        rescaleX = vert_minX / min_pos
    if vert_maxY > max_pos:
        rescaleY = vert_maxY / max_pos
    if vert_minY < min_pos and abs(vert_minY) > vert_maxY:
        rescaleY = vert_minY / min_pos
    if vert_maxZ > max_pos:
        rescaleZ = vert_maxZ / max_pos
    if vert_minZ < min_pos and abs(vert_minZ) > vert_maxZ:
        rescaleZ = vert_minZ / min_pos
    
    rescaleX = max(rescaleX,rescaleY,rescaleZ)
    
    if (rescaleX < 1.0):
        rescaleX = 1.0
    
    data.scaleX = math.ceil(rescaleX*4096)
    rescaleX = data.scaleX / 4096
    
    if (rescaleX > 1.0):
        for i in range(len(data.modelVerts)):
            for j in range(len(data.modelVerts[i].verts)):
                data.modelVerts[i].verts[j].x = int(data.modelVerts[i].verts[j].x/rescaleX)
                data.modelVerts[i].verts[j].y = int(data.modelVerts[i].verts[j].y/rescaleX)
                data.modelVerts[i].verts[j].z = int(data.modelVerts[i].verts[j].z/rescaleX)
    
    # visibility commands, then matrix commands
    
    data.NSBCommands.append(2)
    data.NSBCommands.append(0)
    data.NSBCommands.append(1)
    
    ProcessNodes(data,nodes,inverseWeightMap, materials)
    
    return data