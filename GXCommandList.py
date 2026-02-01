import bpy
from enum import Enum
from . import Stripping

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
        self.prevColor = 0.5
        self.commandInd = 0
        self.commandCount = 0
        self.commands.append(0)
        
    def PushCommand(self, cmd, arg1, arg2, arg3):
        commandShift = self.commandCount * 8
        if cmd == GXCommands.CMD_TEXCOORD.value:
            newUV = (arg1 & 0xFFFF) | ((arg2 & 0xFFFF) << 16)
            if self.prevUV == newUV:
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_TEXCOORD.value << commandShift
            self.commands.append(newUV)
            self.prevUV = newUV
        elif cmd == GXCommands.CMD_NORMAL.value:
            newNorm = (arg1 & 0x3FF) | ((arg2 & 0x3FF) << 10) | ((arg3 & 0x3FF) << 20)
            if self.prevNorm == newNorm:
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_NORMAL.value << commandShift
            self.commands.append(newNorm)
            self.prevNorm = newNorm
        elif cmd == GXCommands.CMD_POS.value:
            diffX = arg1 - self.prevPosx
            diffY = arg2 - self.prevPosy
            diffZ = arg3 - self.prevPosz
            if (abs(diffX) < 512 and abs(diffY) < 512 and abs(diffZ) < 512):
                self.commands[self.commandInd] |= GXFIFOCommands.CMD_VTX_DIFF.value << commandShift
                self.commands.append((diffX & 0x3FF) | ((diffY & 0x3FF) << 10) | ((diffZ & 0x3FF) << 20))
            else:
                self.commands[self.commandInd] |= GXFIFOCommands.CMD_VTX_16.value << commandShift
                self.commands.append((arg1 & 0xFFFF) | ((arg2 & 0xFFFF) << 16))
                self.commands.append((arg3 & 0xFFFF))
            
            self.prevPosx = arg1
            self.prevPosy = arg2
            self.prevPosz = arg3
        elif cmd == GXCommands.CMD_MTX.value:
            if (self.prevMtx == arg1):
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_MTX_RESTORE.value << commandShift
            self.commands.append(arg1)
            self.prevMtx = arg1
            self.prevNorm = 0.5 # invalidate normal as well
        elif cmd == GXCommands.CMD_TRI.value:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX.value << commandShift
            self.commands.append(0)
        elif cmd == GXCommands.CMD_TRISTRIP.value:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX.value << commandShift
            self.commands.append(2)
        elif cmd == GXCommands.CMD_QUAD.value:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX.value << commandShift
            self.commands.append(1)
        elif cmd == GXCommands.CMD_QUADSTRIP.value:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_BEGINVTX.value << commandShift
            self.commands.append(3)
        elif cmd == GXCommands.CMD_COLOR.value:
            newColor = (arg1 & 0x1F) | ((arg2 & 0x1F) << 5) | ((arg3 & 0x1F) << 10)
            if self.prevColor == newColor:
                return
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_COLOR.value << commandShift
            self.commands.append(newColor)
            self.prevColor = newColor
        else:
            self.commands[self.commandInd] |= GXFIFOCommands.CMD_NOP.value << commandShift
        
        if cmd == GXCommands.CMD_TRI.value or cmd == GXCommands.CMD_TRISTRIP.value or cmd == GXCommands.CMD_QUAD.value or cmd == GXCommands.CMD_QUADSTRIP.value:
            self.prevUV = 0.5 # we pass in ints, 0.5 for uninitialized
            self.prevNorm = 0.5
            self.prevPosx = 0xFFFFFF
            self.prevPosy = 0xFFFFFF
            self.prevPosz = 0xFFFFFF
            self.prevColor = 0.5
            self.prevMtx = -1
            self.prevColor = 0.5
        
        self.commandCount += 1
        if (self.commandCount == 4):
            self.commandCount = 0
            self.commandInd = len(self.commands)
            self.commands.append(0)

