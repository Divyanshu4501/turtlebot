import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

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

    # 2. YDLidar Driver (/scan)
    ydlidar_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ydlidar_pkg_share, 'launch', 'ydlidar_launch.py')
        )
    )

    # 3. Differential Drive Motor Controller & Wheel Odometry (/odom, /cmd_vel)
    differential_node = Node(
        package='tortoisebot_firmware',
        executable='differential.py',
        name='differential_drive',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 4. IMU Node (/imu/data)
    imu_node = Node(
        package='tortoisebot_imu',
        executable='imu_node.py',
        name='imu_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true'
        ),
        state_publisher_cmd,
        ydlidar_cmd,
        differential_node,
        imu_node,
    ])
