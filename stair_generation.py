import maya.cmds as cmds
import maya.api.OpenMaya as om
import math
import stair_data

def get_selected_curves():
    selected = cmds.ls(selection=True, objectsOnly=True) or []
    if not selected:
        cmds.warning("Please select at least one NURBS curve.")
        return None
    valid_curves = []
    for obj in selected:
        shapes = cmds.listRelatives(obj, shapes=True, noIntermediate=True) or []
        is_curve = any(cmds.nodeType(shape) == "nurbsCurve" for shape in shapes)
        if not is_curve:
            continue
        valid_curves.append(obj)
        
    if not valid_curves:
        cmds.warning("No valid NURBS curves were selected")
    return valid_curves

def generate_stairs(curve_transform, num_steps, stair_width, stair_thickness):
    if not isinstance(num_steps, int) or num_steps < 1:
        cmds.warning("Number of steps must be a positive integer.")
        return
    if stair_width <= 0:
        cmds.warning("Stair width must be greater than zero.")
        return
    if stair_thickness <= 0:
        cmds.warning("Stair thickness must be greater than zero.")
        return
        
    # Validate that the source object still exists
    if not cmds.objExists(curve_transform):
        cmds.warning("The source curve no longer exists")
        return

    shapes = cmds.listRelatives(curve_transform, shapes=True)
    
    selection = om.MSelectionList()
    selection.add(shapes[0])
    dag_path = selection.getDagPath(0)
    
    curve_fn = om.MFnNurbsCurve(dag_path)
    length = curve_fn.length()
    if not math.isfinite(length) or length <= 1e-6:
        cmds.warning("The source curve must have a non-zero length.")
        return
    step_spacing = length / num_steps
    
    stair_data.staircase_settings[curve_transform] = {
        "num_steps": num_steps,
        "stair_width": stair_width,
        "stair_thickness": stair_thickness
    }
    
    stairs_group_name = curve_transform + "_stairs_GRP"
    if cmds.objExists(stairs_group_name):
        cmds.delete(stairs_group_name)
    stairs_group = cmds.group(empty=True, name=stairs_group_name)
    last_forward = om.MVector(0, 0, 1)
    steps = []
    for i in range(num_steps):
        distance = (i + 0.5) * step_spacing
        parameter = curve_fn.findParamFromLength(distance)
        point = curve_fn.getPointAtParam(parameter, om.MSpace.kWorld)
        step = cmds.polyCube(name="{}_stair_{:02d}".format(curve_transform, i), 
                             width = stair_width,
                             height = stair_thickness,
                             depth = step_spacing,
                             constructionHistory=False)[0]
        steps.append(step)
        
        tangent = curve_fn.tangent(parameter, om.MSpace.kWorld)
        forward = om.MVector(tangent.x, 0, tangent.z)
        if forward.length() > 1e-6:
            forward.normalize()
            last_forward = forward
        else:
            forward = om.MVector(last_forward)
        side = stair_data.world_up ^ forward
        side.normalize()
        up = stair_data.world_up
        
        matrix = om.MMatrix(
                           [side.x, side.y, side.z, 0,
                            up.x, up.y, up.z, 0,
                            forward.x, forward.y, forward.z, 0,
                            point.x, point.y, point.z, 1])
        cmds.xform(step, worldSpace=True, matrix=list(matrix))
        cmds.parent(step, stairs_group)
    stair_data.staircase_treads[curve_transform] = steps