import bpy
from mathutils import Vector

IAN_RIG_NAME = "ian_rig"
DINO_RIG_NAME = "Armature_trex"
LANDSCAPE_NAME = "landscape"
MIDPOINT_TARGET_NAME = "TARGET_Combat_Midpoint"

# switches the 3D viewport into camera view.
def enter_camera_view():
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.region_3d.view_perspective = "CAMERA"
                    return
     
# Finds an object in the Blender scene by name
# Obtains the name of specific actor before creating cameras associated with them          
def get_actor(actor_name):
    actor = bpy.data.objects.get(actor_name)

    if not actor:
        print(f"Actor not found: {actor_name}")

    return actor

# Finds an existing empty object or creates a new one if it does not exist.
# Empty objects are used as camera tracking targets.
def get_or_create_empty(name, location=(0, 0, 0)):
    empty = bpy.data.objects.get(name)

    if not empty:
        bpy.ops.object.empty_add(type="SPHERE", location=location)
        empty = bpy.context.object
        empty.name = name

    return empty

# Finds an existing camera or creates a new one.
# Updates the camera location and lens, then sets it as the active scene camera.
def get_or_create_camera(name, location, lens=35):
    camera = bpy.data.objects.get(name)

    if not camera:
        bpy.ops.object.camera_add(location=location)
        camera = bpy.context.object
        camera.name = name
    else:
        camera.location = location

    camera.data.lens = lens
    bpy.context.scene.camera = camera
    return camera

# Clears old camera constraints and adds a Track To constraint.
# this forces the camera to always aim at the selected target object.
def add_track_to(camera, target):
    camera.constraints.clear()

    constraint = camera.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

# creates a target empty parented to an actor.
# the local offset controls what body area the camera aims at: such as the face, torso, or full body.
def get_or_create_actor_target(target_name, actor_name, local_offset):
    actor = get_actor(actor_name)

    if not actor:
        return None

    target = get_or_create_empty(target_name)

    target.parent = actor
    target.location = local_offset

    return target

# Creates a camera preset that follows a specific actor.
# the target is parented to the actor, while the camera is placed away from the actor and stays focused to look at the target.
def create_actor_camera(camera_name, actor_name, target_name, target_offset, camera_offset, lens=50):
    actor = get_actor(actor_name)

    if not actor:
        return

    target = get_or_create_actor_target(target_name, actor_name, target_offset)

    if not target:
        return

    camera_location = actor.location + Vector(camera_offset)

    camera = get_or_create_camera(camera_name, camera_location, lens)
    add_track_to(camera, target)

    bpy.context.scene.camera = camera
    enter_camera_view()

# Creates a camera that tracks a fixed world-space target..
def create_tracking_camera(camera_name, target_name, target_location, camera_location, lens=50):
    target = get_or_create_empty(target_name, target_location)
    target.parent = None
    target.location = target_location

    camera = get_or_create_camera(camera_name, camera_location, lens)
    add_track_to(camera, target)

    bpy.context.scene.camera = camera
    enter_camera_view()
    
# Creates a camera preset based around the landscape object
def create_landscape_camera(camera_name, target_name, target_offset, camera_offset, lens=35):
    landscape = bpy.data.objects.get(LANDSCAPE_NAME)

    if not landscape:
        print("Landscape not found")
        return

    target = get_or_create_empty(target_name)
    target.parent = landscape
    target.location = target_offset

    camera_location = landscape.location + Vector(camera_offset)

    camera = get_or_create_camera(camera_name, camera_location, lens)
    add_track_to(camera, target)

    bpy.context.scene.camera = camera
    enter_camera_view()

# calculates the midpoint between the two actors (Ian and Dino)
#height offset is added so the camera aims above the ground and closer to the center of the characters.
def get_midpoint_between_actors(height_offset=1.5):
    ian = get_actor(IAN_RIG_NAME)
    dino = get_actor(DINO_RIG_NAME)

    if not ian or not dino:
        return Vector((0, 0, height_offset))

    midpoint = (ian.location + dino.location) / 2
    midpoint.z += height_offset
    return midpoint

# creates or retrieves a shared midpoint target for combat-wide shots.
# so that wide and birds eye cameras track this target.
def get_or_create_combat_midpoint_target():
    target = get_or_create_empty(MIDPOINT_TARGET_NAME)
    target.parent = None
    return target

# updates the midpoint target every frame based on Ian+dino world positions.
# allows wide shots to keep both characters centered as they move.
def update_combat_midpoint(scene=None):
    ian = bpy.data.objects.get(IAN_RIG_NAME)
    dino = bpy.data.objects.get(DINO_RIG_NAME)
    target = bpy.data.objects.get(MIDPOINT_TARGET_NAME)

    if not ian or not dino or not target:
        return

    midpoint = (ian.matrix_world.translation + dino.matrix_world.translation) / 2
    midpoint.z += 1.5

    target.location = midpoint

# Adds the midpoint update function to Blender's frame change handler
# This keeps the combat midpoint target updating during playback 
def register_midpoint_handler():
    if update_combat_midpoint not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(update_combat_midpoint)
     
# Measures the distance between Ian and the dinosaur and adjust camera distance and lens dynamically.   
def get_actor_distance():
    ian = get_actor(IAN_RIG_NAME)
    dino = get_actor(DINO_RIG_NAME)

    if not ian or not dino:
        return 5

    return (ian.matrix_world.translation - dino.matrix_world.translation).length

