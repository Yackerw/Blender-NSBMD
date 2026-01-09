import bpy
from . import util

class InfoBlock():
    def __init__(self):
        self.offsetOffsets = []

class TreeNode():
    def __init__(self):
        self.bit = 0
        self.left = 0
        self.right = 0

def ExtractBit(bitIndex,byteArray):
    currByteIndex = int(bitIndex/8)
    currBitIndex = bitIndex % 8
    if (currByteIndex >= len(byteArray)):
        return 0
    return (byteArray[currByteIndex] >> currBitIndex) & 1

def FindPatriciaBit(names,testName,dontTestList):
    for i in range(0,127):
        currBit = ExtractBit(i, testName)
        for j in range(0,len(names)):
            if dontTestList[j] == True:
                continue
            currName = names[j]
            otherBit = ExtractBit(i, currName)
            if otherBit != currBit:
                for k in range(0,len(names)):
                    if dontTestList[k] == True or k==j:
                        continue
                    currName = names[k]
                    otherBit2 = ExtractBit(i, currName)
                    if otherBit2 != otherBit:
                        if (otherBit2 == 0):
                            return i,k,j
                        else:
                            return i,j,k
    # we failed to find a good two way split, just make one
    for i in range(0,127):
        currBit = ExtractBit(i, testName)
        for j in range(0,len(names)):
            if dontTestList[j] == True:
                continue
            currName = names[j]
            otherBit = ExtractBit(i, currName)
            if otherBit != currBit:
                if otherBit == 0:
                    return i,j,-1
                else:
                    return i,-1,j
    return 0, -1, -1 # MUST be the end of the tree

def CreatePatriciaTree(names):
    for i in range(0,len(names)):
        name = names[i]
        for j in range(i+1,len(names)):
            name2 = names[j]
            if name==name2:
                # identical name!
                def draw(self, context):
                    self.layout.label(text="Two identical names were found in tree generation! Check your bones, textures, and materials for duplicate names.")
                bpy.context.window_manager.popup_menu(draw_func=draw, title="NSBMD Exporter", icon="ERROR")
                raise Exception("Invalid patricia tree")
                
    patricia = []
    newNames = []
    foundNames = []
    for i in range(0,len(names)):
        foundNames.append(False)
        currName = names[i]
        if (len(currName) >= 16):
            currName = currName[:15]
        newNames.append(currName.encode('ascii'))
    for i in range(0,len(names)):
        foundNames[i] = True
        bit,left,right = FindPatriciaBit(newNames,newNames[i],foundNames)
        newNode = TreeNode()
        newNode.bit = bit
        newNode.left = left
        newNode.right = right
        patricia.append(newNode)
        foundNames[left] = True
        foundNames[right] = True
    return patricia

def WriteInfoBlock(f, itemCount, names):
    infoOffsets = InfoBlock()
    
    util.write_byte(f, "<", 0)
    util.write_byte(f, "<", itemCount)
    # header size
    headerSizeOffset = f.tell()
    util.write_short(f, "<", 0)
    # ?
    util.write_short(f, "<", 8)
    # offset to actual info ?
    util.write_short(f, "<", 0xC+(4*itemCount))
    # ?
    util.write_integer(f, "<", 0x17F)
    # patricia tree
    patricia = CreatePatriciaTree(names)
    i = 0
    while i < itemCount:
        util.write_byte(f, "<", patricia[i].bit)
        util.write_byte(f, "<", patricia[i].left+1)
        util.write_byte(f, "<", patricia[i].right+1)
        util.write_byte(f, "<", i)
        i += 1
    # more sizes?
    util.write_short(f, "<", 4)
    util.write_short(f, "<", 4 + (4*itemCount))
    i = 0
    while i < itemCount:
        infoOffsets.offsetOffsets.append(f.tell())
        util.write_integer(f, "<", 0)
        i += 1
    
    # write names
    i = 0
    while i < itemCount:
        util.write_string_set_length(f, names[i], 16)
        i += 1
    
    # write header size
    header_size = f.tell()-headerSizeOffset
    f.seek(headerSizeOffset, 0)
    util.write_short(f, "<", header_size+2)
    f.seek(0, 2)
    
    return infoOffsets;

