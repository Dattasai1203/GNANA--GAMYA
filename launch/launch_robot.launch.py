"""
launch_robot.launch.py — Real Robot Hardware Launch
=====================================================
Launches the complete stack for the physical robot (no Gazebo):
  - Robot State Publisher
  - Twist Mux
  - ros2_control node (reads robot_description from RSP)
  - diff_drive controller spawner (delayed until controller_manager ready)
  - joint_state_broadcaster spawner (delayed)

Joystick is commented out by default — uncomment to enable.

Usage:
  ros2 launch gnanagamya launch_robot.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'gnanagamya'
    pkg_share    = get_package_share_directory(package_name)

    # ── Robot State Publisher ──────────────────────────────────────
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')),
        launch_arguments={
            'use_sim_time':     'false',
            'use_ros2_control': 'true',
        }.items(),
    )

    # ── Joystick (uncomment to enable gamepad teleoperation) ───────
    # joystick = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(pkg_share, 'launch', 'joystick.launch.py')))

    # ── Twist Mux ─────────────────────────────────────────────────
    twist_mux_params = os.path.join(pkg_share, 'config', 'twist_mux.yaml')
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[twist_mux_params],
        remappings=[('/cmd_vel_out', '/diff_cont/cmd_vel_unstamped')],
    )

    # ── ros2_control node ─────────────────────────────────────────
    # Reads robot_description from the already-running RSP node.
    robot_description = Command(
        ['ros2 param get --hide-type /robot_state_publisher robot_description'])

    controller_params_file = os.path.join(pkg_share, 'config', 'my_controllers.yaml')

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            controller_params_file,
        ],
    )

    # Delay controller_manager by 3 s to let RSP finish publishing
    delayed_controller_manager = TimerAction(
        period=3.0,
        actions=[controller_manager],
    )

    # ── diff_drive spawner — starts once controller_manager is up ──
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont'],
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    # ── joint_state_broadcaster spawner ───────────────────────────
    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad'],
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    return LaunchDescription([
        rsp,
        # joystick,
        twist_mux,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
    ])
