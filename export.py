import bpy
import mathutils
from . import DataConvert
from . import GXCommandList

class NSVert:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.normx = 0
        self.normy = 0
        self.normz = 0
        self.colr = 0
        self.colg = 0
        self.colb = 0
        self.cola = 0
        self.u = 0
        self.v = 0

class NSSubModel:
    def __init__(self):
        self.verts = []
        self.tris = []
        self.matId = 0

class NSModel:
    def __init__(self):
        subModels = []
        

def ProcessMesh(mesh):
    mesh = NSModel()
    for matId in range(0,len(mesh.materials)):
        vertTuples = {}
        subMesh = NSSubModel()
        for face in mesh.polygons:
            if face.material_index == matId:
                for loop_ind in range(face.loop_start, face.loop_start+3):
                    newVert = NSVert()
                    loop = obj.loops[loop_ind]
                    newVert.x = obj.vertices[loop.vertex_index].undeformed_co.x
                    newVert.y = obj.vertices[loop.vertex_index].undeformed_co.y
                    newVert.z = obj.vertices[loop.vertex_index].undeformed_co.z
                    newVert.normx = loop.normal.x
                    newVert.normy = loop.normal.y
                    newVert.normz = loop.normal.z
                    for uv_layer in obj.uv_layers:
                        uv = uv_layer.uv[loop_ind].vector
                        newVert.u = uv.x
                        newVert.v = uv.y
                        break
                    
                    vertAsTuple = ((newVert.x,newVert.y,newVert.z),(newVert.normx,newVert.normy,newVert.normz),(newVert.u,newVert.v))
                    if not vertAsTuple in vertTuples:
                        subMesh.verts.append(newVert)
                        vertTuples[vertAsTuple] = len(subMesh.verts)-1
                        subMesh.tris.append(len(subMesh.verts)-1)
                    else:
                        subMesh.tris.append(vertTuples[vertAsTuple])
        mesh.subModels.append(subMesh)
    return mesh

class ExportModel:
    def __init__(self, context, filepath, settings):
        pass

    def execute(self):
        # code to get armatures if people selected meshes
        arma_list = []
        selected_obj = bpy.context.active_object
        
        if (selected_obj.type != "MESH"):
            def draw(self, context):
                self.layout.label(text="No valid model was selected!")
            bpy.context.window_manager.popup_menu(draw_func=draw, title="NSBMD Exporter", icon="ERROR")
            return {'CANCELLED'}
        
        mesh = ProcessMesh(selected_obj)
        
        newConv = DataConvert.ConvertVerts(mesh.verts,False,64,64,True,0,0)
        
        GXList = GXCommandList.ConvertToGXList(newConv.modelVerts, mesh.tris, [], [])

        return{'FINISHED'}
