import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    namespace = 'bot_1'

    # Package directories
    desc_pkg_share = get_package_share_directory('tortoisebot_description')
    ydlidar_pkg_share = get_package_share_directory('ydlidar_ros2_driver')

    # 1. State Publisher (URDF & TF Tree)
    state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(desc_pkg_share, 'launch', 'state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 2. YDLidar Driver (/bot_1/scan)
    ydlidar_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ydlidar_pkg_share, 'launch', 'ydlidar_launch.py')
        )
    )

    # Group included launch files under the namespace
    namespaced_includes = GroupAction(
        actions=[
            PushRosNamespace(namespace),
            state_publisher_cmd,
            ydlidar_cmd,
        ]
    )

    # 3. Differential Drive Controller (/bot_1/odom, /bot_1/cmd_vel)
    differential_node = Node(
        package='tortoisebot_firmware',
        executable='differential.py',
        name='differential_drive',
        namespace=namespace,
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 4. IMU Node (/bot_1/imu/data)
    imu_node = Node(
        package='tortoisebot_imu',
        executable='imu_node.py',
        name='imu_node',
        namespace=namespace,
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true'
        ),
        namespaced_includes,
        differential_node,
        imu_node,
    ])
