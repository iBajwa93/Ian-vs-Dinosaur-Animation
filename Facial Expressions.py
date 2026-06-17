# Facial Expression Tool for Ian vs Dinosaur
# This script creates custom expression buttons in Blender's 3D View sidebar
# Each button applies a preset facial pose by rotating or moving selected facial bones
# The tool supports both the Ian character rig and the dinosaur rig

import bpy

IAN_RIG_NAME = "ian_rig"

DINOSAUR_RIG_NAME = "Armature_trex"

# Object names of the rigs in the Blender scene
# These names are used to find the correct armature before applying expressions

def set_bone_rotation(rig, bone_name, rotation):
    bone = rig.pose.bones.get(bone_name)

    if bone:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = rotation
        bone.keyframe_insert(data_path="rotation_euler")
        print(f"Moved: {bone_name}")
    else:
        print(f"Bone not found: {bone_name}")

# Finds a pose bone by name, sets its Euler rotation, and inserts a rotation keyframe
# This is the main helper function used by the expression presets

def apply_group_rotation(rig, bone_names, rotation):
    for bone_name in bone_names:
        set_bone_rotation(rig, bone_name, rotation)
        
#Same as above, but for the translation of the bones instead of the rotation.
        
def set_bone_location(rig, bone_name, location):
    bone = rig.pose.bones.get(bone_name)

    if bone:
        bone.location = location
        bone.keyframe_insert(data_path="location")
        print(f"Moved location: {bone_name}")
    else:
        print(f"Bone not found: {bone_name}")


def apply_group_location(rig, bone_names, location):
    for bone_name in bone_names:
        set_bone_location(rig, bone_name, location)
        

# Bone groups list
# Grouping bones this way makes it easier to apply expressions without repeating code for every single bone

#Ian specific parts
left_brow = [
    "upper_brow1.l", "upper_brow2.l", "upper_brow3.l",
    "lower_brow1.l", "lower_brow2.l", "lower_brow3.l"
]

right_brow = [
    "upper_brow1.r", "upper_brow2.r", "upper_brow3.r",
    "lower_brow1.r", "lower_brow2.r", "lower_brow3.r"
    ]
    
eyebrows = left_brow + right_brow

top_right_mouth = ["upper_lip3.l", "upper_lip2.l", "upper_lip1.l"]

top_left_mouth = ["upper_lip6.l", "upper_lip5.l", "upper_lip4.l"]

bottom_right_mouth = ["lower_lip3.l", "lower_lip2.l", "lower_lip1.l"]

bottom_left_mouth = ["lower_lip6.l", "lower_lip5.l", "lower_lip4.l"]

mouth = top_right_mouth + top_left_mouth + bottom_right_mouth + bottom_left_mouth


#Dinosaur specific parts


tongue = ["tongue1", "tongue2", "tongue3", "tongue4"]


#Ian/Dinosaur parts

upper_left_eye = [
"upper_eye1.l", "upper_eye2.l", "upper_eye3.l"
]

upper_right_eye = [
"upper_eye1.r", "upper_eye2.r", "upper_eye3.r"
]


lower_left_eye = [
"lower_eye1.l", "lower_eye2.l", "lower_eye3.l"
]

lower_right_eye = [
"lower_eye1.r", "lower_eye2.r", "lower_eye3.r"
]

eyes = upper_right_eye + lower_right_eye + upper_left_eye + lower_left_eye



#acts as a reset for the dinosaur's facial expression

def apply_dinosaur_neutral():
    rig = bpy.data.objects.get(DINOSAUR_RIG_NAME)

    if not rig:
        print("Dinosaur rig not found")
        return
    
    set_bone_rotation(rig, "upper_mouth", (0, 0, 0))
    set_bone_rotation(rig, "lower_mouth", (0, 0, 0))
    apply_group_rotation(rig, tongue, (-0.05, 0, 0))
    apply_group_rotation(rig, eyes, (0, 0, 0))


    print("Dinosaur Neutral expression applied")

# Blender operator class.
# This connects the expression function to a clickable button in the UI panel

