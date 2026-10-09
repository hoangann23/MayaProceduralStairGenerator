import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.utils
import math
import stair_data
import stair_generation

def update_stair_positions(curve_transform):
    if curve_transform not in stair_data.staircase_treads:
        cmds.warning("No generated treads found for this curve.")
        return
    if not cmds.objExists(curve_transform):
        cmds.warning("The source curve no longer exists.")
        return
    shapes = cmds.listRelatives(curve_transform, shapes=True, noIntermediate=True, type="nurbsCurve") or []
    if not shapes:
        cmds.warning("No NURBS curve shape found.")
        return
    selection = om.MSelectionList()
    selection.add(shapes[0])
    curve_fn = om.MFnNurbsCurve(selection.getDagPath(0))
    length = curve_fn.length()
    if not math.isfinite(length) or length <= 1e-6:
        cmds.warning("The source curve must have non-zero length.")
        return
    steps = stair_data.staircase_treads[curve_transform]
    num_steps = len(steps)
    step_spacing = length / num_steps
    last_forward = om.MVector(0, 0, 1)
    for i, step in enumerate(steps):
        if not cmds.objExists(step):
            continue
        distance = (i + 0.5) * step_spacing
        parameter = curve_fn.findParamFromLength(distance)
        point = curve_fn.getPointAtParam(parameter, om.MSpace.kWorld)
        tangent = curve_fn.tangent(parameter, om.MSpace.kWorld)
        forward = om.MVector(tangent.x, 0, tangent.z)
        if forward.length() > 1e-6:
            forward.normalize()
            last_forward = forward
        else:
            forward = om.MVector(last_forward)
        side = stair_data.world_up ^ forward
        side.normalize()
        matrix = om.MMatrix(
            [side.x, side.y, side.z, 0,
             stair_data.world_up.x, stair_data.world_up.y, stair_data.world_up.z, 0,
             forward.x, forward.y, forward.z, 0,
             point.x, point.y, point.z, 1])
        cmds.xform(step, worldSpace=True, matrix=list(matrix))
    
def update_all_stairs(num_steps=None, stair_width=None, stair_thickness=None):
    for curve_transform, settings in list(stair_data.staircase_settings.items()):
        new_num_steps = num_steps if num_steps is not None else settings["num_steps"]
        new_width = stair_width if stair_width is not None else settings["stair_width"]
        new_thickness = stair_thickness if stair_thickness is not None else settings["stair_thickness"]
        
        stair_generation.generate_stairs(curve_transform, new_num_steps, new_width, new_thickness)
        
def update_individual_stair(curve_transform, num_steps=None, stair_width=None, stair_thickness=None):
    if curve_transform not in stair_data.staircase_settings:
        cmds.warning("No settings found for this staircase.")
        return
    settings = stair_data.staircase_settings[curve_transform]
    
    new_num_steps = num_steps if num_steps is not None else settings["num_steps"]
    new_width = stair_width if stair_width is not None else settings["stair_width"]
    new_thickness = stair_thickness if stair_thickness is not None else settings["stair_thickness"]
    stair_generation.generate_stairs(curve_transform, new_num_steps, new_width, new_thickness)

def watch_curve_transform(curve_transform):
    if curve_transform in stair_data.curve_transform_callbacks:
        return

    job_ids = []
    for attribute in ["translate", "rotate", "scale"]:
        job_id = cmds.scriptJob(attributeChange=["{}.{}".format(curve_transform, attribute), lambda curve=curve_transform: update_stair_positions(curve)],
                       protected=True)
        job_ids.append(job_id)
    stair_data.curve_transform_callbacks[curve_transform] = job_ids
        
def watch_curve_shape(curve_transform):
    if curve_transform in stair_data.curve_shape_callbacks:
        return
    if not cmds.objExists(curve_transform):
        return
    shapes = cmds.listRelatives(curve_transform, shapes=True, noIntermediate=True, type="nurbsCurve") or []

    if not shapes:
        cmds.warning("No NURBS curve shape found.")
        return

    selection = om.MSelectionList()
    selection.add(shapes[0])
    shape_object = selection.getDependNode(0)

    def on_shape_dirty(node, client_data):
        if not cmds.objExists(curve_transform):
            return
        maya.utils.executeDeferred(update_stair_positions, curve_transform)
    callback_id = om.MNodeMessage.addNodeDirtyCallback(shape_object, on_shape_dirty)
    stair_data.curve_shape_callbacks[curve_transform] = callback_id

def cleanup_callbacks():
    # Remove Maya API callbacks that monitor curve shapes
    for curve_transform, callback_id in list(
        stair_data.curve_shape_callbacks.items()
    ):
        try:
            om.MMessage.removeCallback(callback_id)
        except RuntimeError:
            # Callback may already have been removed
            pass

    stair_data.curve_shape_callbacks.clear()

    # Remove scriptJobs that monitor curve transforms
    for curve_transform, job_ids in list(
        stair_data.curve_transform_callbacks.items()
    ):
        for job_id in job_ids:
            if cmds.scriptJob(exists=job_id):
                cmds.scriptJob(kill=job_id, force=True)

    stair_data.curve_transform_callbacks.clear()