"""
camera.launch.py — USB Camera (Real Robot)
===========================================
Launches the v4l2_camera node for the physical robot's USB webcam.
Not needed in simulation (camera is handled by the Gazebo sensor
and ros_gz_image_bridge in launch_sim.launch.py).

Requirements:
  sudo apt install ros-<distro>-v4l2-camera

Usage:
  ros2 launch gnanagamya camera.launch.py
"""

import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            output='screen',
            namespace='camera',
            parameters=[{
                'image_size':        [640, 480],
                'time_per_frame':    [1, 6],        # ~6 fps — adjust as needed
                'camera_frame_id':   'camera_link_optical',
            }],
        ),
    ])