def WriteNodes(f, nodes):
    nodeCount = len(nodes)
    nodeNames = []
    for node in nodes:
        nodeNames.append(node.name)
    infoStart = f.tell()
    infoOffsets = WriteInfoBlock(f, nodeCount, nodeNames)
    i = 0
    for node in nodes:
        curr_offs = f.tell()
        f.seek(infoOffsets.offsetOffsets[i], 0)
        util.write_integer(f, "<", curr_offs-infoStart)
        f.seek(0, 2)
        
        if node.validTransform == False:
            # write no transform
            util.write_short(f, "<", 0x7)
            # necessary short
            util.write_short(f, "<", 0x1000)
        else:
            flagValue = 0x4 # disable scale
            if node.position.x == 0 and node.position.y == 0 and node.position.z == 0:
                flagValue |= 0x1 # disable translation
            # i'm not gonna bother with pivots tbh
            if node.rotation[0][0] == 4096 and node.rotation[1][1] == 4096 and node.rotation[2][2] == 4096: # identity matrix
                flagValue |= 0x2 # disable rotation
            util.write_short(f, "<", flagValue)
            util.write_signed_short(f, "<", int(node.rotation[0][0]))
            if (flagValue & 0x1) == 0:
                util.write_signed_integer(f, "<", int(node.position.x))
                util.write_signed_integer(f, "<", int(node.position.y))
                util.write_signed_integer(f, "<", int(node.position.z))
            if (flagValue & 0x2) == 0:
                for j in range(0,3):
                    for k in range(0,3):
                        if j == 0 and k == 0:
                            continue
                        util.write_signed_short(f, "<", int(node.rotation[k][j]))
            
        i += 1

def WriteCommands(f, commands):
    i = 0
    while i < len(commands):
        util.write_byte(f, "<", commands[i])
        i += 1
    util.write_aligned(f, 4)

def WriteMaterials(f, materials):
    materialCount = len(materials)
    texture_pairing_offs = f.tell()
    util.write_short(f, "<", 0) # texture pairing offset
    palette_pairing_offs = f.tell()
    util.write_short(f, "<", 0)
    # same info block as bones use
    # temp
    matNames = []
    for mat in materials:
        matNames.append(mat.name)
    infoOffsets = WriteInfoBlock(f, materialCount, matNames)
    
    curr_offs = f.tell()
    f.seek(texture_pairing_offs, 0)
    util.write_short(f, "<", curr_offs-texture_pairing_offs)
    f.seek(0, 2)
    
    # get unique texture count
    # TODO: open nsbtx and order these the same as the nsbtx
    textures = {}
    textureCount = 0
    for mat in materials:
        if not mat.texture_name in textures:
            textures[mat.texture_name] = textureCount
            textureCount += 1
    # :/
    paletteNames = []
    texNames = []
    for key, value in textures.items():
        paletteNames.append(key+"_pl")
        texNames.append(key)
    texInfo = WriteInfoBlock(f, textureCount, texNames)
    curr_offs = f.tell()
    f.seek(texture_pairing_offs+2, 0)
    util.write_short(f, "<", curr_offs-texture_pairing_offs)
    f.seek(0, 2)
    paletteInfo = WriteInfoBlock(f, textureCount, paletteNames)
    j = 0
    for key, value in textures.items():
        curr_offs = f.tell()
        matUsedCount = 0
        for i in range(0,len(materials)):
            if materials[i].texture_name == key:
                print(key)
                util.write_byte(f, "<", i)
                matUsedCount += 1
        f.seek(texInfo.offsetOffsets[j])
        util.write_integer(f, "<", curr_offs-texture_pairing_offs | (matUsedCount << 16)) # 1 << 16 = count of items
        f.seek(0, 2)
        j += 1
    j = 0
    for key, value in textures.items():
        curr_offs = f.tell()
        matUsedCount = 0
        for i in range(0,len(materials)):
            if materials[i].texture_name == key:
                util.write_byte(f, "<", i)
                matUsedCount += 1
        f.seek(paletteInfo.offsetOffsets[j])
        util.write_integer(f, "<", curr_offs-texture_pairing_offs | (matUsedCount << 16)) # 1 << 16 = count of items
        f.seek(0, 2)
        j += 1
    util.write_aligned(f, 4)
    
    i = 0
    for mat in materials:
        curr_offs = f.tell()
        f.seek(infoOffsets.offsetOffsets[i], 0)
        util.write_integer(f, "<", curr_offs - texture_pairing_offs) # curiously, the offsets stored are relative to the texture pairing offset/first value in materials in general?
        f.seek(0, 2)
        util.write_short(f, "<", 0) # dummy
        util.write_short(f, "<", 0x2C) # material length
        util.write_integer(f, "<", mat.DIF_AMB) # DIF_AMB register
        util.write_integer(f, "<", mat.SPE_EMI) # SPE_EMI register
        util.write_integer(f, "<", mat.POLY_ATTR_OR) # POLYGON_ATTR value to be OR'd with; 31 alpha, front faces
        util.write_integer(f, "<", mat.POLY_ATTR_MASK) # POLYGON_ATTR value to be AND'd with to clear old values
        util.write_integer(f, "<", mat.TEXIMAGE_PARAMS) # TEXIMAGE_PARAM bit16-19 and 30-31: 16-19 are repeat type, 30-31 are transformation mode
        util.write_integer(f, "<", 0xFFFFFFFF) # unknown
        util.write_integer(f, "<", 0x1FCE0000) # unknown
        util.write_short(f, "<", mat.tex_width) # texture width
        util.write_short(f, "<", mat.tex_height) # texture height
        util.write_integer(f, "<", 0x1000) # unknown: 1.0 in DS fixed point. a guess is texture matrix scale?
        util.write_integer(f, "<", 0x1000) # unknown: 1.0 in DS fixed point
        i += 1
    
    
    # note: gbatek implies a full texture matrix can be stored in here, but doesn't understand how or why. worth investigating

