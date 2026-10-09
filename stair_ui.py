import maya.cmds as cmds
import stair_data
import stair_update
import stair_persistence

def get_target_settings(target):
    if target == "Edit Together":
        if not stair_data.staircase_settings:
            return None
        first_curve = next(iter(stair_data.staircase_settings))
        return stair_data.staircase_settings[first_curve]
    return stair_data.staircase_settings.get(target)
def show_staircase_ui():
    window_name = "proceduralStaircaseWindow"
    
    # Close the previous UI if it exists
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    window = cmds.window(window_name, title="Procedural Staircase", sizeable=True, widthHeight=(300,180))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAttach=("both", 10))
    
    # build the menu from the managed staircase settings
    menu_options = ["Edit Together"] + list(stair_data.staircase_settings.keys())
    target_menu = cmds.optionMenu(label="")
    for option in menu_options:
        cmds.menuItem(label=option, parent=target_menu)
    
    def on_target_changed(*args):
        target = cmds.optionMenu(target_menu, query=True, value=True)
        if target == "Edit Together":
            curves = [curve for curve in stair_data.staircase_settings if cmds.objExists(curve)]
            if curves:
                cmds.select(curves, replace=True)
            else:
                cmds.select(clear=True)
        elif cmds.objExists(target):
            cmds.select(target, replace=True)
        else:
            cmds.warning("The selected source curve no longer exists.")
            return
        settings = get_target_settings(target)
        if settings is None:
            return
        cmds.intSliderGrp(count_slider, edit=True, value=settings["num_steps"])
        cmds.floatSliderGrp(width_slider, edit=True, value=settings["stair_width"])
        cmds.floatSliderGrp(thickness_slider, edit=True, value=settings["stair_thickness"])
   
    def on_change(*args):
        target = cmds.optionMenu(target_menu, query=True, value=True)
        num_steps = cmds.intSliderGrp(count_slider, query=True, value=True)
        stair_width = cmds.floatSliderGrp(width_slider, query=True, value=True)
        stair_thickness = cmds.floatSliderGrp(thickness_slider, query=True, value=True)
        if target == "Edit Together":
            stair_update.update_all_stairs(num_steps, stair_width, stair_thickness)
        else:
            stair_update.update_individual_stair(target,num_steps, stair_width, stair_thickness)
        stair_persistence.save_settings()
    
    cmds.optionMenu(target_menu, edit=True, changeCommand=on_target_changed)
    count_slider = cmds.intSliderGrp(label="Number of Steps", field=True, minValue=1, maxValue=100, fieldMinValue=1, fieldMaxValue=1000, value=stair_data.num_steps, dragCommand=on_change, changeCommand=on_change)
    width_slider = cmds.floatSliderGrp(label="Stair Width", field=True, minValue=0.1, maxValue=10.0, fieldMinValue=0.1, fieldMaxValue=100.0, value=stair_data.stair_width, precision=2, dragCommand=on_change, changeCommand=on_change)
    thickness_slider = cmds.floatSliderGrp(label="Thickness", field=True, minValue=0.01, maxValue=2.0, fieldMinValue=0.01, fieldMaxValue=10.0, value=stair_data.stair_thickness, precision=2, dragCommand=on_change, changeCommand=on_change)        
   
    cmds.showWindow(window)