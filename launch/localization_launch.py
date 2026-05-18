"""
localization_launch.py — Nav2 AMCL Localisation
================================================
Starts map_server + amcl + lifecycle_manager.
Requires a pre-built map (pass via 'map' argument).

Usage:
  ros2 launch gnanagamya localization_launch.py map:=/path/to/map.yaml
  ros2 launch gnanagamya localization_launch.py \\
      map:=/path/to/map.yaml use_sim_time:=true
"""

# Copyright (c) 2018 Intel Corporation
# Licensed under the Apache License, Version 2.0

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():

    bringup_dir = get_package_share_directory('gnanagamya')

    namespace      = LaunchConfiguration('namespace')
    map_yaml_file  = LaunchConfiguration('map')
    use_sim_time   = LaunchConfiguration('use_sim_time')
    autostart      = LaunchConfiguration('autostart')
    params_file    = LaunchConfiguration('params_file')
    lifecycle_nodes = ['map_server', 'amcl']

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    param_substitutions = {
        'use_sim_time':  use_sim_time,
        'yaml_filename': map_yaml_file,
    }

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key=namespace,
        param_rewrites=param_substitutions,
        convert_types=True,
    )

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),

        DeclareLaunchArgument(
            'namespace', default_value='',
            description='Top-level namespace'),

        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(bringup_dir, 'maps', 'map.yaml'),
            description='Full path to map YAML file'),

        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use Gazebo clock if true'),

        DeclareLaunchArgument(
            'autostart', default_value='true',
            description='Automatically start the nav2 lifecycle nodes'),

        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(bringup_dir, 'config', 'nav2_params.yaml'),
            description='Full path to nav2 parameters file'),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[configured_params],
            remappings=remappings),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[configured_params],
            remappings=remappings),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'autostart':    autostart},
                {'node_names':   lifecycle_nodes},
            ]),
    ])
