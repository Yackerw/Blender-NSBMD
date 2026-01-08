import bpy
import mathutils
from . import DataConvert
from . import GXCommandList
from . import WriteFile
from . import MaterialProcessing
from . import ArmatureProcessing

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
        self.weights = ()

class NSSubModel:
    def __init__(self):
        self.verts = []
        self.tris = []
        self.quads = []
        self.matId = 0

class NSModel:
    def __init__(self):
        self.subModels = []
        

def ProcessMesh(mesh, obj):
    NSMesh = NSModel()
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    faces = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=faces, quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(mesh)
    bm.free()

    for matId in range(0,len(mesh.materials)):
        vertTuples = {}
        subMesh = NSSubModel()
        for face in mesh.polygons:
            if face.material_index == matId:
                for loop_ind in range(face.loop_start, face.loop_start+face.loop_total):
                    newVert = NSVert()
                    loop = mesh.loops[loop_ind]
                    newVert.x = mesh.vertices[loop.vertex_index].undeformed_co.x
                    newVert.y = mesh.vertices[loop.vertex_index].undeformed_co.y
                    newVert.z = mesh.vertices[loop.vertex_index].undeformed_co.z
                    newVert.normx = loop.normal.x
                    newVert.normy = loop.normal.y
                    newVert.normz = loop.normal.z
                    for uv_layer in mesh.uv_layers:
                        uv = uv_layer.uv[loop_ind].vector
                        newVert.u = uv.x
                        newVert.v = uv.y
                        break

                    weights = tuple([(obj.vertex_groups[group.group].name, group.weight) for group in mesh.vertices[loop.vertex_index].groups[::]])
                    newVert.weights = weights
                    
                    vertAsTuple = ((newVert.x,newVert.y,newVert.z),(newVert.normx,newVert.normy,newVert.normz),(newVert.u,newVert.v), weights)
                    if not vertAsTuple in vertTuples:
                        subMesh.verts.append(newVert)
                        vertTuples[vertAsTuple] = len(subMesh.verts)-1
                        if (face.loop_total == 3):
                            subMesh.tris.append(len(subMesh.verts)-1)
                        else:
                            subMesh.quads.append(len(subMesh.verts)-1)
                    else:
                        if (face.loop_total == 3):
                            subMesh.tris.append(vertTuples[vertAsTuple])
                        else:
                            subMesh.quads.append(vertTuples[vertAsTuple])
        NSMesh.subModels.append(subMesh)
    return NSMesh

class ExportModel:
    def __init__(self, context, filepath, settings):
        self.filepath = filepath

    def execute(self):
        selected_obj = bpy.context.active_object
        
        if (selected_obj.type != "MESH"):
            def draw(self, context):
                self.layout.label(text="No valid model was selected!")
            bpy.context.window_manager.popup_menu(draw_func=draw, title="NSBMD Exporter", icon="ERROR")
            return {'CANCELLED'}
        
        nodes = None
        
        for mod in selected_obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object != None:
                nodes = ArmatureProcessing.GetNodes(mod.object)
        
        if nodes == None:
            nodes = ArmatureProcessing.GetBonelessNode(selected_obj)
        
        blenderMesh = selected_obj.to_mesh(preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
        
        mesh = ProcessMesh(blenderMesh, selected_obj)

        mats = MaterialProcessing.GetMaterialInfo(blenderMesh)
        
        newConv = DataConvert.ConvertVerts(mesh.subModels, mats)
        
        triList = []
        quadList = []
        for subMesh in mesh.subModels:
            triList.append(subMesh.tris)
            quadList.append(subMesh.quads)
        
        GXLists = GXCommandList.ConvertToGXList(newConv, triList, quadList, False)
        
        WriteFile.WriteFile(GXLists, newConv, mats, nodes, self.filepath)

        return{'FINISHED'}