def WriteVertexMesh(f, GXLists, mats):
    listStartOffs = f.tell()
    meshNames = []
    for i in range(0,len(GXLists)):
        meshNames.append(mats[i].name)
    infoOffs = WriteInfoBlock(f, len(GXLists), meshNames)
    vertexMeshStart = f.tell()
    
    j = 0
    GXListOffsets = []
    for GXList in GXLists:
        curr_offs = f.tell()
        f.seek(infoOffs.offsetOffsets[j], 0)
        util.write_integer(f, "<", curr_offs-listStartOffs)
        f.seek(0, 2)
        
        util.write_short(f, "<", 0) # dummy
        util.write_short(f, "<", 0x10) # ? size of segment?
        util.write_integer(f, "<", 0xC) # ??
        GXListOffsets.append(f.tell())
        util.write_integer(f, "<", 0) # offset to GX command list
        util.write_integer(f, "<", len(GXList)*4) # GX command list size
        j += 1
    
    j = 0
    for GXList in GXLists:
        curr_offs = f.tell()
        f.seek(GXListOffsets[j], 0)
        util.write_integer(f, "<", (curr_offs-GXListOffsets[j])+0x8)
        f.seek(0, 2)
        i = 0
        while i < len(GXList):
            util.write_integer(f, "<", GXList[i])
            i += 1
        j += 1

def WriteInverseMatrices(f, nodes):
    for node in nodes:
        for i in range(0,4):
            for j in range(0,3):
                util.write_signed_integer(f, "<", int(node.inverseMatrix[j][i]))
        # UPGRADE NOTE: if scale is added to bones, you will have to remove scale from this next matrix!
        for i in range(0,3):
            for j in range(0,3):
                util.write_signed_integer(f, "<", int(node.inverseMatrix[j][i]))
    

