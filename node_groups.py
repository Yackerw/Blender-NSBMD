import bpy


class MakeGroups:
    def __init__(self):
        pass

    def execute(self):
        if '.NSBMD_SHADER_MULTI' in bpy.data.node_groups:
            return
        # VECTORS
        '''self._nn_reflection()
        # self._reflection_normal()
        self._nn_vector()'''

        # SHADERS
        self._nns_multi()
        self._nns_decal()
        self._nns_toon()
        '''self._gno_shader_init_flat()
        self._gno_shader_init_no_spec()
        self._gno_shader_init_all()
        self._gno_shader()
        self._xno_shader()'''

    @staticmethod
    def _nns_multi():
        tree = bpy.data.node_groups.new('.NSBMD_SHADER_MULTI', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Material Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Material Alpha', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 31
        var.default_value = 31
        var.min_value = 0

        var = tree.interface.new_socket(name='Ambient', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.5, 0.5, 0.5, 1.0)

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)

        var = tree.interface.new_socket(name='Emission', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Texture Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Texture Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Use Vertex Color', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketShader')
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1470.07958984375, -520.1580810546875)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (2578.059814453125, -144.22499084472656)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.location = (-1116.964111328125, 188.75318908691406)

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.width = 150.0
        var.location = (-1384.963623046875, 120.74063873291016)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.label = 'AMB'
        var.location = (-590.5086669921875, 104.7331771850586)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB'
        var.location = (-1382.7823486328125, -102.23172760009766)

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF'
        var.location = (-1616.0599365234375, -130.42684936523438)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[2].default_value = 0.5
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[4].default_value = 0.0
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = 0.0
        var.inputs[7].default_value = 0.0
        var.inputs[8].default_value = (0.0, 0.0, 0.0)
        var.inputs[9].default_value = 0.0
        var.inputs[10].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.label = 'MIX TEX COL'
        var.location = (846.5193481445312, -72.74815368652344)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.002'
        var.location = (-818.5494384765625, 176.40940856933594)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeVertexColor')
        var.name = 'Color Attribute'
        var.location = (-1214.761962890625, -1309.056884765625)

        var = tree.nodes.new(type='ShaderNodeMixShader')
        var.name = 'Mix Shader'
        var.location = (2220.1708984375, -186.28367614746094)
        var.inputs[0].default_value = 0.5

        var = tree.nodes.new(type='ShaderNodeEmission')
        var.name = 'Emission'
        var.location = (1753.9820556640625, -504.353515625)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeBsdfTransparent')
        var.name = 'Transparent BSDF'
        var.location = (1753.9820556640625, -379.15447998046875)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'SPEC'
        var.label = 'SPEC'
        var.location = (-1121.510009765625, 20.122167587280273)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.label = 'REMOVE LIGHT IF VCOL'
        var.location = (-332.3349914550781, 97.25360870361328)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert Color'
        var.label = 'IS NOT USE VCOL'
        var.location = (-689.8701171875, -129.18194580078125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-847.0528564453125, -1151.8304443359375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeWireframe')
        var.name = 'Wireframe'
        var.location = (-559.7589721679688, -620.1923828125)
        var.inputs[0].default_value = 2
        var.use_pixel_size = True

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-828.0872802734375, -696.0550537109375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-315.82391357421875, -625.2730712890625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (-774.8389282226562, -935.2531127929688)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 31.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'DIVIDE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-315.01226806640625, -808.3602294921875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (-40.2066535949707, -608.3751831054688)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.location = (-554.1008911132812, -754.0420532226562)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 1.0
        var.use_clamp = False
        var.operation = 'SUBTRACT'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.006'
        var.location = (-500.69171142578125, -934.0504150390625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.label = 'MAT COL'
        var.location = (-66.17074584960938, 70.77839660644531)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.010'
        var.location = (213.71603393554688, 45.75735855102539)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.label = 'FAC BETWEEN'
        var.location = (516.6444091796875, -28.566295623779297)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        # Group Node links
        tree.links.new(tree.nodes["Diffuse BSDF"].outputs[0], tree.nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(tree.nodes["Specular BSDF"].outputs[0], tree.nodes["Shader to RGB"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Transparent BSDF"].outputs[0], tree.nodes["Mix Shader"].inputs[1])
        tree.links.new(tree.nodes["Emission"].outputs[0], tree.nodes["Mix Shader"].inputs[2])
        tree.links.new(tree.nodes["Shader to RGB.001"].outputs[0], tree.nodes["Mix.002"].inputs[1])
        tree.links.new(tree.nodes["SPEC"].outputs[0], tree.nodes["Mix.002"].inputs[2])
        tree.links.new(tree.nodes["Shader to RGB"].outputs[0], tree.nodes["SPEC"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["SPEC"].inputs[2])
        tree.links.new(tree.nodes["Mix.002"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Invert Color"].inputs[1])
        tree.links.new(tree.nodes["Invert Color"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Color Attribute"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Wireframe"].outputs[0], tree.nodes["Math.001"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.004"].inputs[1])
        tree.links.new(tree.nodes["Math.004"].outputs[0], tree.nodes["Mix Shader"].inputs[0])
        tree.links.new(tree.nodes["Mix Shader"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Math.005"].outputs[0], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Math.006"].inputs[0])
        tree.links.new(tree.nodes["Math.002"].outputs[0], tree.nodes["Math.006"].inputs[1])
        tree.links.new(tree.nodes["Math.006"].outputs[0], tree.nodes["Math.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.010"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.010"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Mix.007"].inputs[0])
        tree.links.new(tree.nodes["Mix.010"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Emission"].inputs[0])

    @staticmethod
    def _nns_decal():
        tree = bpy.data.node_groups.new('.NSBMD_SHADER_DECAL', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Material Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Material Alpha', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 31
        var.default_value = 31
        var.min_value = 0

        var = tree.interface.new_socket(name='Ambient', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.5, 0.5, 0.5, 1.0)

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)

        var = tree.interface.new_socket(name='Emission', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Texture Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Texture Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Use Vertex Color', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketShader')
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1470.07958984375, -520.1580810546875)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (2578.059814453125, -144.22499084472656)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.location = (-1116.964111328125, 188.75318908691406)

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.width = 150.0
        var.location = (-1384.963623046875, 120.74063873291016)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.label = 'AMB'
        var.location = (-590.5086669921875, 104.7331771850586)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB'
        var.location = (-1382.7823486328125, -102.23172760009766)

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF'
        var.location = (-1616.0599365234375, -130.42684936523438)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[2].default_value = 0.5
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[4].default_value = 0.0
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = 0.0
        var.inputs[7].default_value = 0.0
        var.inputs[8].default_value = (0.0, 0.0, 0.0)
        var.inputs[9].default_value = 0.0
        var.inputs[10].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.label = 'MIX TEX COL'
        var.location = (846.5193481445312, -72.74815368652344)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.002'
        var.location = (-818.5494384765625, 176.40940856933594)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeVertexColor')
        var.name = 'Color Attribute'
        var.location = (-1214.761962890625, -1309.056884765625)

        var = tree.nodes.new(type='ShaderNodeMixShader')
        var.name = 'Mix Shader'
        var.location = (2220.1708984375, -186.28367614746094)
        var.inputs[0].default_value = 0.5

        var = tree.nodes.new(type='ShaderNodeEmission')
        var.name = 'Emission'
        var.location = (1753.9820556640625, -504.353515625)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeBsdfTransparent')
        var.name = 'Transparent BSDF'
        var.location = (1753.9820556640625, -379.15447998046875)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'SPEC'
        var.label = 'SPEC'
        var.location = (-1121.510009765625, 20.122167587280273)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.label = 'REMOVE LIGHT IF VCOL'
        var.location = (-332.3349914550781, 97.25360870361328)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert Color'
        var.label = 'IS NOT USE VCOL'
        var.location = (-689.8701171875, -129.18194580078125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-847.0528564453125, -1151.8304443359375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeWireframe')
        var.name = 'Wireframe'
        var.location = (-559.7589721679688, -620.1923828125)
        var.inputs[0].default_value = 2
        var.use_pixel_size = True

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-828.0872802734375, -696.0550537109375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-315.82391357421875, -625.2730712890625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (-706.667236328125, -951.7984619140625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 31.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'DIVIDE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-315.01226806640625, -808.3602294921875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (-40.2066535949707, -608.3751831054688)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.location = (-554.1008911132812, -754.0420532226562)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 1.0
        var.use_clamp = False
        var.operation = 'SUBTRACT'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.label = 'MAT COL'
        var.location = (-66.17074584960938, 70.77839660644531)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.010'
        var.location = (213.71603393554688, 45.75735855102539)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.label = 'FAC BETWEEN'
        var.location = (516.6444091796875, -28.566295623779297)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        # Group Node links
        tree.links.new(tree.nodes["Diffuse BSDF"].outputs[0], tree.nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(tree.nodes["Specular BSDF"].outputs[0], tree.nodes["Shader to RGB"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Transparent BSDF"].outputs[0], tree.nodes["Mix Shader"].inputs[1])
        tree.links.new(tree.nodes["Emission"].outputs[0], tree.nodes["Mix Shader"].inputs[2])
        tree.links.new(tree.nodes["Shader to RGB.001"].outputs[0], tree.nodes["Mix.002"].inputs[1])
        tree.links.new(tree.nodes["SPEC"].outputs[0], tree.nodes["Mix.002"].inputs[2])
        tree.links.new(tree.nodes["Shader to RGB"].outputs[0], tree.nodes["SPEC"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["SPEC"].inputs[2])
        tree.links.new(tree.nodes["Mix.002"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Invert Color"].inputs[1])
        tree.links.new(tree.nodes["Invert Color"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Color Attribute"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Wireframe"].outputs[0], tree.nodes["Math.001"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.004"].inputs[1])
        tree.links.new(tree.nodes["Math.004"].outputs[0], tree.nodes["Mix Shader"].inputs[0])
        tree.links.new(tree.nodes["Mix Shader"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Math.005"].outputs[0], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.010"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.010"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Mix.007"].inputs[0])
        tree.links.new(tree.nodes["Mix.010"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Mix.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Emission"].inputs[0])
        tree.links.new(tree.nodes["Math.002"].outputs[0], tree.nodes["Math.003"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Mix.003"].inputs[0])

    @staticmethod
    def _nns_toon():
        tree = bpy.data.node_groups.new('.NSBMD_SHADER_TOON', 'ShaderNodeTree')
        tree.use_fake_user = True

        # Group inputs
        var = tree.interface.new_socket(name='Material Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Material Alpha', in_out='INPUT', socket_type='NodeSocketInt')
        var.hide_value = False
        var.max_value = 31
        var.default_value = 31
        var.min_value = 0

        var = tree.interface.new_socket(name='Ambient', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.5, 0.5, 0.5, 1.0)

        var = tree.interface.new_socket(name='Specular', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)

        var = tree.interface.new_socket(name='Emission', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = False
        var.default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.interface.new_socket(name='Texture Color', in_out='INPUT', socket_type='NodeSocketColor')
        var.hide_value = True
        var.default_value = (1.0, 1.0, 1.0, 1.0)

        var = tree.interface.new_socket(name='Texture Alpha', in_out='INPUT', socket_type='NodeSocketFloat')
        var.hide_value = True
        var.max_value = 1.0
        var.default_value = 1.0
        var.min_value = 0.0

        var = tree.interface.new_socket(name='Use Vertex Color', in_out='INPUT', socket_type='NodeSocketBool')
        var.hide_value = False
        var.default_value = False

        # Group outputs
        var = tree.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketShader')
        var.hide_value = False

        # Group Nodes
        var = tree.nodes.new(type='NodeGroupInput')
        var.name = 'Group Input'
        var.location = (-1470.07958984375, -520.1580810546875)

        var = tree.nodes.new(type='NodeGroupOutput')
        var.name = 'Group Output'
        var.location = (2578.059814453125, -144.22499084472656)
        var.is_active_output = True

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB.001'
        var.location = (-1116.964111328125, 188.75318908691406)

        var = tree.nodes.new(type='ShaderNodeBsdfDiffuse')
        var.name = 'Diffuse BSDF'
        var.width = 150.0
        var.location = (-1384.963623046875, 120.74063873291016)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = (0.0, 0.0, 0.0)
        var.inputs[3].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.001'
        var.label = 'AMB'
        var.location = (-590.5086669921875, 104.7331771850586)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeShaderToRGB')
        var.name = 'Shader to RGB'
        var.location = (-1382.7823486328125, -102.23172760009766)

        var = tree.nodes.new(type='ShaderNodeEeveeSpecular')
        var.name = 'Specular BSDF'
        var.location = (-1616.0599365234375, -130.42684936523438)
        var.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[2].default_value = 0.5
        var.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
        var.inputs[4].default_value = 0.0
        var.inputs[5].default_value = (0.0, 0.0, 0.0)
        var.inputs[6].default_value = 0.0
        var.inputs[7].default_value = 0.0
        var.inputs[8].default_value = (0.0, 0.0, 0.0)
        var.inputs[9].default_value = 0.0
        var.inputs[10].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.003'
        var.label = 'MIX TEX COL'
        var.location = (1720.7552490234375, -32.86249923706055)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.002'
        var.location = (-818.5494384765625, 176.40940856933594)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeVertexColor')
        var.name = 'Color Attribute'
        var.location = (-1214.761962890625, -1309.056884765625)

        var = tree.nodes.new(type='ShaderNodeMixShader')
        var.name = 'Mix Shader'
        var.location = (2220.1708984375, -186.28367614746094)
        var.inputs[0].default_value = 0.5

        var = tree.nodes.new(type='ShaderNodeEmission')
        var.name = 'Emission'
        var.location = (2077.77490234375, -446.4674377441406)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeBsdfTransparent')
        var.name = 'Transparent BSDF'
        var.location = (1762.1595458984375, -372.8448791503906)
        var.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        var.inputs[1].default_value = 0.0

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'SPEC'
        var.label = 'SPEC'
        var.location = (-1121.510009765625, 20.122167587280273)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.005'
        var.label = 'REMOVE LIGHT IF VCOL'
        var.location = (-332.3349914550781, 97.25360870361328)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeInvert')
        var.name = 'Invert Color'
        var.label = 'IS NOT USE VCOL'
        var.location = (-689.8701171875, -129.18194580078125)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.0, 0.0, 0.0, 1.0)

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.006'
        var.location = (-847.0528564453125, -1151.8304443359375)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeWireframe')
        var.name = 'Wireframe'
        var.location = (-559.7589721679688, -620.1923828125)
        var.inputs[0].default_value = 2
        var.use_pixel_size = True

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math'
        var.location = (-828.0872802734375, -696.0550537109375)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'COMPARE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.001'
        var.location = (-315.82391357421875, -625.2730712890625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.002'
        var.location = (-774.8389282226562, -935.2531127929688)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 31.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'DIVIDE'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.003'
        var.location = (-315.01226806640625, -808.3602294921875)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.004'
        var.location = (-40.2066535949707, -608.3751831054688)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = False
        var.operation = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.005'
        var.location = (-554.1008911132812, -754.0420532226562)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = 1.0
        var.inputs[2].default_value = 1.0
        var.use_clamp = False
        var.operation = 'SUBTRACT'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.006'
        var.location = (-500.69171142578125, -934.0504150390625)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.20000000298023224
        var.use_clamp = True
        var.operation = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.008'
        var.label = 'MAT COL'
        var.location = (-66.17074584960938, 70.77839660644531)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'MULTIPLY'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.010'
        var.location = (213.71603393554688, 45.75735855102539)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = True
        var.use_alpha = False
        var.blend_type = 'ADD'

        var = tree.nodes.new(type='ShaderNodeMixRGB')
        var.name = 'Mix.007'
        var.label = 'FAC BETWEEN'
        var.location = (516.6444091796875, -28.566295623779297)
        var.inputs[0].default_value = 1.0
        var.inputs[1].default_value = (0.005104083567857742, 0.005104083567857742, 0.005104083567857742, 1.0)
        var.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
        var.use_clamp = False
        var.use_alpha = False
        var.blend_type = 'MIX'

        var = tree.nodes.new(type='ShaderNodeSeparateColor')
        var.name = 'Separate Color'
        var.location = (799.6558837890625, 178.72842407226562)
        var.inputs[0].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        var.mode = 'RGB'

        var = tree.nodes.new(type='ShaderNodeCombineColor')
        var.name = 'Combine Color'
        var.location = (1455.770751953125, 212.0609588623047)
        var.inputs[0].default_value = 0.0
        var.inputs[1].default_value = 0.0
        var.inputs[2].default_value = 0.0
        var.mode = 'RGB'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.007'
        var.location = (1010.4313354492188, 218.13330078125)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.5
        var.inputs[2].default_value = 0.5
        var.use_clamp = False
        var.operation = 'GREATER_THAN'

        var = tree.nodes.new(type='ShaderNodeMath')
        var.name = 'Math.008'
        var.location = (1233.3878173828125, 224.95077514648438)
        var.inputs[0].default_value = 0.5
        var.inputs[1].default_value = 0.15000000596046448
        var.inputs[2].default_value = 0.5
        var.use_clamp = True
        var.operation = 'ADD'

        # Group Node links
        tree.links.new(tree.nodes["Diffuse BSDF"].outputs[0], tree.nodes["Shader to RGB.001"].inputs[0])
        tree.links.new(tree.nodes["Specular BSDF"].outputs[0], tree.nodes["Shader to RGB"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[2], tree.nodes["Mix.001"].inputs[2])
        tree.links.new(tree.nodes["Transparent BSDF"].outputs[0], tree.nodes["Mix Shader"].inputs[1])
        tree.links.new(tree.nodes["Emission"].outputs[0], tree.nodes["Mix Shader"].inputs[2])
        tree.links.new(tree.nodes["Shader to RGB.001"].outputs[0], tree.nodes["Mix.002"].inputs[1])
        tree.links.new(tree.nodes["SPEC"].outputs[0], tree.nodes["Mix.002"].inputs[2])
        tree.links.new(tree.nodes["Shader to RGB"].outputs[0], tree.nodes["SPEC"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[3], tree.nodes["SPEC"].inputs[2])
        tree.links.new(tree.nodes["Mix.002"].outputs[0], tree.nodes["Mix.001"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Invert Color"].inputs[1])
        tree.links.new(tree.nodes["Invert Color"].outputs[0], tree.nodes["Mix.005"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.006"].inputs[1])
        tree.links.new(tree.nodes["Color Attribute"].outputs[0], tree.nodes["Mix.006"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math"].inputs[0])
        tree.links.new(tree.nodes["Group Input"].outputs[1], tree.nodes["Math.002"].inputs[0])
        tree.links.new(tree.nodes["Wireframe"].outputs[0], tree.nodes["Math.001"].inputs[1])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.001"].inputs[0])
        tree.links.new(tree.nodes["Math.001"].outputs[0], tree.nodes["Math.004"].inputs[0])
        tree.links.new(tree.nodes["Math.003"].outputs[0], tree.nodes["Math.004"].inputs[1])
        tree.links.new(tree.nodes["Math.004"].outputs[0], tree.nodes["Mix Shader"].inputs[0])
        tree.links.new(tree.nodes["Mix Shader"].outputs[0], tree.nodes["Group Output"].inputs[0])
        tree.links.new(tree.nodes["Math.005"].outputs[0], tree.nodes["Math.003"].inputs[0])
        tree.links.new(tree.nodes["Math"].outputs[0], tree.nodes["Math.005"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[5], tree.nodes["Mix.003"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[6], tree.nodes["Math.006"].inputs[0])
        tree.links.new(tree.nodes["Math.002"].outputs[0], tree.nodes["Math.006"].inputs[1])
        tree.links.new(tree.nodes["Math.006"].outputs[0], tree.nodes["Math.003"].inputs[1])
        tree.links.new(tree.nodes["Mix.005"].outputs[0], tree.nodes["Mix.008"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[0], tree.nodes["Mix.008"].inputs[2])
        tree.links.new(tree.nodes["Mix.001"].outputs[0], tree.nodes["Mix.005"].inputs[1])
        tree.links.new(tree.nodes["Mix.008"].outputs[0], tree.nodes["Mix.010"].inputs[2])
        tree.links.new(tree.nodes["Group Input"].outputs[4], tree.nodes["Mix.010"].inputs[1])
        tree.links.new(tree.nodes["Group Input"].outputs[7], tree.nodes["Mix.007"].inputs[0])
        tree.links.new(tree.nodes["Mix.010"].outputs[0], tree.nodes["Mix.007"].inputs[1])
        tree.links.new(tree.nodes["Mix.006"].outputs[0], tree.nodes["Mix.007"].inputs[2])
        tree.links.new(tree.nodes["Mix.003"].outputs[0], tree.nodes["Emission"].inputs[0])
        tree.links.new(tree.nodes["Mix.007"].outputs[0], tree.nodes["Separate Color"].inputs[0])
        tree.links.new(tree.nodes["Separate Color"].outputs[0], tree.nodes["Math.007"].inputs[0])
        tree.links.new(tree.nodes["Math.007"].outputs[0], tree.nodes["Math.008"].inputs[0])
        tree.links.new(tree.nodes["Math.008"].outputs[0], tree.nodes["Combine Color"].inputs[0])
        tree.links.new(tree.nodes["Math.008"].outputs[0], tree.nodes["Combine Color"].inputs[1])
        tree.links.new(tree.nodes["Math.008"].outputs[0], tree.nodes["Combine Color"].inputs[2])
        tree.links.new(tree.nodes["Combine Color"].outputs[0], tree.nodes["Mix.003"].inputs[1])