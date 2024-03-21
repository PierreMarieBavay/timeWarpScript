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


def create_timeWarp_sphere(node_index):
    y_position = node_index * 3

    sphere_name = 'timeWarpInfo_geo_{}'.format(node_index)
    if cmds.objExists(sphere_name):
        print("Sphere '{}' already exists.".format(sphere_name))
        return

    sphere_name = cmds.polySphere(name=sphere_name)[0]

    if node_index == 0:
        lambert_material = cmds.shadingNode('lambert', asShader=True, name='timeWarpInfo_lambert_{}'.format(node_index))
        cmds.setAttr(lambert_material + ".color", 1, 0, 0, type='double3')
    elif node_index == 1:
        lambert_material = cmds.shadingNode('lambert', asShader=True, name='timeWarpInfo_lambert_{}'.format(node_index))
        cmds.setAttr(lambert_material + ".color", 0, 0, 1, type='double3')
    elif node_index == 2:
        lambert_material = cmds.shadingNode('lambert', asShader=True, name='timeWarpInfo_lambert_{}'.format(node_index))
        cmds.setAttr(lambert_material + ".color", 0, 1, 0, type='double3')
    elif node_index == 3:
        lambert_material = cmds.shadingNode('lambert', asShader=True, name='timeWarpInfo_lambert_{}'.format(node_index))
        cmds.setAttr(lambert_material + ".color", 1, 1, 0, type='double3')

    cmds.move(0, y_position, 0, sphere_name)

    cmds.select(sphere_name)
    cmds.hyperShade(assign=lambert_material)

    return sphere_name


def create_timeWarp_spheres():
    sphere_names = []
    for index in range(4):
        node_name = 'timeWarp' if index == 0 else 'timeWarp{}'.format(index)
        if not cmds.objExists(node_name):
            continue
        sphere_name = create_timeWarp_sphere(index)
        sphere_names.append(sphere_name)
    return sphere_names


def delete_timeWarp_spheres():
    for index in range(4):
        timeWarp_name = 'timeWarp' if index == 0 else 'timeWarp{}'.format(index)
        sphere_name = 'timeWarpInfo_geo_{}'.format(index)

        if not cmds.objExists(timeWarp_name):
            if cmds.objExists(sphere_name):
                lambert_name = cmds.listConnections('{}.instObjGroups[0]'.format(sphere_name), type='lambert')
                if lambert_name:
                    cmds.delete(lambert_name)
                cmds.delete(sphere_name)


delete_timeWarp_spheres()

create_timeWarp_spheres()


def find_camera_with_name(name_contains):
    all_cameras = cmds.ls(type='camera')
    for camera_shape in all_cameras:
        if re.search(name_contains, camera_shape):
            camera_transform = cmds.listRelatives(camera_shape, parent=True, fullPath=True)
            if camera_transform:
                print("Selected Camera:", camera_transform[0])
                return camera_transform[0]
    return None


def parent_all_spheres_to_camera(camera_name):
    for node_index in range(4):
        sphere_name = 'timeWarpInfo_geo_{}'.format(node_index)
        if not cmds.objExists(sphere_name):
            cmds.warning("Sphere '{}' does not exist.".format(sphere_name))
            continue

        if not cmds.objExists(camera_name):
            cmds.warning("Camera '{}' does not exist.".format(camera_name))
            continue

        current_parent = cmds.listRelatives(sphere_name, parent=True, fullPath=True)
        if current_parent and current_parent[0] == camera_name:
            print("Sphere '{}' is already parented to camera '{}'.".format(sphere_name, camera_name))
            continue

        cmds.parent(sphere_name, camera_name)


# Utilisation :
camera_with_name = find_camera_with_name("renderCam")
if camera_with_name:
    parent_all_spheres_to_camera(camera_with_name)
else:
    cmds.warning("No camera found containing 'renderCam' in its name.")


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


def get_keyframe_times(timeWarp_name):
    if not cmds.objExists(timeWarp_name):
        cmds.warning("TimeWarp '{}' does not exist.".format(timeWarp_name))
        return []

    keyframe_times = cmds.keyframe(timeWarp_name, query=True, timeChange=True) or []
    return keyframe_times


def set_visibility_keyframes(frames_with_key, min_frame, max_frame, sphere_associations):
    for timeWarp_name, sphere_name in sphere_associations.items():
        # Obtenir les temps clés pour le timeWarp spécifique
        frames_with_key = get_keyframe_times(timeWarp_name)

        cmds.select(sphere_name)
        for frame in range(min_frame, max_frame + 1):
            if frame not in frames_with_key:
                cmds.setKeyframe(v=0, at='visibility', t=frame)
            else:
                cmds.setKeyframe(v=1, at='visibility', t=frame)


sphere_associations = associate_timeWarps_with_spheres()

min_frame = int(cmds.playbackOptions(q=True, min=True))
max_frame = int(cmds.playbackOptions(q=True, max=True))
set_visibility_keyframes(frames_with_key, min_frame, max_frame, sphere_associations)

cmds.select(clear=True)

cmds.select(clear=True)
