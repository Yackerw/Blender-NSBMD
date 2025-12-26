import bpy
from . import util

class InfoBlock():
    def __init__(self):
        self.offsetOffsets = []
        self.hashOffsets = []

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
    # hashes...?
    i = 0
    while i < itemCount:
        infoOffsets.hashOffsets.append(f.tell())
        util.write_integer(f, "<", 0)
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

def WriteNodes(f, convertedData):
    nodeCount = 1
    nodeNames = []
    nodeNames.append("Model")
    infoStart = f.tell()
    infoOffsets = WriteInfoBlock(f, nodeCount, nodeNames)
    curr_offs = f.tell()
    f.seek(infoOffsets.offsetOffsets[0], 0)
    util.write_integer(f, "<", curr_offs-infoStart)
    f.seek(0, 2)
    # write no transform
    util.write_short(f, "<", 0x7)
    # necessary short
    util.write_short(f, "<", 0x1000)

def WriteCommands(f, commands):
    i = 0
    while i < len(commands):
        util.write_byte(f, "<", commands[i])
        i += 1
    util.write_aligned(f, 4)

def WriteMaterials(f):
    materialCount = 1
    texture_pairing_offs = f.tell()
    util.write_short(f, "<", 0) # texture pairing offset
    palette_pairing_offs = f.tell()
    util.write_short(f, "<", 0)
    # same info block as bones use
    # temp
    matNames = []
    matNames.append("Material")
    infoOffsets = WriteInfoBlock(f, materialCount, matNames)
    
    # write a dummy material
    curr_offs = f.tell()
    f.seek(infoOffsets.offsetOffsets[0], 0)
    util.write_integer(f, "<", curr_offs - texture_pairing_offs) # curiously, the offsets stored are relative to the texture pairing offset/first value in materials in general?
    f.seek(0, 2)
    
    # material outline:
    util.write_short(f, "<", 0) # dummy
    util.write_short(f, "<", 0x2C) # material length
    util.write_integer(f, "<", 0) # DIF_AMB register
    util.write_integer(f, "<", 0) # SPE_EMI register
    util.write_integer(f, "<", 0x1F0000) # POLYGON_ATTR value to be OR'd with; 31 alpha
    util.write_integer(f, "<", 0x3F1FF8FF) # POLYGON_ATTR value to be AND'd with to clear old values
    util.write_integer(f, "<", 0) # TEXIMAGE_PARAM bit16-19 and 30-31: 16-19 are repeat type, 30-31 are transformation mode
    util.write_integer(f, "<", 0xFFFFFFFF) # unknown
    util.write_integer(f, "<", 0x1FCE0000) # unknown
    util.write_short(f, "<", 0) # texture width
    util.write_short(f, "<", 0) # texture height
    util.write_integer(f, "<", 0x1000) # unknown: 1.0 in DS fixed point. a guess is texture matrix scale?
    util.write_integer(f, "<", 0x1000) # unknown: 1.0 in DS fixed point
    # note: gbatek implies a full texture matrix can be stored in here, but doesn't understand how or why. worth investigating
    
    curr_offs = f.tell()
    f.seek(texture_pairing_offs, 0)
    util.write_short(f, "<", curr_offs-texture_pairing_offs)
    util.write_short(f, "<", curr_offs-texture_pairing_offs)
    f.seek(0, 2)
    # :/
    WriteInfoBlock(f, 0, [])

def WriteVertexMesh(f, GXList):
    listStartOffs = f.tell()
    meshNameDummy = []
    meshNameDummy.append("Mesh")
    infoOffs = WriteInfoBlock(f, 1, meshNameDummy)
    curr_offs = f.tell()
    f.seek(infoOffs.offsetOffsets[0], 0)
    util.write_integer(f, "<", curr_offs-listStartOffs)
    f.seek(0, 2)
    
    vertexMeshStart = f.tell()
    util.write_short(f, "<", 0) # dummy
    util.write_short(f, "<", 0x10) # ? size of segment?
    util.write_integer(f, "<", 0xC) # ?? look into this value
    GXListOffs = f.tell()
    util.write_integer(f, "<", 0) # offset to GX command list
    util.write_integer(f, "<", len(GXList)*4) # GX command list size
    
    curr_offs = f.tell()
    f.seek(GXListOffs, 0)
    util.write_integer(f, "<", curr_offs-vertexMeshStart)
    f.seek(0, 2)
    i = 0
    while i < len(GXList):
        util.write_integer(f, "<", GXList[i])
        i += 1
    

def WriteBMD(f, GXList, convertedData):
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
    util.write_byte(f, "<", 1)
    # material count
    util.write_byte(f, "<", 1)
    # vertexmesh count
    util.write_byte(f, "<", 1)
    # ? do bone count again?
    util.write_short(f, "<", 1)
    # scale factor
    util.write_integer(f, "<", convertedData.scaleX)
    util.write_integer(f, "<", int(16777216 / convertedData.scaleX))
    # data counts (only for debugging, considering it uses draw lists?)
    util.write_short(f, "<", convertedData.vertCount)
    util.write_short(f, "<", convertedData.triCount + convertedData.quadCount)
    util.write_short(f, "<", convertedData.triCount)
    util.write_short(f, "<", convertedData.quadCount)
    util.write_short(f, "<", convertedData.boundsX)
    util.write_short(f, "<", convertedData.boundsY)
    util.write_short(f, "<", convertedData.boundsZ)
    util.write_short(f, "<", convertedData.boundsXWidth)
    util.write_short(f, "<", convertedData.boundsHeight)
    util.write_short(f, "<", convertedData.boundsZWidth)
    util.write_integer(f, "<", 4096)
    util.write_integer(f, "<", 4096)
    
    WriteNodes(f, convertedData)
    
    curr_offs = f.tell()
    f.seek(render_list_offs, 0)
    util.write_integer(f, "<", curr_offs-model_size_offs)
    f.seek(0, 2)
    WriteCommands(f, convertedData.NSBCommands)
    curr_offs = f.tell()
    f.seek(material_offs_offs, 0)
    util.write_integer(f, "<", curr_offs-model_size_offs)
    f.seek(0, 2)
    WriteMaterials(f) # TODO: MATERIALS
    curr_offs = f.tell()
    f.seek(vertexMesh_offs_offs, 0)
    util.write_integer(f, "<", curr_offs-model_size_offs)
    f.seek(0, 2)
    WriteVertexMesh(f, GXList)
    #curr_offs = f.tell()
    #f.seek(inverse_matrices_offs, 0)
    #util.write_integer(f, "<", curr_offs-model_size_offs)
    #f.seek(0,2)
    #WriteInverseMatrices(f, convertedData)
    
    curr_offs = f.tell()
    
    f.seek(model_size_offs, 0)
    util.write_integer(f, "<", curr_offs - model_size_offs)
    
    f.seek(MDL0_size_offs, 0)
    util.write_integer(f, "<", curr_offs-MDL0_size_offs)
    f.seek(0, 2)
    

def WriteFile(GXList, convertedData, filepath):
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
    
    WriteBMD(f, GXList, convertedData)
    
    curr_offs = f.tell()
    f.seek(file_size_offs)
    util.write_integer(f, "<", curr_offs)
    f.seek(0,2)
    
    f.close()