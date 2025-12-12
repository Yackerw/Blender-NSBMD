import bpy
from . import util

def WriteBones(f, convertedData):
    boneCount = 0
    # bone count
    util.write_short(f, "<", boneCount)
    # header size
    header_size_offs = f.tell()
    util.write_short(f, "<", 0)
    # this part size
    util.write_short(f, "<", 8)
    # offset to actual info ?
    util.write_short(f, "<", 0xC+(4*boneCount))
    # ?
    util.write_integer(f, "<", 0x17F)
    # hashes?
    i = 0
    while i < boneCount:
        util.write_integer(f, "<", 0)
        i += 1
    # another size...
    util.write_short(f, "<", 4)
    util.write_short(f, "<", 4 + (4*boneCount))
    bone_offses = []
    i = 0
    while i < boneCount:
        bone_offses.append(f.tell())
        util.write_integer(f, "<", 0)
    # TODO: write names and bone info; names need to be 16 aligned
    header_size = f.tell()-header_size_offs
    f.seek(header_size_offs)
    util.write_short(f, "<", header_size+2)
    f.seek(0, 2)

def WriteBMD(f, GXList, convertedData):
    util.write_integer(f, "<", 0x304C444D)
    # chunk size...fill in later...
    MDL0_size_offs = f.tell()
    util.write_integer(f, "<", 0)
    # model count
    util.write_short(f, "<", 1)
    # model offset, fill in later: relative to MDL0 size position in bytes
    model_offset_offs = f.tell()
    util.write_short(f, "<", 0)
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