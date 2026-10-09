import maya.cmds as cmds
import sys

project_dir = cmds.workspace(query=True, rootDirectory=True)
scripts_dir = project_dir + "scripts/"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import stair_data
import stair_generation
import stair_update
import stair_ui
import stair_persistence

stair_update.cleanup_callbacks()
stair_persistence.load_settings()
valid_curves = stair_generation.get_selected_curves()
if valid_curves:
    for curve_transform in valid_curves:
        stair_generation.generate_stairs(curve_transform, stair_data.num_steps, stair_data.stair_width, stair_data.stair_thickness)
        stair_persistence.save_settings()
        stair_update.watch_curve_transform(curve_transform)
        stair_update.watch_curve_shape(curve_transform)

stair_ui.show_staircase_ui()