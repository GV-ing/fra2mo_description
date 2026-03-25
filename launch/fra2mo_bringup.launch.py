import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():

    # 1. Configurazione per il Robot State Publisher (Legge l'URDF)
    fra2mo_description_dir = get_package_share_directory('fra2mo_description')
    xacro_file = os.path.join(fra2mo_description_dir, 'urdf', 'fra2mo.urdf.xacro')
    
    # Usa xacro per processare il file e generare la stringa XML del robot
    robot_description_content = Command(['xacro ', xacro_file])
    
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content, 'use_sim_time': False}] 
        # NOTA: use_sim_time è False perché ora usiamo il tempo reale del Raspberry!
    )

    # 2. Configurazione per il Micro-ROS Agent (Comunica con il Pico via USB)
    # Assumiamo che il Pico sia collegato alla porta /dev/ttyACM0
    micro_ros_agent_node = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        output='screen',
        arguments=['serial', '--dev', '/dev/ttyACM0', '-v6'] 
        # -v6 stampa log dettagliati, utile per il debug iniziale
    )

    # 3. (Futuro) Nodo del LiDAR reale
    # Lo aggiungeremo qui non appena mi dirai che modello di LiDAR possiedi!

    return LaunchDescription([
        robot_state_publisher_node,
        micro_ros_agent_node
    ])