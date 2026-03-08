import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Package path
    pkg_share = get_package_share_directory('fra2mo_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    # URDF/Xacro files path
    xacro_file = os.path.join(pkg_share, 'urdf', 'fra2mo.xacro')
    
    # RViz configuration file path
    rviz_config_file = os.path.join(pkg_share, 'conf', 'fratomo_conf_ros2.rviz')

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    # Used to enable Gazebo simulation time
    # This way all nodes using time synchronize with Gazebo
    # instead of real time, avoiding synchronization issues 
    # between nodes and simulation
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Set the Gazebo resource path for meshes
    # GZ looks for model://package_name/...
    # Include both local workspace and realsense2_description paths
    realsense_share = get_package_share_directory('realsense2_description')
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.dirname(pkg_share) + ':' + os.path.dirname(realsense_share)
        # Points to .../share/ directories so model://package_name works
    )

    # Robot description from xacro
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    #  Include Gazebo Ignition launch file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': '-r empty.sdf'
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

    # Spawn robot in Gazebo Ignition
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'fratomo',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ]
    )

    # Bridge for Gazebo Ignition <-> ROS 2 topics
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
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/depth_camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/depth_camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/depth_camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/depth_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
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

    # Static transform to correct depth camera frame orientation if needed
    # This publishes identity transform - adjust rpy values if points are rotated
    depth_camera_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='depth_camera_static_tf',
        arguments=['0', '0', '0', '0', '0', '0', 'd435_link', 'camera_depth_correct_frame']
    )

    return LaunchDescription([
        declare_use_sim_time,
        gz_resource_path,
        gazebo,
        robot_state_publisher_node,
        spawn_entity_node,
        gz_bridge,
        joint_state_publisher_node,
        depth_camera_tf,
        #rviz_node
    ])
