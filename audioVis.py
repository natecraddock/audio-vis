bl_info = {
    "name": "Easy Audio Vis",
    "author": "Nathan Craddock",
    "version": (1, 0, 0),
    "blender": (2, 7, 2),
    "location": "Object Mode >> Tool Shelf >> AudioVis Tab",
    "description": "",
    "category": "Object"
}

import bpy

class AudioVisPanel(bpy.types.Panel):
    """Audio Visualizer Panel"""
    bl_category = "AudioVis"
    bl_idname = "AUDIO_VIS"
    bl_context = "objectmode"
    bl_label = "Easy Audio Visualizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.prop(context.scene, "audio_vis_file")
        layout.separator()
        
        split = layout.split()
        
        # Location
        col = split.column(align = True)
        col.label(text = "Location:")
        col.prop(context.scene, "audio_vis_location_x")
        col.prop(context.scene, "audio_vis_location_y")
        col.prop(context.scene, "audio_vis_location_z")
        
        # Rotation
        col = split.column(align = True)
        col.label(text = "Rotation:")
        col.prop(context.scene, "audio_vis_rotation_x")
        col.prop(context.scene, "audio_vis_rotation_y")
        col.prop(context.scene, "audio_vis_rotation_z")
        
        # Scale
        col = split.column(align = True)
        col.label(text = "Scale:")
        col.prop(context.scene, "audio_vis_scale_x")
        col.prop(context.scene, "audio_vis_scale_y")
        col.prop(context.scene, "audio_vis_scale_z")
        layout.separator()
        
        # Color
        layout.prop(context.scene, "audio_vis_color")           
        if context.scene.audio_vis_color:
            #layout.prop_search(context.scene, "audio_vis_chosen_material", bpy.context.active_object, "material_slots", "Material")
            layout.operator("object.audio_vis_add_color_ramp")
            
            cr_node = bpy.data.materials['Ramp Material'].node_tree.nodes['ColorRamp']
            layout.template_color_ramp(cr_node, "color_ramp", expand=True)
        
        
        # F-Curve bake options
        layout.label(text = "Bake options:")

        row = layout.row()
        row.prop(context.scene, "audio_vis_low_freq")
        row.prop(context.scene, "audio_vis_high_freq")
        
        row = layout.row()
        row.prop(context.scene, "audio_vis_attack")
        row.prop(context.scene, "audio_vis_release")
        
        row = layout.row()
        row.prop(context.scene, "audio_vis_threshold")
        
        row = layout.row()
        row.operator("object.audio_vis_run")
        
class AudioVis(bpy.types.Operator):
    """Run the addon"""
    bl_idname = "object.audio_vis_run"
    bl_label = "Bake Sound"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        def insertKeyframes():           
            locRotScaleKeyframes()
        
        def locRotScaleKeyframes():
            object = bpy.context.object
            bpy.context.active_object.animation_data_clear()
            bpy.context.scene.frame_set(1)
            
            if bpy.context.scene.audio_vis_location_x:
                object.keyframe_insert(data_path = "location", index = 0)
            if bpy.context.scene.audio_vis_location_y:
                object.keyframe_insert(data_path = "location", index = 1)        
            if bpy.context.scene.audio_vis_location_z:
                object.keyframe_insert(data_path = "location", index = 2)
                
            if bpy.context.scene.audio_vis_rotation_x:
                object.keyframe_insert(data_path = "rotation_euler", index = 0)
            if bpy.context.scene.audio_vis_rotation_y:
                object.keyframe_insert(data_path = "rotation_euler", index = 1)        
            if bpy.context.scene.audio_vis_rotation_z:
                object.keyframe_insert(data_path = "rotation_euler", index = 2)    
                
            if bpy.context.scene.audio_vis_scale_x:
                object.keyframe_insert(data_path = "scale", index = 0)
            if bpy.context.scene.audio_vis_scale_y:
                object.keyframe_insert(data_path = "scale", index = 1)        
            if bpy.context.scene.audio_vis_scale_z:
                object.keyframe_insert(data_path = "scale", index = 2)
        
        insertKeyframes()
        
        bpy.context.area.type = 'SEQUENCE_EDITOR'
        
        bpy.context.scene.sequence_editor_clear()
        bpy.ops.sequencer.sound_strip_add(filepath = bpy.context.scene["audio_vis_file"], frame_start = 1)
        
        bpy.context.area.type = 'GRAPH_EDITOR'
        
        try:
            bpy.ops.graph.sound_bake(filepath = bpy.context.scene["audio_vis_file"],
            low = context.scene.audio_vis_low_freq,
            high = context.scene.audio_vis_high_freq,
            attack = bpy.context.scene.audio_vis_attack,
            release = bpy.context.scene.audio_vis_release,
            threshold = bpy.context.scene.audio_vis_threshold)
        
        except:
            False
        
        bpy.context.area.type = 'VIEW_3D'
        
        return {'FINISHED'}
        
        