class DINOSAUR_OT_neutral_expression(bpy.types.Operator):
    bl_idname = "dinosaur.neutral_expression"
    bl_label = "Neutral"

    def execute(self, context):
        apply_dinosaur_neutral()
        return {"FINISHED"}
    
# Applies the dinosaur roar expression by opening the upper and lower mouth,
# curling the tongue, and rotating eyelids for a more aggressive look

def apply_dinosaur_roar():
    rig = bpy.data.objects.get(DINOSAUR_RIG_NAME)

    if not rig:
        print("Dinosaur rig not found")
        return
    
#    Dinosaur rotation reset before applying new expression, to prevent values from conflicting
    set_bone_rotation(rig, "upper_mouth", (0, 0, 0))
    set_bone_rotation(rig, "lower_mouth", (0, 0, 0))
    apply_group_rotation(rig, tongue, (0, 0, 0))
    apply_group_rotation(rig, eyes, (0, 0, 0))
    
    set_bone_rotation(rig, "upper_mouth", (0.5, 0, 0))
    set_bone_rotation(rig, "lower_mouth", (-0.5, 0, 0))
    
    apply_group_rotation(rig, tongue, (-0.1, 0, 0))
    set_bone_rotation(rig, "tongue3", (0.4, 0, 0))
    set_bone_rotation(rig, "tongue4", (0.5, 0, 0))
    
    apply_group_rotation(rig, upper_left_eye, (-0.1, 0, 0))
    apply_group_rotation(rig, upper_right_eye, (-0.1, 0, 0))




    print("Dinosaur Roar expression applied")


class DINOSAUR_OT_roar_expression(bpy.types.Operator):
    bl_idname = "dinosaur.roar_expression"
    bl_label = "Roar"

    def execute(self, context):
        apply_dinosaur_roar()
        return {"FINISHED"}


def apply_dinosaur_stunned():
    rig = bpy.data.objects.get(DINOSAUR_RIG_NAME)

    if not rig:
        print("Dinosaur rig not found")
        return
    
    #    Dinosaur rotation reset before applying new expression
    set_bone_rotation(rig, "upper_mouth", (0, 0, 0))
    set_bone_rotation(rig, "lower_mouth", (0, 0, 0))
    apply_group_rotation(rig, tongue, (0, 0, 0))
    apply_group_rotation(rig, eyes, (0, 0, 0))
    
    set_bone_rotation(rig, "upper_mouth", (-0.35, 0, 0))
    set_bone_rotation(rig, "lower_mouth", (-0.05, 0.15, 0.10))
    
    apply_group_rotation(rig, tongue, (-0.1, 0, 0))
    set_bone_rotation(rig, "tongue2", (0, 0, -0.55))
    set_bone_rotation(rig, "tongue3", (-0.25, 0, 0))
    set_bone_rotation(rig, "tongue4", (-0.85, 0, 0))
    
    apply_group_rotation(rig, upper_left_eye, (0.30, 0, 0))
    apply_group_rotation(rig, upper_right_eye, (0.30, 0, 0))




    print("Dinosaur Stunned expression applied")


class DINOSAUR_OT_stunned_expression(bpy.types.Operator):
    bl_idname = "dinosaur.stunned_expression"
    bl_label = "Stunned"

    def execute(self, context):
        apply_dinosaur_stunned()
        return {"FINISHED"}

#acts as a reset to the facial expression    

def apply_ian_neutral():
    rig = bpy.data.objects.get(IAN_RIG_NAME)

    if not rig:
        print("Ian rig not found")
        return
    
    apply_group_rotation(rig, mouth, (0, 0, 0))
    apply_group_rotation(rig, eyebrows, (0, 0, 0))
    apply_group_location(rig, eyes, (0, 0, 0))
    

    print("Ian Neutral expression applied")


class IAN_OT_neutral_expression(bpy.types.Operator):
    bl_idname = "ian.neutral_expression"
    bl_label = "Neutral"

    def execute(self, context):
        apply_ian_neutral()
        return {"FINISHED"}

# Applies Ian's angry expression by adjusting eyebrow, eye, and mouth bones
# The expression is built from grouped bone rotations and individual bone adjustment


