# Reactive Robot - Wall Follower (TRI - 2nd Semester)

This repository contains our ROS 2 package for the Reactive Robotics assignment. The goal of this project is to program a differential-drive robot to navigate a custom "5-shaped" arena purely using reactive sensor data (LiDAR), with no mapping or memory.

## Current Progress
Custom 3D Arena: Modeled in Blender with a hollow, curved "belly" and entrance gap; exported as a collision-ready .stl.

Gazebo World: A clean five.sdf that handles the mesh loading, lighting, and physics.

Reactive Brain: A Python-based controller using 360° LiDAR segments to handle wall-following and sharp outside corners.

## How to Build and Run

### 1. Build the Workspace
Navigate to the root of your ROS 2 workspace in your terminal and compile the package:
```bash
cd <path_to_your_workspace_root>
colcon build --symlink-install
source install/setup.bash
```

### 2. Run the Simulation

Every time you open a new terminal to run this project, you must run these three commands from the root of your workspace.

```bash
# Launch Gazebo & Robot
ros2 launch reactive_robot assignment.launch.py

# Start the Wall Follower
ros2 run reactive_robot wall_follower

```

