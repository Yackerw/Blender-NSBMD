import bpy


class StripContext():
    def __init__(self):
        self.faceLength = 0
        self.strips = []
        self.inds = []
        self.faces = []
        

def RotateFace(face):
    newFace = []
    for i in range(len(face)):
        newFace.append(0)
    for i in range(len(face)):
        newFace[i-1] = face[i]
    return newFace

def CheckTriEnd(face, strip):
    # strips flip every other face, account for that
    if (((len(strip)-3)%2)==0):
        if (strip[-2] == face[1] and strip[-1] == face[0]):
            return True
    else:
        if (strip[-2] == face[0] and strip[-1] == face[1]):
            return True
    return False

def CheckQuadEnd(face, strip):
    if (len(strip) == 4):
        if (strip[-2] == face[1] and strip[-1] == face[0]):
            return 1
    else:
        if (strip[-2] == face[0] and strip[-1] == face[1]):
            return 2
    return 0

def CreateStrip(ctx, ind):
    face = []
    for i in range(0, ctx.faceLength):
        face.append(ctx.faces[ind+i])
    
    for i in range(0, ctx.faceLength):
        # prioritize existing strips over new ones to make longer strips
        for j in range(len(ctx.strips)):
            strip = ctx.strips[j]
            if (len(strip) > ctx.faceLength):
                if (ctx.faceLength == 3):
                    if (CheckTriEnd(face, strip)):
                        strip.append(face[2])
                        ctx.strips[j] = strip
                        return True
                else:
                    quadCheck = CheckQuadEnd(face, strip) 
                    if (quadCheck == 1):
                        tmp = strip[-1]
                        strip[-1] = strip[-2]
                        strip[-2] = tmp
                        strip.append(face[3])
                        strip.append(face[2])
                        ctx.strips[j] = strip
                        return True
                    if (quadCheck == 2):
                        strip.append(face[3])
                        strip.append(face[2])
                        ctx.strips[j] = strip
                        return True
                        
        face = RotateFace(face)
    for i in range(0, ctx.faceLength):
        for j in range(len(ctx.strips)):
            strip = ctx.strips[j]
            if (len(strip) == ctx.faceLength):
                # one face long strip should also be rotated to test...
                for k in range(0,ctx.faceLength):
                    if (ctx.faceLength == 3):
                        if (CheckTriEnd(face, strip)):
                            strip.append(face[2])
                            ctx.strips[j] = strip
                            return True
                    else:
                        quadCheck = CheckQuadEnd(face, strip) 
                        if (quadCheck == 1):
                            tmp = strip[-1]
                            strip[-1] = strip[-2]
                            strip[-2] = tmp
                            strip.append(face[3])
                            strip.append(face[2])
                            ctx.strips[j] = strip
                            return True
                        if (quadCheck == 2):
                            strip.append(face[3])
                            strip.append(face[2])
                            ctx.strips[j] = strip
                            return True
                    strip = RotateFace(strip)
                    
        face = RotateFace(face)
    # add to new strip
    ctx.strips.append(face)
    return False

def CreateIndividuals(ctx):
    newStrips = []
    newInds = []
    for strip in ctx.strips:
        if (len(strip) == ctx.faceLength):
            for i in strip:
                newInds.append(i)
        else:
            newStrips.append(strip)
    
    ctx.inds = newInds
    ctx.strips = newStrips

"""def CreateStripAlt(ctx, ind):
    face = []
    newFace = []
    for i in range(0, ctx.faceLength):
        face.append(ctx.faces[ind+i])
        newFace.append(0)
    
    shouldRotate = True
    foundTri = False
    i = 0
    while i < ctx.faceLength or foundTri:
        foundTri = False
        
        for j in range(ind, len(ctx.faces), ctx.faceLength):
            for k in range(ctx.faceLength):
                newFace[k] = ctx.faces[j+k]
            
            for k in range(ctx.faceLength):
                
                if (CheckTriEnd(newFace, face)):
                    face.append(newFace[2])
                    for l in range(ctx.faceLength):
                        ctx.faces.pop(k)
                    shouldRotate = False
                    foundTri = True
                    break
                newFace = RotateFace(newFace)
            if (foundTri == True):
                break
        
        if shouldRotate:
            face = RotateFace(face)
        i += 1
    ctx.strips.append(face)

# creates longer strips, but leaves more triangles..
def CreateStripsAlt(indices, vertsInFace):
    ctx = StripContext()
    ctx.faces = indices
    ctx.faceLength = vertsInFace
    
    i = 0
    while i < len(ctx.faces):
        CreateStripAlt(ctx, i)
        i += ctx.faceLength
    
    CreateIndividuals(ctx)
    
    maxStripLen = 0
    for strip in ctx.strips:
        maxStripLen += len(strip)-2
    
    print(maxStripLen/len(ctx.strips))
    print(len(ctx.inds)/3)
    
    return ctx.strips, ctx.inds"""

def CreateStrips(indices, vertsInFace):
    ctx = StripContext()
    ctx.faces = indices
    ctx.faceLength = vertsInFace
    
    i = 0
    # ctx.faces can be modified within, so we can't use range
    while i < len(ctx.faces):
        CreateStrip(ctx, i)
        i += ctx.faceLength
    
    keepIterating = True
    while (keepIterating):
        keepIterating = False
        CreateIndividuals(ctx)
        ctx.faces = ctx.inds
        i = 0
        while i < len(ctx.faces):
            if (CreateStrip(ctx, i)):
                keepIterating = True
            i += ctx.faceLength
    
    CreateIndividuals(ctx)
    
    maxStripLen = 0
    if (ctx.faceLength == 4 and len(ctx.strips) > 0):
        for strip in ctx.strips:
            maxStripLen += (len(strip)-2)/2
        
        print(maxStripLen/len(ctx.strips))
        print(len(ctx.inds)/4)
    
    return ctx.strips, ctx.inds