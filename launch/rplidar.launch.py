"""
rplidar.launch.py — RPLidar A-Series (Real Robot)
==================================================
Launches the rplidar_ros driver for the physical robot's LiDAR.
Not needed in simulation (LiDAR is a Gazebo sensor in lidar.xacro).

Requirements:
  sudo apt install ros-<distro>-rplidar-ros

Serial port:
  The default path targets a USB device connected via PCIe→USB on a
  Raspberry Pi 4. Update 'serial_port' to match your actual device path,
  e.g. '/dev/ttyUSB0' or '/dev/serial/by-id/<your-device>'.

Usage:
  ros2 launch gnanagamya rplidar.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([
        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[{
                # Update this path to match your hardware setup
                'serial_port': '/dev/serial/by-path/'
                               'platform-fd500000.pcie-pci-0000:01:00.0'
                               '-usb-0:1.3:1.0-port0',
                'frame_id':         'laser_frame',
                'angle_compensate': True,
                'scan_mode':        'Standard',
            }],
        ),
    ])
