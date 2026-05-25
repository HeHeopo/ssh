import os
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.conditions import IfCondition
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction


def generate_launch_description():
    package_name = 'snowbot123'

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='false')

    declare_rviz = DeclareLaunchArgument(
        'rviz', default_value='True')

    declare_nav2 = DeclareLaunchArgument(
        'nav2', default_value='False')

    declare_slam = DeclareLaunchArgument(
        'slam', default_value='False')

    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz = LaunchConfiguration('rviz')
    nav2 = LaunchConfiguration('nav2')
    slam = LaunchConfiguration('slam')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    odom_tf_bridge = Node(
        package='snowbot',
        executable='odom_tf_bridge.py',
        name='odom_tf_bridge',
        output='screen',
    )


    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'),
                         'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': os.path.join(
                get_package_share_directory(package_name),
                'config', 'slam_toolbox_mapping.yaml'),
        }.items(),
        condition=IfCondition(slam)
    )


    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('nav2_bringup'),
                         'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'autostart': 'true',
            'params_file': os.path.join(
                get_package_share_directory(package_name),
                'config', 'nav2_slam_params.yaml'),
            'map': '',
        }.items(),
        condition=IfCondition(nav2)
    )

    rviz_config = os.path.join(get_package_share_directory(package_name), 'rviz', 'bot.rviz')
    rviz_node = GroupAction(
        condition=IfCondition(rviz),
        actions=[Node(
            package='rviz2', executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        )]
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_rviz,
        declare_nav2,
        declare_slam,

        rsp,
        odom_tf_bridge,
        slam_toolbox,
        nav2_launch,
        rviz_node,
    ])
