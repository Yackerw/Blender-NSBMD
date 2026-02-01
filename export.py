import bpy
import mathutils
from . import DataConvert
from . import GXCommandList
from . import WriteFile
from . import MaterialProcessing
from . import ArmatureProcessing
from . import NSBTX
from . import util

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
        

def ProcessMesh(mesh, obj, mats):
    NSMesh = NSModel()
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    faces = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=faces, quad_method='BEAUTY', ngon_method='BEAUTY')
    bm.to_mesh(mesh)
    bm.free()
    
    colors = None
    
    if len(mesh.color_attributes) > 0:
        colors = mesh.color_attributes[0]
        if (colors.data_type != "FLOAT_COLOR"):
            colorsAsFloat = False
        col = [0, 0, 0, 0] * len(colors.data)
        colors.data.foreach_get("color", col)
        if list(set(col)) == [1.0]:
            col = None
        
        if (colors.domain == "POINT"):
            # convert to corner
            newCol = []
            for face in mesh.polygons:
                for loop_ind in range(face.loop_start, face.loop_start+3):
                    newCol.append(col[mesh.loops[loop_ind].vertex_index*4])
                    newCol.append(col[(mesh.loops[loop_ind].vertex_index*4)+1])
                    newCol.append(col[(mesh.loops[loop_ind].vertex_index*4)+2])
                    newCol.append(col[(mesh.loops[loop_ind].vertex_index*4)+3])
            col = newCol
        colors = col

    for matId in range(0,len(mesh.materials)):
        vertTuples = {}
        subMesh = NSSubModel()
        for face in mesh.polygons:
            if face.material_index == matId:
                if (face.loop_total < 3):
                    continue
                for loop_ind in range(face.loop_start, face.loop_start+face.loop_total):
                    newVert = NSVert()
                    loop = mesh.loops[loop_ind]
                    newVert.x = mesh.vertices[loop.vertex_index].undeformed_co.x
                    newVert.y = mesh.vertices[loop.vertex_index].undeformed_co.y
                    newVert.z = mesh.vertices[loop.vertex_index].undeformed_co.z
                    if (mats[matId].use_vcol == True):
                        if (colors == None):
                            newVert.colr = 255
                            newVert.colg = 255
                            newVert.colb = 255
                        else:
                            newVert.colr = colors[loop_ind*4]*255
                            newVert.colg = colors[(loop_ind*4)+1]*255
                            newVert.colb = colors[(loop_ind*4)+2]*255
                    else:
                        newVert.normx = loop.normal.x
                        newVert.normy = loop.normal.y
                        newVert.normz = loop.normal.z
                        
                    for uv_layer in mesh.uv_layers:
                        uv = uv_layer.uv[loop_ind].vector
                        newVert.u = uv.x
                        newVert.v = 1.0-uv.y
                        break

                    weights = [(obj.vertex_groups[group.group].name, int(group.weight*256)) for group in mesh.vertices[loop.vertex_index].groups[::]]
                    
                    weightTotal = 0
                    i = 0
                    while i < len(weights):
                        weightTotal += weights[i][1]
                        if (weights[i][1] == 0):
                            weights.pop(i)
                            i -= 1
                        i += 1
                    if (weightTotal < 256 and len(weights) > 0):
                        weights[0] = (weights[0][0], weights[0][1] + 256-weightTotal)
                    
                    if (len(weights) > 1):
                        for i in range(len(weights)):
                            if (weights[i][1] == 256):
                                weights[i][1] = 255
                
                    newVert.weights = tuple(weights)
                    
                    vertAsTuple = ((newVert.x,newVert.y,newVert.z),(newVert.normx,newVert.normy,newVert.normz),(newVert.u,newVert.v), newVert.weights)
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
    def __init__(self, context, filepath, settings, pack_tex):
        self.filepath = filepath
        self.pack_tex = pack_tex

    def execute(self):
        selected_obj = bpy.context.active_object
        
        if (selected_obj.type != "MESH"):
            def draw(self, context):
                self.layout.label(text="No valid model was selected!")
            bpy.context.window_manager.popup_menu(draw_func=draw, title="NSBMD Exporter", icon="ERROR")
            return {'CANCELLED'}
        
        texs = NSBTX.OpenNSBTX(selected_obj.data.nsbtx_path)
        
        if texs == None:
            util.show_not_read_nsbtx("NSBMD Exporter")
            return {'CANCELLED'}
        
        nodes = None
        
        for mod in selected_obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object != None:
                nodes = ArmatureProcessing.GetNodes(mod.object)
        
        if nodes == None:
            nodes = []
        
        nodes.append(ArmatureProcessing.GetBonelessNode(selected_obj))
        
        blenderMesh = selected_obj.to_mesh(preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
        
        mats = MaterialProcessing.GetMaterialInfo(blenderMesh, texs)
        
        mesh = ProcessMesh(blenderMesh, selected_obj, mats)
        
        if (mats == None):
            return {'CANCELLED'}
        
        newConv = DataConvert.ConvertVerts(mesh.subModels, mats, nodes)
        
        GXLists = GXCommandList.ConvertToGXList(newConv, mats)
        
        WriteFile.WriteFile(GXLists, newConv, mats, nodes, texs, self.pack_tex, self.filepath)

        return{'FINISHED'}
