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
    CMD_COLOR = 9

class GXFIFOCommands(Enum):
    CMD_TEXCOORD = 0x22
    CMD_NORMAL = 0x21
    CMD_COLOR = 0x20
    CMD_VTX_16 = 0x23
    CMD_VTX_DIFF = 0x28
    CMD_MTX_RESTORE = 0x14
    CMD_BEGINVTX = 0x40
    CMD_NOP = 0

class GXWriter():
    def __init__(self):
        self.commands = []
        self.prevUV = 0.5 # we pass in ints, 0.5 for uninitialized
        self.prevNorm = 0.5
        self.prevPosx = 0xFFFFFF
        self.prevPosy = 0xFFFFFF
        self.prevPosz = 0xFFFFFF
        self.prevColor = 0.5
        self.prevMtx = -1
        self.commandInd = 0
        self.commandCount = 0
        self.prevColor = 0.5
        self.dirtyScale = 1
        self.dirtyTrans = 1
        self.commands.append(0)
        
    def PushCommand(self, cmd, arg1, arg2, arg3):
        commandShift = self.commandCount * 8
        if cmd == GXCommands.CMD_TEXCOORD:
            newUV = (arg1 & 0xFFFF) | ((arg2 & 0xFFFF) << 16)
            if self.prevUV == newUV:
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_TEXCOORD << commandShift
            self.commands.append(newUV)
            self.prevUV = newUV
        elif cmd == GXCommands.CMD_NORMAL:
            newNorm = (arg1 & 0x3FF) | ((arg2 & 0x3FF) << 10) | ((arg3 & 0x3FF) << 20)
            if self.prevNorm == newNorm:
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_NORMAL << commandShift
            self.commands.append(newNorm)
            self.prevNorm = newNorm
        elif cmd == GXCommands.CMD_POS:
            diffX = arg1 - self.prevPosx
            diffY = arg2 - self.prevPosy
            diffZ = arg3 - self.prevPosZ
            if (abs(diffX) < 512 and abs(diffY) and abs(diffZ)):
                self.commands[self.commandInd] |= GXFIFOCommands.CMD_VTX_DIFF << commandShift
                self.commands.append((diffX & 0x3FF) | ((diffY & 0x3FF) << 10) | ((diffZ & 0x3FF) << 20)
            else:
                self.commands[self.commandInd] |= GXFIFOCommands.CMD_VTX_16 << commandShift
                self.commands.append((arg1 & 0xFFFF) | ((arg2 & 0xFFFF) << 16)
                self.commands.append((arg3 & 0xFFFF))
            
            self.prevPosx = arg1
            self.prevPosy = arg2
            self.prevPosz = arg3
        elif cmd == GXCommands.CMD_MTX:
            if (self.prevMtx == arg1):
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_MTX_RESTORE << commandShift
            self.commands.append(arg1)
            self.prevMtx = arg1
            self.prevNorm = 0.5 # invalidate normal as well
        elif cmd == GXCommands.CMD_TRI:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX << commandShift
            self.commands.append(0)
        elif cmd == GXCommands.CMD_TRISTRIP:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX << commandShift
            self.commands.append(2)
        elif cmd == GXCommands.CMD_QUAD:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX << commandShift
            self.commands.append(1)
        elif cmd == GXCommands.CMD_QUADSTRIP:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX << commandShift
            self.commands.append(3)
        elif cmd == GXCommands.CMD_COLOR:
            newColor = (arg1 & 0x1F) | ((arg2 & 0x1F) << 5) | ((arg3 & 0x1F) << 10)
            if self.prevColor == newColor:
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_COLOR << commandShift
            self.commands.append(newColor)
            self.prevColor = newColor
        else:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_NOP << commandShift
        
        self.commandCount += 1
        if (self.commandCount == 4):
            self.commandCount = 0
            self.commandInd = len(self.commands)
            self.commands.append(0)

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
    
    max_pos = 32767
    min_pos = -32768
    
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
        