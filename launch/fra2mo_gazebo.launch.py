import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Package paths
    pkg_share = get_package_share_directory('fra2mo_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    # URDF/Xacro files path
    xacro_file = os.path.join(pkg_share, 'urdf', 'fra2mo.urdf.xacro')
    
    # RViz configuration file path (Corretto errore di battitura 'fratomo')
    rviz_config_file = os.path.join(pkg_share, 'conf', 'fra2mo_conf_ros2.rviz')

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
    )

    # Set the Gazebo resource path for meshes and models
    realsense_share = get_package_share_directory('realsense2_description')
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(pkg_share, 'worlds') + ':' + os.path.join(pkg_share, 'models') + ':' + os.path.dirname(pkg_share) + ':' + os.path.dirname(realsense_share)
    )

    # Robot description from xacro
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    # Include Gazebo Harmonic launch file
    gazebo = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={
                'gz_args': '-r leonardo_race_field.sdf'
            }.items()
        )

    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }]
    )

    # Spawn robot in Gazebo Harmonic
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'fra2mo',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ]
    )

    # Bridge for Gazebo Harmonic <-> ROS 2 topics
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/model/fra2mo/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/depth_camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/depth_camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/depth_camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/depth_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
        ],
        remappings=[
            ('/model/fra2mo/tf', '/tf')
        ]
    )

    # Joint State Publisher GUI node
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    telop_node = Node(
        package='fra2mo_description',
        executable='joy_to_cmdvel',
        name='joy_to_cmdvel',
        output='screen'
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen'
    )

    return LaunchDescription([
        declare_use_sim_time,
        gz_resource_path,
        gazebo,
        robot_state_publisher_node,
        spawn_entity_node,
        gz_bridge,
        joint_state_publisher_node,
        joy_node,
        telop_node,
        #rviz_node
    ])