# creates a wide camera shot centered between Ian and the dinosaur.
# lens and camera distance adjust based on how far apart the characters are, helping keep both actors in frame.
def wide_shot():
    target = get_or_create_combat_midpoint_target()
    update_combat_midpoint()

    actor_distance = get_actor_distance()

    #camera lens changes depending on the distance of the actors to fit both actors in camera frame 

    if actor_distance < 8:
        lens = 50
    elif actor_distance < 15:
        lens = 40
    else:
        lens = 20
    

    # Camera pulls back more when actors are farther apart
    camera_back_distance = max(15, actor_distance * 0.8)
    camera_height = max(1.0, actor_distance * 0.1)

    camera = get_or_create_camera(
        "CAM_Wide_Shot",
        target.location + Vector((0, -camera_back_distance, camera_height)),
        lens=lens
    )

    add_track_to(camera, target)

    bpy.context.scene.camera = camera
    enter_camera_view()
    register_midpoint_handler()
    
# Creates an overhead camera shot looking down at the combat midpoint.
# The camera height and lens adjust based on the distance between the actors.
def birds_eye():
    target = get_or_create_combat_midpoint_target()
    update_combat_midpoint()

    actor_distance = get_actor_distance()

    #camera lens changes depending on the distance of the actors to fit both actors in camera frame 

    if actor_distance < 8:
        lens = 50
    elif actor_distance < 15:
        lens = 40
    else:
        lens = 24

    # Height get higher when fighters spread apart
    camera_height = max(18, actor_distance * 1)

    camera = get_or_create_camera(
        "CAM_Birds_Eye",
        target.location + Vector((0, 0, camera_height)),
        lens=lens
    )

    add_track_to(camera, target)

    bpy.context.scene.camera = camera
    enter_camera_view()
    register_midpoint_handler()
    
# Creates a close-up camera for Ian.
# The target offset aims near Ian's face
def track_ian_close():
    create_actor_camera(
        "CAM_Ian_Close",
        IAN_RIG_NAME,
        "TARGET_Ian_Close",
        (0, 0, 1.7),      # Target Offset (Camera lens focuses face of model)
        (-4.0, -1, 1.5), # Camera Offset (camera location)
        lens=300
    )

# Creates a full-body tracking shot for Ian.
def track_ian_full():
    create_actor_camera(
        "CAM_Ian_Full",
        IAN_RIG_NAME,
        "TARGET_Ian_Full",
        (0, 0, 0.92),
        (-10, -3.2, 1),
        lens=110
    )

# Creates a close-up tracking shot for the dinosaur.
# The target offset aims near the head
def track_dino_close():
    create_actor_camera(
        "CAM_Dino_Close",
        DINO_RIG_NAME,
        "TARGET_Dino_Close",
        (-2, 0, 3),
        (7.5, -6, 3.75),
        lens=64
    )

# Creates a full-body tracking shot for the dinosaur
# Useful for showing the full creature rig
def track_dino_full():
    create_actor_camera(
        "CAM_Dino_Full",
        DINO_RIG_NAME,
        "TARGET_Dino_Full",
        (-3, 2, 2.5),
        (5.5, -7, 2.3),
        lens=23
    )

# Blender api class which connects the camera preset function to a clickable UI button.
class CAMERA_OT_wide_shot(bpy.types.Operator):
    bl_idname = "combat_camera.wide_shot"
    bl_label = "Wide Shot"

    def execute(self, context):
        wide_shot()
        return {"FINISHED"}

# Creates the Combat Camera Assistant panel in the 3D View sidebar with buttons to switch to different cameras

class CAMERA_OT_birds_eye(bpy.types.Operator):
    bl_idname = "combat_camera.birds_eye"
    bl_label = "Bird's Eye View"

    def execute(self, context):
        birds_eye()
        return {"FINISHED"}


class CAMERA_OT_ian_close(bpy.types.Operator):
    bl_idname = "combat_camera.ian_close"
    bl_label = "Track Ian Close-Up"

    def execute(self, context):
        track_ian_close()
        return {"FINISHED"}


class CAMERA_OT_ian_full(bpy.types.Operator):
    bl_idname = "combat_camera.ian_full"
    bl_label = "Track Ian Full Body"

    def execute(self, context):
        track_ian_full()
        return {"FINISHED"}


class CAMERA_OT_dino_close(bpy.types.Operator):
    bl_idname = "combat_camera.dino_close"
    bl_label = "Track Dinosaur Close-Up"

    def execute(self, context):
        track_dino_close()
        return {"FINISHED"}


class CAMERA_OT_dino_full(bpy.types.Operator):
    bl_idname = "combat_camera.dino_full"
    bl_label = "Track Dinosaur Full Body"

    def execute(self, context):
        track_dino_full()
        return {"FINISHED"}


class CAMERA_PT_combat_camera_panel(bpy.types.Panel):
    bl_label = "Combat Camera Assistant"
    bl_idname = "CAMERA_PT_combat_camera_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Camera"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Preset Shots")
        layout.operator("combat_camera.wide_shot")
        layout.operator("combat_camera.birds_eye")

        layout.separator()

        layout.label(text="Ian Tracking")
        layout.operator("combat_camera.ian_close")
        layout.operator("combat_camera.ian_full")

        layout.separator()

        layout.label(text="Dinosaur Tracking")
        layout.operator("combat_camera.dino_close")
        layout.operator("combat_camera.dino_full")

# All custom operator and panel classes that need to be registered with Blender.
classes = [
    CAMERA_OT_wide_shot,
    CAMERA_OT_birds_eye,
    CAMERA_OT_ian_close,
    CAMERA_OT_ian_full,
    CAMERA_OT_dino_close,
    CAMERA_OT_dino_full,
    CAMERA_PT_combat_camera_panel
]

# Registers all classes and the UI panel so Blender can display them.
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

# Unregisters the classes and panel
# This allows the script to be safely reloaded during development without any lingering scripts.
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass

    register()