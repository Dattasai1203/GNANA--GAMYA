"""
online_async_launch.py — SLAM Toolbox (Online Async)
======================================================
Launches slam_toolbox in online asynchronous mode for either:
  - Mapping  : build a new occupancy grid map while driving
  - Localisation: localise within a previously saved map
                  (controlled by mapper_params_online_async.yaml → mode)

Requirements:
  sudo apt install ros-<distro>-slam-toolbox

Usage:
  # Simulation (use_sim_time=true by default)
  ros2 launch gnanagamya online_async_launch.py

  # Real robot
  ros2 launch gnanagamya online_async_launch.py use_sim_time:=false

  # Custom params file
  ros2 launch gnanagamya online_async_launch.py \\
      params_file:=/path/to/your_params.yaml
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from nav2_common.launch import HasNodeParams


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file  = LaunchConfiguration('params_file')

    default_params_file = os.path.join(
        get_package_share_directory('gnanagamya'),
        'config', 'mapper_params_online_async.yaml',
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use Gazebo simulation clock')

    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to slam_toolbox parameters file')

    # Fall back to default params if the provided file lacks slam_toolbox section
    has_node_params    = HasNodeParams(source_file=params_file,
                                       node_name='slam_toolbox')
    actual_params_file = PythonExpression([
        '"', params_file, '" if ', has_node_params,
        ' else "', default_params_file, '"',
    ])

    log_param_change = LogInfo(
        msg=['Provided params_file ', params_file,
             ' has no slam_toolbox params. Using default: ', default_params_file],
        condition=UnlessCondition(has_node_params),
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[actual_params_file, {'use_sim_time': use_sim_time}],
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_params_file)
    ld.add_action(log_param_change)
    ld.add_action(slam_node)
    return ld
