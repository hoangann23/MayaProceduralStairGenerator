

# Procedural Staircase Generator — Autodesk Maya

A procedural modeling tool built with Python for Autodesk Maya that generates staircases along 3D NURBS curves. The tool allows artists to quickly create and customize staircases while automatically updating the geometry when the underlying curve changes.

## Features

* **Procedural Generation:** Creates individual stair treads distributed along a curve using arc-length sampling.
* **Customizable Parameters:** Adjusts step count, tread width, and thickness through a Maya UI.
* **Live Updates:** Repositions treads when the curve's control vertices or transform are modified.
* **Flexible Editing:** Supports editing multiple staircases together or customizing them individually.
* **Scene Persistence:** Saves staircase settings to JSON and restores them when reopening the tool.
* **Organized Geometry:** Groups generated treads for easier scene management.

## Technologies

* Python
* Autodesk Maya
* Maya Python API 2.0
* JSON

## Demo

See the video below for a walkthrough of procedural generation, parameter adjustments, and live curve editing.


https://github.com/user-attachments/assets/5e501158-c88d-419a-81e6-26d52339107e

## Motivation

This project explores procedural modeling and artist-facing tool development, with an emphasis on automating repetitive modeling tasks and supporting an efficient, flexible workflow.
