import bpy
from . import util

class NSBTXFile():
    def __init__(self):
        self.fileContents = []
        self.texNames = []
        self.texFormats = []
        self.texSizesX = []
        self.texSizesY = []
        self.paletteNames = []

def ReadDictNames(f, dictOffs):
    f.seek(dictOffs+1, 0)
    itemCount = util.read_byte(f, "<")
    headerSize = util.read_short(f, "<")
    f.seek(dictOffs+headerSize-(itemCount*16), 0)
    retValue = []
    for i in range(itemCount):
        retValue.append(util.read_str(f, 16))
    return retValue

def ReadTexInfo(f, dictOffs):
    f.seek(dictOffs+1, 0)
    itemCount = util.read_byte(f, "<")
    f.seek(dictOffs+0xC+(itemCount*4)+4, 0)
    retValue = []
    retValueX = []
    retValueY = []
    for i in range(itemCount):
        retValue.append((util.read_integer(f, "<") >> 26) & 7)
        texSize = util.read_integer(f, "<")
        retValueX.append(texSize & 2047)
        retValueY.append((texSize >> 11) & 2047)
    return retValue,retValueX,retValueY

def OpenNSBTX(filePath):
    f = open(filePath,"rb")
    if (f == None):
        return None
    checkByte = util.read_byte(f, "<")
    if checkByte != 0x42:
        return None
    checkByte = util.read_byte(f, "<")
    if checkByte != 0x54:
        return None
    checkByte = util.read_byte(f, "<")
    if checkByte != 0x58:
        return None
    checkByte = util.read_byte(f, "<")
    if checkByte != 0x30:
        return None
    
    retTex = NSBTXFile()
    f.seek(0x10, 0)
    TEXOffset = util.read_integer(f, "<")
    f.seek(TEXOffset+4, 0)
    TEXSize = util.read_integer(f, "<")
    f.seek(TEXOffset, 0)
    for i in range(TEXSize):
        retTex.fileContents.append(util.read_byte(f, "<"))
    
    f.seek(TEXOffset+0xE, 0)
    dictOffset = util.read_short(f, "<")+TEXOffset
    
    retTex.texNames = ReadDictNames(f, dictOffset)
    
    retTex.texFormats,retTex.texSizesX,retTex.texSizesY = ReadTexInfo(f, dictOffset)
    
    f.seek(TEXOffset+0x34, 0)
    dictOffset = util.read_short(f, "<")+TEXOffset
    
    retTex.paletteNames = ReadDictNames(f, dictOffset)
    
    f.close()
    
    return retTex