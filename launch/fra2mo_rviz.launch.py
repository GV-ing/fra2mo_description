import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Package path
    pkg_share = get_package_share_directory('fra2mo_description')
    
    # URDF/Xacro files path
    xacro_file = os.path.join(pkg_share, 'urdf', 'fra2mo.urdf.xacro')
    
    # RViz configuration file path
    rviz_config_file = os.path.join(pkg_share, 'conf', 'fra2mo_conf_ros2_sim.rviz')

    # Robot description from xacro
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    # Robot State Publisher node,
    # not necessary since we are using Gazebo Harmonic to simulate the robot,
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    # Joint State Publisher node,
    # not necessary since we are using Gazebo Harmonic to simulate the robot,
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
        arguments=['-d', rviz_config_file]
    )

    #Joistick teleoperation node
    # not necessary since we already lounch it in 
    # fra2mo_gazebo.launch.py
    telop_node = Node(
        package='fra2mo_description',
        executable='joy_to_cmdvel',
        name='joy_to_cmdvel',
        output='screen',
        remappings=[('/cmd_vel', '/fra2mo/cmd_vel')]
    )
    #Reading joystick inputs Node
    # not necessary since we already lounch it in 
    # fra2mo_gazebo.launch.py
    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen'
    )


    return LaunchDescription([
        #robot_state_publisher_node,
        #joint_state_publisher_node,
        #telop_node,
        #joy_node,
        rviz_node
    ])
