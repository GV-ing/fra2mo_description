
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    # 1. Configurazione per il Robot State Publisher (Legge l'URDF)
    fra2mo_description_dir = get_package_share_directory('fra2mo_description')
    xacro_file = os.path.join(fra2mo_description_dir, 'urdf', 'fra2mo.urdf.xacro')
    
    # Usa xacro per processare il file e generare la stringa XML del robot
    robot_description_content = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)
    
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content, 'use_sim_time': False}]
        # NOTA: use_sim_time è False perché ora usiamo il tempo reale del Raspberry!
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': False}]
    )

    return LaunchDescription([
        joint_state_publisher_node,
        robot_state_publisher_node
    ])