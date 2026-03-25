import random
import math
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import AppendEnvironmentVariable

def generate_launch_description():
    # Fetch installed package
    pkg_share = FindPackageShare('reactive_robot').find('reactive_robot')

    # Construct absolute path to 'models' folder of package
    models_path = os.path.join(pkg_share, 'models')
    
    # Set GZ_SIM_RESOURCE_PATH environment variable to path
    set_gz_resource_path = AppendEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=models_path
    )
    
    # Paths to the world and URDF files
    world_file = os.path.join(pkg_share, 'worlds', 'five.sdf')
    urdf_file = os.path.join(pkg_share, 'urdf', 'reactive_robot.urdf')

    # Define the total safe spawning area
    WORLD_MIN_X, WORLD_MAX_X = -10.0, 10.0
    WORLD_MIN_Y, WORLD_MAX_Y = -10.0, 10.0

    # Define the "Danger Zone" (the bounding box of "5" maze)
    EXCLUDE_MIN_X, EXCLUDE_MAX_X = -4.5, 4.0
    EXCLUDE_MIN_Y, EXCLUDE_MAX_Y = -7.0, 4.5

    valid_spawn = False
    while not valid_spawn:
        rand_x = random.uniform(WORLD_MIN_X, WORLD_MAX_X)
        rand_y = random.uniform(WORLD_MIN_Y, WORLD_MAX_Y)
        
        # Check if the coordinates fall inside the exclusion zone
        inside_x = EXCLUDE_MIN_X < rand_x < EXCLUDE_MAX_X
        inside_y = EXCLUDE_MIN_Y < rand_y < EXCLUDE_MAX_Y
        
        if not (inside_x and inside_y):
            valid_spawn = True

    # Generate a random heading (yaw) between 0 and 2*Pi radians (360 degrees)
    rand_yaw = random.uniform(0.0, 2 * math.pi)

    # Start Gazebo Sim with the world file
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('ros_gz_sim').find('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # Bridge ROS 2 and Gazebo Topics for cmd_vel and scan
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        output='screen'
    )

    # Update spawn_entity arguments to use these configurations
    spawn_entity = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-file', urdf_file,
                    '-name', 'reactive_robot',
                    '-x', str(rand_x), 
                    '-y', str(rand_y), 
                    '-z', '0.2', 
                    '-Y', str(rand_yaw)], 
            output='screen'
        )

    print(f"ATTEMPTING TO SPAWN ROBOT AT: X: {rand_x:.2f}, Y: {rand_y:.2f}, YAW: {rand_yaw * 360 / (2 * math.pi):.2f}")

    return LaunchDescription([
        set_gz_resource_path,
        gz_sim,
        bridge,
        spawn_entity
    ])