def apply_ian_angry():
    rig = bpy.data.objects.get(IAN_RIG_NAME)

    if not rig:
        print("Ian rig not found")
        return
    
    #    resets mouth, eyebrows and eye before making changes
    apply_group_location(rig, mouth, (0, 0, 0))
    apply_group_location(rig, eyebrows, (0, 0, 0))
    apply_group_location(rig, eyes, (0, 0, 0))


    apply_group_rotation(rig, left_brow, (0, 0, 0.12))
    apply_group_rotation(rig, right_brow, (0, 0, -0.12))
    
    apply_group_rotation(rig, lower_left_eye, (0, 0, 0.20))
    apply_group_rotation(rig, lower_right_eye, (0, 0, -0.20))
    
    apply_group_rotation(rig, upper_left_eye, (0, 0, -0.15))
    apply_group_rotation(rig, upper_right_eye, (0, 0, 0.15))
    
    apply_group_rotation(rig, top_left_mouth, (0, 0, -0.25))
    apply_group_rotation(rig, top_right_mouth, (0, 0, -0.25))
    
    apply_group_rotation(rig, bottom_left_mouth, (0, 0, -0.35))
    apply_group_rotation(rig, bottom_right_mouth, (0, 0, -0.25))
    
    set_bone_rotation(rig, "upper_lip3.l", (0, 0, 0.45))

    print("Ian Angry expression applied")


class IAN_OT_angry_expression(bpy.types.Operator):
    bl_idname = "ian.angry_expression"
    bl_label = "Angry"

    def execute(self, context):
        apply_ian_angry()
        return {"FINISHED"}
    

def apply_ian_fear():
    rig = bpy.data.objects.get(IAN_RIG_NAME)

    if not rig:
        print("Ian rig not found")
        return
    
    #    resets mouth, eyebrows and eye before making changes
    apply_group_location(rig, mouth, (0, 0, 0))
    apply_group_location(rig, eyebrows, (0, 0, 0))
    apply_group_location(rig, eyes, (0, 0, 0))



    apply_group_rotation(rig, left_brow, (0, 0, -0.15))
    apply_group_rotation(rig, right_brow, (0, 0, 0.15))
    
    apply_group_rotation(rig, upper_left_eye, (0, 0, -0.15))
    apply_group_rotation(rig, upper_right_eye, (0, 0, 0.15))
    
    apply_group_rotation(rig, lower_left_eye, (0, 0, -0.15))
    apply_group_rotation(rig, lower_right_eye, (0, 0, 0.15))
    
    apply_group_rotation(rig, top_left_mouth, (0, 0, 0.35))
    apply_group_rotation(rig, top_right_mouth, (0, 0, 0.35))
    
    set_bone_rotation(rig, "lower_lip1.l", (0, 0, 0.45))
    set_bone_rotation(rig, "lower_lip4.l", (0, 0, 0.35))
    set_bone_rotation(rig, "lower_lip5.l", (0, 0, 0.30))
    set_bone_rotation(rig, "lower_lip6.l", (0, 0, 0.00))
    
    

    print("Ian Fear expression applied")
    
class IAN_OT_fear_expression(bpy.types.Operator):
    bl_idname = "ian.fear_expression"
    bl_label = "Fear"

    def execute(self, context):
        apply_ian_fear()
        return {"FINISHED"}