def WriteBMD(f, GXLists, convertedData, materials, nodes):
    util.write_integer(f, "<", 0x304C444D)
    # chunk size...fill in later...
    MDL0_size_offs = f.tell()
    util.write_integer(f, "<", 0)
    # i hate these info blocks
    info_block_start = f.tell()
    nameTest = []
    nameTest.append("Model")
    infoOffs = WriteInfoBlock(f, 1, nameTest)
    curr_offs = f.tell()
    f.seek(infoOffs.offsetOffsets[0], 0)
    util.write_integer(f, "<", (curr_offs-MDL0_size_offs)+4)
    f.seek(0, 2)
    # model size
    model_size_offs = f.tell()
    util.write_integer(f, "<", 0)
    # render command list offset, all these offsets are relative to "model size"
    render_list_offs = f.tell()
    util.write_integer(f, "<", 0)
    # material offset
    material_offs_offs = f.tell()
    util.write_integer(f, "<", 0)
    # offset to "VertexMesh" value; great name, gbatek
    vertexMesh_offs_offs = f.tell()
    util.write_integer(f, "<", 0)
    # offset to inverse bone matrices
    inverse_matrices_offs = f.tell()
    util.write_integer(f, "<", 0)
    # ?
    util.write_byte(f, "<", 0)
    util.write_byte(f, "<", 0)
    util.write_byte(f, "<", 0)
    # bone count. fill out once we get bones!
    util.write_byte(f, "<", len(nodes))
    # material count
    util.write_byte(f, "<", 1)
    # vertexmesh count
    util.write_byte(f, "<", 1)
    # ? do bone count again?
    util.write_short(f, "<", len(nodes))
    # scale factor
    util.write_integer(f, "<", convertedData.scaleX)
    util.write_integer(f, "<", int(16777216 / convertedData.scaleX))
    # data counts (only for debugging, considering it uses draw lists?)
    util.write_short(f, "<", convertedData.vertCount)
    util.write_short(f, "<", convertedData.triCount + convertedData.quadCount)
    util.write_short(f, "<", convertedData.triCount)
    util.write_short(f, "<", convertedData.quadCount)
    util.write_signed_short(f, "<", convertedData.boundsX)
    util.write_signed_short(f, "<", convertedData.boundsY)
    util.write_signed_short(f, "<", convertedData.boundsZ)
    util.write_signed_short(f, "<", convertedData.boundsXWidth)
    util.write_signed_short(f, "<", convertedData.boundsHeight)
    util.write_signed_short(f, "<", convertedData.boundsZWidth)
    util.write_integer(f, "<", 4096)
    util.write_integer(f, "<", 4096)
    
    WriteNodes(f, nodes)
    
    curr_offs = f.tell()
    f.seek(render_list_offs, 0)
    util.write_integer(f, "<", curr_offs-model_size_offs)
    f.seek(0, 2)
    WriteCommands(f, convertedData.NSBCommands)
    curr_offs = f.tell()
    f.seek(material_offs_offs, 0)
    util.write_integer(f, "<", curr_offs-model_size_offs)
    f.seek(0, 2)
    WriteMaterials(f, materials)
    curr_offs = f.tell()
    f.seek(vertexMesh_offs_offs, 0)
    util.write_integer(f, "<", curr_offs-model_size_offs)
    f.seek(0, 2)
    WriteVertexMesh(f, GXLists, materials)
    curr_offs = f.tell()
    f.seek(inverse_matrices_offs, 0)
    util.write_integer(f, "<", curr_offs-model_size_offs)
    f.seek(0,2)
    WriteInverseMatrices(f, nodes)
    
    curr_offs = f.tell()
    
    f.seek(model_size_offs, 0)
    util.write_integer(f, "<", curr_offs - model_size_offs)
    
    f.seek(MDL0_size_offs, 0)
    util.write_integer(f, "<", (curr_offs-MDL0_size_offs)+4)
    f.seek(0, 2)
    

def WriteFile(GXLists, convertedData, materials, nodes, filepath):
    f = open(filepath, "wb")
    # simple header stuff
    util.write_integer(f, "<", 0x30444d42)
    util.write_short(f, "<", 0xFEFF)
    util.write_short(f, "<", 2)
    # file size; fill in later
    file_size_offs = f.tell()
    util.write_integer(f, "<", 0)
    # header size
    util.write_short(f, "<", 0x10)
    # 1 = MDL only, 2 = TEX as well
    util.write_short(f, "<", 1)
    # offset to BMD0
    util.write_integer(f, "<", 0x18)
    # offset to TEX0
    util.write_integer(f, "<", 0)
    
    WriteBMD(f, GXLists, convertedData, materials, nodes)
    
    curr_offs = f.tell()
    f.seek(file_size_offs)
    util.write_integer(f, "<", curr_offs)
    f.seek(0,2)
    
    f.close()