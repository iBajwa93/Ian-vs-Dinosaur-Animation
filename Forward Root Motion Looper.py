#Take one animated cycle and measure how far the root bone moves during that cycle, 
#then duplicate the keyframes forward offsetting the root bone so the motion keeps traveling forward instead of snapping back.

import bpy

# Stores user-editable settings for the root motion looper panel
# These values appear in the Blender UI so the user can choose
# the frame range, number of loops, and root bone name (if the name is something other than "root") 
#Min/Max applied to prevent accidental user entries that might crash blender

class ROOTMOTION_Properties(bpy.types.PropertyGroup):
    start_frame: bpy.props.IntProperty(
        name="Start Frame",
        default=0,
        min=0
    )

    end_frame: bpy.props.IntProperty(
        name="End Frame",
        default=32,
        min=0
    )

    loop_count: bpy.props.IntProperty(
        name="Number of Loops",
        default=4,
        min=1,
        max=50
    )

    root_bone_name: bpy.props.StringProperty(
        name="Root Bone",
        default="root"
    )

# Blender operator that generates repeated animation loops
# Duplicates the selected action's bone keyframes over multiple cycles
# but offsets the root bone so the character continues moving forward

class ROOTMOTION_OT_generate_loops(bpy.types.Operator):
    bl_idname = "rootmotion.generate_loops"
    bl_label = "Generate Continuous Root Motion"
    
    def execute(self, context):
        # Get the user's settings from the custom scene properties
        props = context.scene.rootmotion_props
        
        # The selected object should be the armature being animated
        armature = context.object
        
        # Stops the tool if the user has not selected an armature
        if not armature or armature.type != "ARMATURE":
            self.report({"ERROR"}, "Select the armature first.")
            return {"CANCELLED"}
        
        # Stops the tool if the armature has no active animation action
        if not armature.animation_data or not armature.animation_data.action:
            self.report({"ERROR"}, "Selected armature has no active action.")
            return {"CANCELLED"}
        
        # store the active action so its keyframes can be read and duplicated
        action = armature.animation_data.action
        
        # read the user-defined loop settings.
        start = props.start_frame
        end = props.end_frame
        loop_count = props.loop_count
        root_name = props.root_bone_name
        
        # number of frames in one whole animation cycle (add 1 because the frames start from 0)
        cycle_length = end - start + 1
        
        # Prevent invalid frame ranges (no negatives)
        if cycle_length <= 0:
            self.report({"ERROR"}, "End frame must be after start frame.")
            return {"CANCELLED"}

        # Data path for the selected root bone's location animation.
        #this points to the X, Y, and Z location curves for the root bone
        root_path = f'pose.bones["{root_name}"].location'
        
        # Stores how far the root bone moves during one cycle using displacement.
        # Index 0 (X), 1 (Y), 2 (Z)
        root_displacement = [0, 0, 0]
        
        # Measure the root bone's movement from the start frame to the end frame
        # this displacement calculation is later added to each repeated loop
        for axis_index in range(3):
            fc = action.fcurves.find(root_path, index=axis_index)

            if fc:
                start_value = fc.evaluate(start)
                end_value = fc.evaluate(end)
                root_displacement[axis_index] = end_value - start_value
                
        # Store the original keyframes within the chosen frame range
        # These keyframes are used as the cycle for all repeated loops
        original_keys = []

        for fc in action.fcurves:
            for key in fc.keyframe_points:
                frame = key.co.x

                if start <= frame <= end:
                    original_keys.append({
                        "data_path": fc.data_path,
                        "array_index": fc.array_index,
                        "frame": frame,
                        "value": key.co.y,
                        "interpolation": key.interpolation
                    })
                    
        # Create additional copies of the original animation cycle.
        # loop_index starts at 1 because the first loop already exists.
        for loop_index in range(1, loop_count):
            frame_offset = loop_index * cycle_length

            for key in original_keys:
                is_root_location = key["data_path"] == root_path
                is_first_frame_of_cycle = key["frame"] == start

                # Skip the first root-location key on repeated loops.
                # This prevents the root from having a brief pausing at the beginning
                if is_root_location and is_first_frame_of_cycle:
                    continue

                 # Move the copied keyframe forward in time.
                new_frame = key["frame"] + frame_offset
                
                # Start with the original keyframe value.
                new_value = key["value"]
                
                # If a key belongs to the root bone's location
                # it gets offset it by the total root displacement for the loop number.
                # This keeps the character moving forward instead of returning to the same position every cycle
                if is_root_location and key["array_index"] in [0, 1, 2]:
                    new_value += root_displacement[key["array_index"]] * loop_index

                # Find the matching animation curve for this key.
                fc = action.fcurves.find(
                    key["data_path"],
                    index=key["array_index"]
                )
                # If the curve does not exist, create it.
                if not fc:
                    fc = action.fcurves.new(
                        data_path=key["data_path"],
                        index=key["array_index"]
                    )
                # Insert the copied keyframe into the animation curve.
                new_key = fc.keyframe_points.insert(
                    new_frame,
                    new_value,
                    options={"FAST"}
                )
                # Preserve the original interpolation type
                new_key.interpolation = key["interpolation"]

        #Make only the root location keys linear.
        # This keeps root travel consistent while leaving body animation alone.
        for fc in action.fcurves:
            if fc.data_path == root_path and fc.array_index in [0, 1, 2]:
                for key in fc.keyframe_points:
                    key.interpolation = "LINEAR"
            fc.update()
        context.scene.frame_end = start + (cycle_length * loop_count) - 1
        
        # confirmation message in Blender with the measured displacement.
        self.report(
            {"INFO"},
            f"Generated {loop_count} loops using root displacement "
            f"X:{root_displacement[0]:.3f}, "
            f"Y:{root_displacement[1]:.3f}, "
            f"Z:{root_displacement[2]:.3f}"
        )

        return {"FINISHED"}


# Root Motion UI panel in the 3D View sidebar.
# This gives the user controls for frame range, loop count, and root bone name.
class ROOTMOTION_PT_panel(bpy.types.Panel):
    bl_label = "Continuous Root Motion Looper"
    bl_idname = "ROOTMOTION_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Root Motion"

    def draw(self, context):
        layout = self.layout
        props = context.scene.rootmotion_props

        #  user input fields
        layout.prop(props, "start_frame")
        layout.prop(props, "end_frame")
        layout.prop(props, "loop_count")
        layout.prop(props, "root_bone_name")

        layout.separator()
        
        layout.operator("rootmotion.generate_loops")

# List of classes that need to be registered with Blender.
classes = [
    ROOTMOTION_Properties,
    ROOTMOTION_OT_generate_loops,
    ROOTMOTION_PT_panel
]

# Registers the property group, operator, and panel with Blender
# attache custom root motion properties to the Scene
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.rootmotion_props = bpy.props.PointerProperty(
        type=ROOTMOTION_Properties
    )

# Unregisters the tool and removes the custom scene properties
# allows the script to be safely reloaded after script edits
def unregister():
    if hasattr(bpy.types.Scene, "rootmotion_props"):
        del bpy.types.Scene.rootmotion_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass

    register()