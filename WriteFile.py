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

def WriteBones(f, convertedData):
    boneCount = 0
    infoOffsets = WriteInfoBlock(f, boneCount, [])

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
    

def WriteBMD(f, GXList, convertedData):
    util.write_integer(f, "<", 0x304C444D)
    # chunk size...fill in later...
    MDL0_size_offs = f.tell()
    util.write_integer(f, "<", 0)
    # model count
    util.write_short(f, "<", 1)
    # model offset, fill in later: relative to MDL0 size position in bytes
    model_offset_offs = f.tell()
    util.write_short(f, "<", 4) # TODO: change if we add multiple meshes?
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
    util.write_byte(f, "<", 0)
    # material count
    util.write_byte(f, "<", 1)
    # vertexmesh count
    util.write_byte(f, "<", 1)
    # ? do bone count again?
    util.write_short(f, "<", 0)
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
    
    WriteBones(f, convertedData)
    
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
    
    f.close()