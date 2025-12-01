import bpy
from enum import Enum

class GXCommands(Enum):
    CMD_TEXCOORD = 1
    CMD_NORMAL = 2
    CMD_POS = 3
    CMD_MTX = 4
    CMD_TRI = 5
    CMD_TRISTRIP = 6
    CMD_QUAD = 7
    CMD_QUADSTRIP = 8
    CMD_SCALE = 9
    CMD_COLOR = 10
    CMD_TRANSLATE = 11

class GXFIFOCommands(Enum):
    CMD_TEXCOORD = 1

class GXWriter():
    def __init__(self):
        self.commands = []
        self.prevUV = 0.5 # we pass in ints, 0.5 for uninitialized
        self.prevNorm = 0
        self.prevPosx = 0.5
        self.prevPosy = 0.5
        self.prevPosz = 0.5
        self.prevColor = 0.5
        self.prevMtx = -1
        self.commandInd = 0
        self.commandCount = 0
        self.commands.append(0)
        
    def PushCommand(self, cmd, arg1, arg2, arg3):
        commandShift = self.commandCount * 8
        if cmd == GXCommands.CMD_TEXCOORD:
            if self.prevUV == arg1:
                return
            self.commands[self.commandInd] = GXFIFOCommands.CMD_TEXCOORD << commandShift
            self.commands.append(arg1)
            self.prevUV = arg1

def ConvertToGXList(vertList, triList, quadList):
    vert_maxX = -99999999
    vert_maxY = -99999999
    vert_maxZ = -99999999
    vert_minX = 99999999
    vert_minY = 99999999
    vert_minZ = 99999999
    
    i = 0
    while (i < len(vertList)):
        curr_pos = vertList[i].Pos
        if (vert_maxX < curr_pos.x):
            vert_maxX = curr_pos.x
        if (vert_minX > curr_pos.x):
            vert_minX = curr_pos.x
        if (vert_maxY < curr_pos.y):
            vert_maxY = curr_pos.y
        if (vert_minY > curr_pos.y):
            vert_minY = curr_pos.y
        if (vert_maxZ < curr_pos.z):
            vert_maxZ = curr_pos.z
        if (vert_minZ > curr_pos.z):
            vert_minZ = curr_pos.z
        
        i = i + 1
    vert_centerX = (maxX+minX)/2
    vert_centerY = (maxY+minY)/2
    vert_centerZ = (maxZ+minZ)/2
    
    recenterX = 0
    recenterY = 0
    recenterZ = 0
    rescaleX = 1
    rescaleY = 1
    rescaleZ = 1
    
    max_pos = 32767/4096
    min_pos = -8
    
    if vert_maxX > max_pos or vert_minX < min_pos:
        recenterX = -vert_centerX
    if vert_maxY > max_pos or vert_minY < min_pos:
        recenterY = -vert_centerY
    if vert_maxZ > max_pos or vert_minZ < min_pos:
        recenterZ = -vert_centerZ
    
    if vert_maxX > max_pos:
        rescaleX = vert_maxX / max_pos
    if vert_maxY > max_pos:
        recenterY = vert_maxY / max_pos
    if vert_maxZ > max_pos:
        recenterZ = vert_maxZ / max_pos
    
    i = 0
    while (i < len(triList)):
        