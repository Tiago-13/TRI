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
    pkg_share = FindPackageShare('reactive_robot').find('reactive_robot')

    # Define where your models are (usually in the share directory after install)
    models_path = os.path.join(pkg_share, 'models')
    
    # This REPLACES the manual export command
    set_gz_resource_path = AppendEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=models_path
    )
    
    # Paths to the world and URDF files
    world_file = os.path.join(pkg_share, 'worlds', 'five.sdf')
    urdf_file = os.path.join(pkg_share, 'urdf', 'reactive_robot.urdf')

    # 1. Start Gazebo Sim with the world file
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('ros_gz_sim').find('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # 2. Spawn the robot into Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', urdf_file,
                   '-name', 'reactive_robot',
                   # Spawning outside the bottom of the "5"
                   '-x', '0.0', '-y', '-8.0', '-z', '0.2', '-Y', '1.5708'], 
        output='screen'
    )

    # 3. Bridge ROS 2 and Gazebo Topics for cmd_vel and scan
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'
        ],
        output='screen'
    )

    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='-8.0')
    yaw_pose = LaunchConfiguration('yaw_pose', default='1.5708')

    # Update your spawn_entity arguments to use these configurations
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', urdf_file,
                   '-name', 'reactive_robot',
                   '-x', x_pose, '-y', y_pose, '-z', '0.2', '-Y', yaw_pose], 
        output='screen'
    )

    return LaunchDescription([
        set_gz_resource_path,
        DeclareLaunchArgument('x_pose', default_value='0.0'),
        DeclareLaunchArgument('y_pose', default_value='-8.0'),
        DeclareLaunchArgument('yaw_pose', default_value='1.5708'),
        gz_sim,
        spawn_entity,
        bridge
    ])