import bpy
import mathutils

class Node():
    def __init__(self):
        self.inverseMatrix = mathutils.Matrix()
        self.parent = -1
        self.position = mathutils.Vector()
        self.scale = mathutils.Vector((1.0,1.0,1.0))
        self.rotation = mathutils.Matrix()
        self.name = ""
        self.validTransform = True
        self.blenderBone = None

def GetNodes(arma):
    bone_ind = 0
    retValue = []
    for bone in arma.data.bones:
        node = Node()
        node.blenderBone = bone
        node.name = bone.name
        node.position = mathutils.Vector((bone.head.x*4096, bone.head.y*4096, bone.head.z*4096)) # todo: i think we need to factor in the scale value from the header here
        #node.scale doesn't need changing and never will as blender doesn't encode scale into bones
        node.rotation = bone.matrix.to_quaternion().to_matrix() # hehe
        rotationMatrix = []
        for i in range(0,3):
            rotationMatrix.append([])
            for j in range(0,3):
                rotationMatrix[i].append(node.rotation[i][j]*4096)
        node.rotation = mathutils.Matrix(rotationMatrix)
        node.inverseMatrix = bone.matrix_local.inverted_safe()
        if (node.inverseMatrix == mathutils.Matrix.Identity(4)):
            node.validTransform = False
        invMatrix = []
        for i in range(0,4):
            invMatrix.append([])
            for j in range(0,4):
                invMatrix[i].append(node.inverseMatrix[i][j]*4096)
        node.inverseMatrix = mathutils.Matrix(invMatrix)
        
        parentId = 0
        for pBone in retValue:
            if pBone.blenderBone == bone.parent:
                node.parent = parentId
                break
            parentId += 1
        
        
        retValue.append(node)
        
        bone_ind += 1
    return retValue

def GetBonelessNode(obj):
    
    node = Node()
    node.name = obj.name
    node.validTransform = False
    return node