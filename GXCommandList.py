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
        self.prevPosx = 0.5
        self.prevPosy = 0.5
        self.prevPosz = 0.5
        self.prevColor = 0.5
        self.prevMtx = -1
        self.prevColor = 0.5
        self.commandInd = 0
        self.commandCount = 0
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
                self.commands.append((diffX & 0x3FF) | ((diffY & 0x3FF) << 10) | ((diffZ & 0x3FF) << 20))
            else:
                self.commands[self.commandInd] |= GXFIFOCommands.CMD_VTX_16 << commandShift
                self.commands.append((arg1 & 0xFFFF) | ((arg2 & 0xFFFF) << 16))
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
        
        if cmd == GXCommands.CMD_TRI or cmd == GXCommands.CMD_TRISTRIP or cmd == GXCommands.CMD_QUAD or cmd == GXCommands.CMD_QUADSTRIP:
            self.prevUV = 0.5 # we pass in ints, 0.5 for uninitialized
            self.prevNorm = 0.5
            self.prevPosx = 0.5
            self.prevPosy = 0.5
            self.prevPosz = 0.5
            self.prevColor = 0.5
            self.prevMtx = -1
            self.prevColor = 0.5
        
        self.commandCount += 1
        if (self.commandCount == 4):
            self.commandCount = 0
            self.commandInd = len(self.commands)
            self.commands.append(0)

def ConvertToGXList(vertList, triList, quadList, useColor):
    
    GXList = GXWriter()
    
    i = 0
    # TODO: strips
    if (len(triList) > 0):
        GXList.PushCommand(GXCommands.CMD_TRI)
        while (i < len(triList)):
            GXList.PushCommand(GXCommands.CMD_MTX, vertList[triList[i]].targetMatrix, 0, 0)
            GXList.PushCommand(GXCommands.CMD_TEXCOORD, vertList[triList[i]].u, vertList[triList[i]].v, 0)
            GXList.PushCommand(GXCommands.CMD_NORMAL, vertList[triList[i]].normx, vertList[triList[i]].normy, vertList[triList[i]].normz)
            GXList.PushCommand(GXCommands.CMD_POS, vertList[triList[i]].x, vertList[triList[i]].y, vertList[triList[i]].z)
    
    if (len(quadList) > 0):
        GXList.PushCommand(GXCommands.CMD_QUAD)
        while (i < len(quadList)):
            GXList.PushCommand(GXCommands.CMD_MTX, vertList[quadList[i]].targetMatrix, 0, 0)
            GXList.PushCommand(GXCommands.CMD_TEXCOORD, vertList[quadList[i]].u, vertList[quadList[i]].v, 0)
            GXList.PushCommand(GXCommands.CMD_NORMAL, vertList[quadList[i]].normx, vertList[quadList[i]].normy, vertList[quadList[i]].normz)
            GXList.PushCommand(GXCommands.CMD_POS, vertList[quadList[i]].x, vertList[quadList[i]].y, vertList[quadList[i]].z)
    
    return GXList.commands