class AudioVisColorRamp(bpy.types.Operator):
    """Create a Color ramp"""
    bl_idname = "object.audio_vis_add_color_ramp"
    bl_label = "Add Color Ramp"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        def addColorRamp():
            material = bpy.data.materials.new("Ramp Material")

            material.use_nodes = True
            nodes = material.node_tree.nodes
            
            # Add the color ramp
            node = nodes.new('ShaderNodeValToRGB')
            node.location = -100, 0
            
            # Mode the other nodes
            node = nodes['Material Output']
            node.location = 400, 0
            
            node = nodes['Diffuse BSDF']
            node.location = 200, 0
            
            # Connect the nodes
            output = nodes['ColorRamp'].outputs['Color']
            input = nodes['Diffuse BSDF'].inputs['Color']
            material.node_tree.links.new(output, input)
            
            output = nodes['Diffuse BSDF'].outputs['BSDF']
            input = nodes['Material Output'].inputs['Surface']
            material.node_tree.links.new(output, input)
            
            # Add to object
            bpy.context.object.data.materials.append(material)
        
        addColorRamp()
        
        return {'FINISHED'}

def properties():
    bpy.types.Scene.audio_vis_file = bpy.props.StringProperty(
        name = "File Path",
        description = "Define the path of the audio file",
        subtype = 'FILE_PATH')
    
    bpy.types.Scene.audio_vis_location_x = bpy.props.BoolProperty(
        name = "X",
        description = "Bake music to X location?",
        default = False)
    
    bpy.types.Scene.audio_vis_location_y = bpy.props.BoolProperty(
        name = "Y",
        description = "Bake music to Y location?",
        default = False)
        
    bpy.types.Scene.audio_vis_location_z = bpy.props.BoolProperty(
        name = "Z",
        description = "Bake music to Z location?",
        default = False)
    
    bpy.types.Scene.audio_vis_rotation_x = bpy.props.BoolProperty(
        name = "X",
        description = "Bake music to X rotation?",
        default = False)
    
    bpy.types.Scene.audio_vis_rotation_y = bpy.props.BoolProperty(
        name = "Y",
        description = "Bake music to Y rotation?",
        default = False)
        
    bpy.types.Scene.audio_vis_rotation_z = bpy.props.BoolProperty(
        name = "Z",
        description = "Bake music to Z rotation?",
        default = False)   

    bpy.types.Scene.audio_vis_scale_x = bpy.props.BoolProperty(
        name = "X",
        description = "Bake music to X scale?",
        default = False)
    
    bpy.types.Scene.audio_vis_scale_y = bpy.props.BoolProperty(
        name = "Y",
        description = "Bake music to Y scale?",
        default = False)
        
    bpy.types.Scene.audio_vis_scale_z = bpy.props.BoolProperty(
        name = "Z",
        description = "Bake music to Z scale?",
        default = False)

    bpy.types.Scene.audio_vis_low_freq = bpy.props.FloatProperty(
        name = "Min Frequency",
        description = "The minimum frequency to bake from",
        default = 0,
        min = 0,
        max = 100000)
        
    bpy.types.Scene.audio_vis_high_freq = bpy.props.FloatProperty(
        name = "Max Frequency",
        description = "The maximum frequency to bake from",
        default = 100000,
        min = 0,
        max = 100000)
        
    bpy.types.Scene.audio_vis_attack = bpy.props.FloatProperty(
        name = "Attack Time",
        description = "How fast the curve can rise",
        default = .005,
        min = 0,
        max = 2)
        
    bpy.types.Scene.audio_vis_release = bpy.props.FloatProperty(
        name = "Release Time",
        description = "How fast the curve can rise",
        default = .200,
        min = 0,
        max = 5)
        
    bpy.types.Scene.audio_vis_threshold = bpy.props.FloatProperty(
        name = "Threshold",
        description = "Minimum amplitude needed to influence the curve",
        default = 0,
        min = 0,
        max = 1)
        
    bpy.types.Scene.audio_vis_color = bpy.props.BoolProperty(
        name = "Color",
        description = "Animate the color?",
        default = False)
        
    bpy.types.Scene.audio_vis_chosen_material = bpy.props.StringProperty()

    
def register():
    bpy.utils.register_class(AudioVisPanel)
    bpy.utils.register_class(AudioVis)
    bpy.utils.register_class(AudioVisColorRamp)
    
    properties()
   
def unregister():
    bpy.utils.unregister_class(AudioVisPanel)
    bpy.utils.unregister_class(AudioVis)
    bpy.utils.unregister_class(AudioVisColorRamp)
    