def apply_ian_happy():
    rig = bpy.data.objects.get(IAN_RIG_NAME)

    if not rig:
        print("Ian rig not found")
        return
    
    #    resets mouth, eyebrows and eye before making changes
    apply_group_location(rig, mouth, (0, 0, 0))
    apply_group_location(rig, eyebrows, (0, 0, 0))
    apply_group_location(rig, eyes, (0, 0, 0))


    apply_group_rotation(rig, left_brow, (0, 0, -0.10))
    apply_group_rotation(rig, right_brow, (0, 0, 0.10))
    
    apply_group_rotation(rig, upper_left_eye, (0, 0, 0.15))
    apply_group_rotation(rig, upper_right_eye, (0, 0, -0.15))
    
    apply_group_rotation(rig, lower_left_eye, (0, 0, 0.08))
    apply_group_rotation(rig, lower_right_eye, (0, 0, -0.08))
    
    apply_group_location(rig, top_right_mouth, (0, 0, 0))
    
    
    
    set_bone_rotation(rig, "upper_lip1.l", (0, 0, 20.967))
    set_bone_rotation(rig, "upper_lip3.l", (-0.001067, 0.001027, 0.000103))
    

    set_bone_location(rig, "upper_lip1.l", (0.001877, 0.011086, -0.00058))
    set_bone_location(rig, "upper_lip2.l", (0, 0, 0))
    set_bone_location(rig, "upper_lip3.l", (-0.001067, 0.001027, 0.000103))
    
    set_bone_location(rig, "upper_lip4.l", (-0.000939, -0.001568, -0.000584))
    set_bone_location(rig, "upper_lip5.l", (0.00175, 0.000764, 0.000648))
    set_bone_location(rig, "upper_lip6.l", (0.006753, 0.001545 , 0.001947))
    
    set_bone_location(rig, "lower_lip1.l", (0.006178, -0.004146, 0.00093))
    set_bone_location(rig, "lower_lip2.l", (0.003218, 0.000491, 0.000291))
    set_bone_location(rig, "lower_lip3.l", (0.004803, 0.002961, 0.000112))
    
    set_bone_location(rig, "lower_lip4.l", (0.004381, 00.003478, 0.000922))
    set_bone_location(rig, "lower_lip5.l", (0.003122, 0.001551, 0.000876))
    set_bone_location(rig, "lower_lip6.l", (0.005393, 0.005494, 0.001076))
    
    

    print("Ian Happy expression applied")
    
class IAN_OT_happy_expression(bpy.types.Operator):
    bl_idname = "ian.happy_expression"
    bl_label = "Happy"

    def execute(self, context):
        apply_ian_happy()
        return {"FINISHED"}



class EXPRESSIONS_PT_panel(bpy.types.Panel):
    bl_label = "Expressions"
    bl_idname = "EXPRESSIONS_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Expressions"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj and obj.name == IAN_RIG_NAME:
            layout.label(text="Ian Expressions")
            layout.operator("ian.neutral_expression", text="Neutral")
            layout.operator("ian.angry_expression", text="Angry")
            layout.operator("ian.fear_expression", text="Fear")
            layout.operator("ian.happy_expression", text="Happy")
        
        if obj and obj.name == DINOSAUR_RIG_NAME:
            layout.label(text="Dinosaur Expressions")
            layout.operator("dinosaur.neutral_expression", text="Neutral")
            layout.operator("dinosaur.roar_expression", text="Roar")
            layout.operator("dinosaur.stunned_expression", text="Stunned")
            
        else:
            layout.label(text="Select a rig.")
            
            


# Registers all custom operators and the UI panel so Blender can display and use them

def register():
    bpy.utils.register_class(IAN_OT_neutral_expression)
    bpy.utils.register_class(IAN_OT_fear_expression)
    bpy.utils.register_class(IAN_OT_angry_expression)
    bpy.utils.register_class(IAN_OT_happy_expression)
    
    bpy.utils.register_class(DINOSAUR_OT_neutral_expression)
    bpy.utils.register_class(DINOSAUR_OT_roar_expression)
    bpy.utils.register_class(DINOSAUR_OT_stunned_expression)
    
    bpy.utils.register_class(EXPRESSIONS_PT_panel)

# Unregisters the operators and panel. This helps add further edits and prevent conflict errors when reloading script.
# Common practice includes removing in reverse order to prevent dependancy issues for each class

def unregister():
    bpy.utils.unregister_class(EXPRESSIONS_PT_panel)
    
    bpy.utils.unregister_class(IAN_OT_happy_expression)
    bpy.utils.unregister_class(IAN_OT_angry_expression)
    bpy.utils.unregister_class(IAN_OT_fear_expression)
    bpy.utils.unregister_class(IAN_OT_neutral_expression)
    
    bpy.utils.unregister_class(DINOSAUR_OT_stunned_expression)
    bpy.utils.unregister_class(DINOSAUR_OT_roar_expression)
    bpy.utils.unregister_class(DINOSAUR_OT_neutral_expression)
    
    


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass

    register()