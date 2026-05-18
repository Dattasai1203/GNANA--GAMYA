"""
launch_sim.launch.py — Full Gazebo Simulation
===============================================
Launches the complete simulation stack:
  - Robot State Publisher (URDF → /robot_description)
  - Joystick teleoperation
  - Twist Mux (velocity priority multiplexer)
  - Gazebo Sim (Ignition) with the chosen world
  - Robot spawner
  - ros2_control: diff_drive + joint_state_broadcaster
  - Gazebo ↔ ROS 2 topic bridge (gz_bridge.yaml)
  - Camera image bridge

Usage:
  ros2 launch gnanagamya launch_sim.launch.py
  ros2 launch gnanagamya launch_sim.launch.py world:=<path/to/world.sdf>
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, DeclareLaunchArgument)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'gnanagamya'
    pkg_share    = get_package_share_directory(package_name)

    # ── Robot State Publisher ──────────────────────────────────────
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')),
        launch_arguments={
            'use_sim_time':     'true',
            'use_ros2_control': 'true',
        }.items(),
    )

    # ── Joystick teleoperation ─────────────────────────────────────
    joystick = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'joystick.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    # ── Twist Mux ─────────────────────────────────────────────────
    twist_mux_params = os.path.join(pkg_share, 'config', 'twist_mux.yaml')
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[twist_mux_params, {'use_sim_time': True}],
        remappings=[('/cmd_vel_out', '/diff_cont/cmd_vel_unstamped')],
    )

    # ── World selection ───────────────────────────────────────────
    default_world = os.path.join(pkg_share, 'worlds', 'empty.world')
    world     = LaunchConfiguration('world')
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Path to Gazebo world file (.world or .sdf)',
    )

    # ── Gazebo Sim (Ignition) ─────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args':        ['-r -v4 ', world],
            'on_exit_shutdown': 'true',
        }.items(),
    )

    # ── Spawn robot into Gazebo ───────────────────────────────────
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name',  'my_bot',
            '-z',     '0.1',
        ],
        output='screen',
    )

    # ── ros2_control: spawn diff_drive controller ─────────────────
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont'],
    )

    # ── ros2_control: spawn joint state broadcaster ───────────────
    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad'],
    )

    # ── Gazebo ↔ ROS 2 bridge (clock, scan, odom, tf, cmd_vel) ────
    bridge_params = os.path.join(pkg_share, 'config', 'gz_bridge.yaml')
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_params}'],
    )

    # ── Camera image bridge ────────────────────────────────────────
    ros_gz_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw'],
    )

    return LaunchDescription([
        rsp,
        joystick,
        twist_mux,
        world_arg,
        gazebo,
        spawn_entity,
        diff_drive_spawner,
        joint_broad_spawner,
        ros_gz_bridge,
        ros_gz_image_bridge,
    ])
