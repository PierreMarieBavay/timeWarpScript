import maya.cmds as cmds

import re
def get_keyframe_times_for_timeWarp_nodes():
    keyframe_times_dict = {}

    index = 0
    while True:
        node_name = 'timeWarp' if index == 0 else 'timeWarp{}'.format(index)
        if not cmds.objExists(node_name):
            break  # Arrête la recherche si le nœud n'existe pas
        keyframe_times = cmds.keyframe(node_name, query=True, timeChange=True) or []
        keyframe_times_dict[node_name] = keyframe_times
        index += 1

    return keyframe_times_dict

keyframe_times_dict = get_keyframe_times_for_timeWarp_nodes()

for node_name, keyframe_times in keyframe_times_dict.items():
    print("Keyframe Times on {}: {}".format(node_name, keyframe_times))



def create_red_lambert_sphere():
    # Vérifiez si la sphère existe déjà dans la scène
    if cmds.objExists('timeWarpInfo_geo'):
        cmds.warning("Sphere 'timeWarpInfo_geo' already exists in the scene.")
        return

    # Créer une sphère
    sphere_name = cmds.polySphere(name='timeWarpInfo_geo')[0]

    # Créer un matériau Lambert rouge
    lambert_material = cmds.shadingNode('lambert', asShader=True, name='timeWarpInfo_lambert')
    cmds.setAttr(lambert_material + ".color", 1, 0, 0, type='double3')

    # Associer le matériau Lambert à la sphère
    cmds.select(sphere_name)
    cmds.hyperShade(assign=lambert_material)

# Appeler la fonction pour créer la sphère rouge si elle n'existe pas déjà
create_red_lambert_sphere()


def find_camera_with_name(name_contains):
    all_cameras = cmds.ls(type='camera')
    for camera_shape in all_cameras:
        if re.search(name_contains, camera_shape):
            camera_transform = cmds.listRelatives(camera_shape, parent=True, fullPath=True)
            if camera_transform:
                print("Selected Camera:", camera_transform[0])
                return camera_transform[0]
    return None

def match_camera_transform_to_sphere():
    sphere = "timeWarpInfo_geo"
    if not cmds.objExists(sphere):
        cmds.warning("Sphere 'timeWarpInfo_geo' does not exist.")
        return

    camera_with_name = find_camera_with_name("renderCam")
    if not camera_with_name:
        cmds.warning("No camera found containing 'renderCam' in its name.")
        return


match_camera_transform_to_sphere()


def parent_to_camera(obj_name, camera_name):
    if not cmds.objExists(obj_name):
        cmds.warning("Object '{}' does not exist.".format(obj_name))
        return

    if not cmds.objExists(camera_name):
        cmds.warning("Camera '{}' does not exist.".format(camera_name))
        return

    current_parent = cmds.listRelatives(obj_name, parent=True, fullPath=True)
    if current_parent and current_parent[0] == camera_name:
        print("Object '{}' is already parented to camera '{}'.".format(obj_name, camera_name))
        return

    cmds.parent(obj_name, camera_name)

camera_with_name = find_camera_with_name("renderCam")
if camera_with_name:
    print("Camera containing 'renderCam' in its name:", camera_with_name)

    parent_to_camera('timeWarpInfo_geo', camera_with_name)
else:
    print("No camera found containing 'renderCam' in its name.")


def get_keyframe_times(node_name):
    if not cmds.objExists(node_name):
        cmds.warning("Node '{}' does not exist.".format(node_name))
        return []
    keyframe_times = cmds.keyframe(node_name, query=True, timeChange=True) or []
    return keyframe_times

def set_visibility_keyframes(frames_with_key, min_frame, max_frame, sphere_name):
    cmds.select(sphere_name)
    for frame in range(min_frame, max_frame + 1):
        if frame not in frames_with_key:
            cmds.setKeyframe(v=0, at='visibility', t=frame)
        else:
            cmds.setKeyframe(v=1, at='visibility', t=frame)

frames_with_key = get_keyframe_times('timeWarp')
min_frame = int(cmds.playbackOptions(q=True, min=True))
max_frame = int(cmds.playbackOptions(q=True, max=True))
set_visibility_keyframes(frames_with_key, min_frame, max_frame, 'timeWarpInfo_geo')


cmds.select(clear=True)

