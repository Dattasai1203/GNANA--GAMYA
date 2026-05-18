"""
joystick.launch.py — Gamepad Teleoperation
===========================================
Launches joy_node + teleop_twist_joy + twist_stamper.

  joy_node        : reads gamepad via /dev/input/js0
  teleop_node     : converts joy axes → cmd_vel_joy (Twist)
  twist_stamper   : adds timestamps to unstamped cmd_vel
                    (required by some ros2_control setups)

Output topic : /cmd_vel_joy  (consumed by twist_mux at priority 100)

Usage:
  ros2 launch gnanagamya joystick.launch.py
  ros2 launch gnanagamya joystick.launch.py use_sim_time:=true
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    joy_params = os.path.join(
        get_package_share_directory('gnanagamya'), 'config', 'joystick.yaml')

    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[joy_params, {'use_sim_time': use_sim_time}],
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_node',
        parameters=[joy_params, {'use_sim_time': use_sim_time}],
        remappings=[('/cmd_vel', '/cmd_vel_joy')],
    )

    # Adds a header timestamp to the unstamped diff_cont output
    # Required when ros2_control expects TwistStamped on /diff_cont/cmd_vel
    twist_stamper = Node(
        package='twist_stamper',
        executable='twist_stamper',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('/cmd_vel_in',  '/diff_cont/cmd_vel_unstamped'),
            ('/cmd_vel_out', '/diff_cont/cmd_vel'),
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use Gazebo sim time if true'),
        joy_node,
        teleop_node,
        twist_stamper,
    ])
