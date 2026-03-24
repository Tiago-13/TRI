# Reactive Robot - Wall Follower (TRI - 2nd Semester)

This repository contains our ROS 2 package for the Reactive Robotics assignment. The goal of this project is to program a differential-drive robot to navigate a custom "5-shaped" arena purely using reactive sensor data (LiDAR), with no mapping or memory.

## Current Progress
* **Custom 3D Arena:** Designed the "5" maze in Blender (complete with the hollow, curved belly and entrance gap) and exported it as a collision-ready `.stl` file.
* **Gazebo World:** Wrote a clean `five.sdf` file that loads the custom Blender mesh, paints it black, and sets up the physics and lighting. 
* **Build System:** Configured `setup.py` to properly install the `worlds` and `models` folders so Gazebo can find them.

## How to Build and Run

### 1. Build the Workspace
Navigate to the root of your ROS 2 workspace in your terminal and compile the package:
```bash
cd <path_to_your_workspace_root>
colcon build --symlink-install
``

### 2. Run the Simulation

Every time you open a new terminal to run this project, you must run these three commands from the root of your workspace.

```bash
# 1. Source the workspace
source install/setup.bash

# 2. Tell Gazebo where our custom 3D models are hidden
export GZ_SIM_RESOURCE_PATH=${PWD}/install/reactive_robot/share/reactive_robot/models

# 3. Launch the world
gz sim src/reactive_robot/worlds/five.sdf
```