def ConvertToGXList(convData, mats):
    
    retValue = []
    for k in range(0,len(convData.modelVerts)):
        vertList = convData.modelVerts[k].verts
    
        GXList = GXWriter()
        
        triList = convData.modelVerts[k].tris
        quadList = convData.modelVerts[k].quads
        
        triStrips, indTris = Stripping.CreateStrips(triList, 3)
        
        i = 0
        # TODO: strips
        if (len(indTris) > 0):
            GXList.PushCommand(GXCommands.CMD_TRI.value, 0, 0, 0)
            for i in range(len(indTris)):
                GXList.PushCommand(GXCommands.CMD_MTX.value, vertList[indTris[i]].targetMatrix, 0, 0)
                GXList.PushCommand(GXCommands.CMD_TEXCOORD.value, vertList[indTris[i]].u, vertList[indTris[i]].v, 0)
                if (mats[convData.modelVerts[k].materialInd].use_vcol):
                    GXList.PushCommand(GXCommands.CMD_COLOR.value, vertList[indTris[i]].colr, vertList[indTris[i]].colg, vertList[indTris[i]].colb)
                else:
                    GXList.PushCommand(GXCommands.CMD_NORMAL.value, vertList[indTris[i]].normx, vertList[indTris[i]].normy, vertList[indTris[i]].normz)
                
                GXList.PushCommand(GXCommands.CMD_POS.value, vertList[indTris[i]].x, vertList[indTris[i]].y, vertList[indTris[i]].z)
                i += 1
        
        if (len(triStrips) > 0):
            for strip in triStrips:
                GXList.PushCommand(GXCommands.CMD_TRISTRIP.value, 0, 0, 0)
                for j in strip:
                    GXList.PushCommand(GXCommands.CMD_MTX.value, vertList[j].targetMatrix, 0, 0)
                    GXList.PushCommand(GXCommands.CMD_TEXCOORD.value, vertList[j].u, vertList[j].v, 0)
                    if (mats[convData.modelVerts[k].materialInd].use_vcol):
                        GXList.PushCommand(GXCommands.CMD_COLOR.value, vertList[j].colr, vertList[j].colg, vertList[j].colb)
                    else:
                        GXList.PushCommand(GXCommands.CMD_NORMAL.value, vertList[j].normx, vertList[j].normy, vertList[j].normz)
                    GXList.PushCommand(GXCommands.CMD_POS.value, vertList[j].x, vertList[j].y, vertList[j].z)
        
        quadStrips, indQuads = Stripping.CreateStrips(quadList, 4)
        
        if (len(indQuads) > 0):
            GXList.PushCommand(GXCommands.CMD_QUAD.value, 0, 0, 0)
            for i in range(len(indQuads)):
                GXList.PushCommand(GXCommands.CMD_MTX.value, vertList[indQuads[i]].targetMatrix, 0, 0)
                GXList.PushCommand(GXCommands.CMD_TEXCOORD.value, vertList[indQuads[i]].u, vertList[indQuads[i]].v, 0)
                if (mats[convData.modelVerts[k].materialInd].use_vcol):
                    GXList.PushCommand(GXCommands.CMD_COLOR.value, vertList[indQuads[i]].colr, vertList[indQuads[i]].colg, vertList[indQuads[i]].colb)
                else:
                    GXList.PushCommand(GXCommands.CMD_NORMAL.value, vertList[indQuads[i]].normx, vertList[indQuads[i]].normy, vertList[indQuads[i]].normz)
                GXList.PushCommand(GXCommands.CMD_POS.value, vertList[indQuads[i]].x, vertList[indQuads[i]].y, vertList[indQuads[i]].z)
        
        if (len(quadStrips) > 0):
            for strip in quadStrips:
                GXList.PushCommand(GXCommands.CMD_QUADSTRIP.value, 0, 0, 0)
                for j in strip:
                    GXList.PushCommand(GXCommands.CMD_MTX.value, vertList[j].targetMatrix, 0, 0)
                    GXList.PushCommand(GXCommands.CMD_TEXCOORD.value, vertList[j].u, vertList[j].v, 0)
                    if (mats[convData.modelVerts[k].materialInd].use_vcol):
                        GXList.PushCommand(GXCommands.CMD_COLOR.value, vertList[j].colr, vertList[j].colg, vertList[j].colb)
                    else:
                        GXList.PushCommand(GXCommands.CMD_NORMAL.value, vertList[j].normx, vertList[j].normy, vertList[j].normz)
                    GXList.PushCommand(GXCommands.CMD_POS.value, vertList[j].x, vertList[j].y, vertList[j].z)
        
        convData.vertCount += len(triList)
        convData.triCount += int(len(triList)/3)
        retValue.append(GXList.commands)
    
    return retValue