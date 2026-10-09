import json
import os
import maya.cmds as cmds
import stair_data

def get_settings_path():
    scene_path = cmds.file(query=True, sceneName=True)
    if not scene_path:
        cmds.warning("Save the Maya scene before saving staircase settings.")
        return None
    scene_name, _ = os.path.splitext(scene_path)
    return scene_name + ".stairs.json"

def save_settings():
    """
    Save the staircase settings dictionary to JSON
    """
    settings_path = get_settings_path()

    if settings_path is None:
        return

    data = {
        "stairs": {}
    }

    for curve, settings in stair_data.staircase_settings.items():
        data["stairs"][curve] = {
            "curve": curve,
            "group": curve + "_stairs_GRP",
            "num_steps": settings["num_steps"],
            "stair_width": settings["stair_width"],
            "stair_thickness": settings["stair_thickness"]
        }
    with open(settings_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)
    print("Saved staircase settings to: {}".format(settings_path))

def load_settings():
    """
    Load staircase settings from JSON into memory
    Does not generate or modify any geometry.
    """
    settings_path = get_settings_path()

    if settings_path is None:
        return False
    if not os.path.exists(settings_path):
        print("No staircase settings file found: {}".format(settings_path))
        return False
    with open(settings_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    stair_data.staircase_settings.clear()
    stair_data.staircase_treads.clear()
    
    restored_count = 0

    for entry in data.get("stairs", {}).values():
        curve = entry["curve"]
        group_name = entry["group"]

        # Only restore settings for curves that still exist
        if not cmds.objExists(curve):
            cmds.warning("Skipping saved staircase; curve not found: {}".format(curve))
            continue
        if not cmds.objExists(group_name):
            cmds.warning("Skipping staircase; group not found: {}".format(group_name))
            continue

        treads = find_existing_treads(group_name)

        if not treads:
            cmds.warning("No existing tread meshes found under: {}".format(group_name))
            continue

        stair_data.staircase_treads[curve] = treads
        restored_count += 1

        stair_data.staircase_settings[curve] = {
            "num_steps": int(entry["num_steps"]),
            "stair_width": float(entry["stair_width"]),
            "stair_thickness": float(entry["stair_thickness"])
        }

    print("Loaded staircase settings from: {}".format(settings_path))
    print("Restored {} staircase(s) from JSON.".format(restored_count))
    return True

def find_existing_treads(group_name):
    """
    Find the existing tread objects directly under a staircase group.
    Does not create or modify geometry
    """
    if not cmds.objExists(group_name):
        cmds.warning("Staircase group not found: {}".format(group_name))
        return []
    children = cmds.listRelatives(group_name, children=True, type="transform") or []

    # Keep only transforms that contain polygon mesh shapes
    treads = []
    for child in children:
        shapes = cmds.listRelatives(
            child,
            shapes=True,
            noIntermediate=True,
            type="mesh") or []
        if shapes:
            treads.append(child)
    return treads