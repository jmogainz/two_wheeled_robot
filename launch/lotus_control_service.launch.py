# Author: Addison Sears-Collins
# Date: September 28, 2021
# Description: Launch a two-wheeled robot using the ROS 2 Navigation Stack. 
#              The spawning of the robot is performed by the Gazebo-ROS spawn_entity node.
#              The robot must be in both SDF and URDF format.
#              If you want to spawn the robot in a pose other than the default, be sure to set that inside
#              the nav2_params_path yaml file: amcl ---> initial_pose: [x, y, z, yaw]
# https://automaticaddison.com

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
  package_name = 'two_wheeled_robot'
  robot_name_in_model = 'two_wheeled_robot'
  default_launch_dir = 'launch'
  gazebo_models_path = 'models'
  map_file_path = 'maps/lotus_control_service_test_world/blank_map.yaml'
  nav2_params_path = 'params/regulated_velo.yaml'
  robot_localization_file_path = 'config/ekf_with_gps.yaml'
  rviz_config_file_path = 'rviz/cafe_world/nav2_config.rviz'
  sdf_model_path = 'models/two_wheeled_robot_description/lotus_model.sdf'
  urdf_file_path = 'urdf/robots/4wd.urdf.xacro'
  world_file_path = 'worlds/empty.world'
  
  # Pose where we want to spawn the robot
  spawn_x_val = '0.0'
  spawn_y_val = '0.0'
  spawn_z_val = '0.0'
  spawn_yaw_val = '0.0'

  ########## You do not need to change anything below this line ###############
  
  # Set the path to different files and folders.  
  # pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')   
  pkg_share = FindPackageShare(package=package_name).find(package_name)
  default_launch_dir = os.path.join(pkg_share, default_launch_dir)
  default_urdf_model_path = os.path.join(pkg_share, urdf_file_path)
  robot_localization_file_path = os.path.join(pkg_share, robot_localization_file_path) 
  default_rviz_config_path = os.path.join(pkg_share, rviz_config_file_path)
  world_path = os.path.join(pkg_share, world_file_path)
  # gazebo_models_path = os.path.join(pkg_share, gazebo_models_path)
  # os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path
  nav2_dir = FindPackageShare(package='nav2_bringup').find('nav2_bringup') 
  ublox_dir = FindPackageShare(package='ublox_gps').find('ublox_gps')
  vesc_dir = FindPackageShare(package='vesc_driver').find('vesc_driver')
  vesc_launch_dir = os.path.join(vesc_dir, 'launch')
  ublox_launch_dir = os.path.join(ublox_dir, 'launch')
  nav2_launch_dir = os.path.join(nav2_dir, 'launch') 
  sdf_model_path = os.path.join(pkg_share, sdf_model_path)
  static_map_path = os.path.join(pkg_share, map_file_path)
  nav2_params_path = os.path.join(pkg_share, nav2_params_path)
  nav2_bt_path = FindPackageShare(package='nav2_bt_navigator').find('nav2_bt_navigator')
  
  # Launch configuration variables specific to simulation
  autostart = LaunchConfiguration('autostart')
  headless = LaunchConfiguration('headless')
  namespace = LaunchConfiguration('namespace')
  map_yaml_file = LaunchConfiguration('map')
  params_file = LaunchConfiguration('params_file')
  rviz_config_file = LaunchConfiguration('rviz_config_file')
  sdf_model = LaunchConfiguration('sdf_model')
  urdf_model = LaunchConfiguration('urdf_model')
  use_namespace = LaunchConfiguration('use_namespace')
  use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
  use_rviz = LaunchConfiguration('use_rviz')
  use_sim_time = LaunchConfiguration('use_sim_time')
  use_simulator = LaunchConfiguration('use_simulator')
  world = LaunchConfiguration('world')
  
  # Map fully qualified names to relative ones so the node's namespace can be prepended.
  # In case of the transforms (tf), currently, there doesn't seem to be a better alternative
  # https://github.com/ros/geometry2/issues/32
  # https://github.com/ros/robot_state_publisher/pull/30
  # TODO(orduno) Substitute with `PushNodeRemapping`
  #              https://github.com/ros2/launch_ros/issues/56
  remappings = [('/tf', 'tf'),
                ('/tf_static', 'tf_static')]
  
  # Declare the launch arguments  
  declare_namespace_cmd = DeclareLaunchArgument(
    name='namespace',
    default_value='',
    description='Top-level namespace')

  declare_use_namespace_cmd = DeclareLaunchArgument(
    name='use_namespace',
    default_value='false',
    description='Whether to apply a namespace to the navigation stack')
        
  declare_autostart_cmd = DeclareLaunchArgument(
    name='autostart', 
    default_value='true',
    description='Automatically startup the nav2 stack')

  declare_map_yaml_cmd = DeclareLaunchArgument(
    name='map',
    default_value=static_map_path,
    description='Full path to map file to load')

  declare_params_file_cmd = DeclareLaunchArgument(
    name='params_file',
    default_value=nav2_params_path,
    description='Full path to the ROS2 parameters file to use for all launched nodes')
    
  declare_rviz_config_file_cmd = DeclareLaunchArgument(
    name='rviz_config_file',
    default_value=default_rviz_config_path,
    description='Full path to the RVIZ config file to use')

  # declare_sdf_model_path_cmd = DeclareLaunchArgument(
  #   name='sdf_model', 
  #   default_value=sdf_model_path, 
  #   description='Absolute path to robot sdf file')

  # declare_simulator_cmd = DeclareLaunchArgument(
  #   name='headless',
  #   default_value='False',
  #   description='Whether to execute gzclient')

  # declare_slam_cmd = DeclareLaunchArgument(
  #   name='slam',
  #   default_value='False',
  #   description='Whether to run SLAM')

  declare_urdf_model_path_cmd = DeclareLaunchArgument(
    name='urdf_model', 
    default_value=default_urdf_model_path, 
    description='Absolute path to robot urdf file')
    
  declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
    name='use_robot_state_pub',
    default_value='True',
    description='Whether to start the robot state publisher')

  declare_use_rviz_cmd = DeclareLaunchArgument(
    name='use_rviz',
    default_value='True',
    description='Whether to start RVIZ')
    
  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='false',
    description='Use simulation (Gazebo) clock if true')

  declare_use_simulator_cmd = DeclareLaunchArgument(
    name='use_simulator',
    default_value='false',
    description='Whether to start the simulator')

  # declare_world_cmd = DeclareLaunchArgument(
  #   name='world',
  #   default_value=world_path,
  #   description='Full path to the world model file to load')
   
  # Specify the actions

  # Start Gazebo server
  # start_gazebo_server_cmd = IncludeLaunchDescription(
  #   PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
  #   condition=IfCondition(use_simulator),
  #   launch_arguments={'world': world}.items())

  # # Start Gazebo client    
  # start_gazebo_client_cmd = IncludeLaunchDescription(
  #   PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
  #   condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless])))

  # Launch the robot
  # spawn_entity_cmd = Node(
  #   package='gazebo_ros',
  #   executable='spawn_entity.py',
  #   arguments=['-entity', robot_name_in_model,
  #              '-file', sdf_model,
  #                 '-x', spawn_x_val,
  #                 '-y', spawn_y_val,
  #                 '-z', spawn_z_val,
  #                 '-Y', spawn_yaw_val],
  #      output='screen')

  start_imu_publisher_cmd = Node(
    package="bno055_sensor",
    executable="bno055_sensor_node",
    arguments=["--ros-args", "-p", "i2c_address:=/dev/i2c-0"],
    output='screen'
  )

  start_ublox_gps_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(ublox_launch_dir, 'ublox_gps_node-launch.py')))

  start_vesc_driver_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(vesc_launch_dir, 'launch_vesc_driver.launch.py')))

  # Start the navsat transform node which converts GPS data into the world coordinate frame
  start_navsat_transform_cmd = Node(
    package='robot_localization',
    executable='navsat_transform_node',
    name='navsat_transform',
    output='screen',
    parameters=[robot_localization_file_path, 
    {'use_sim_time': use_sim_time}],
    remappings=[('imu', 'imu/data'),
                ('gps/fix', 'gps/fix'), 
                ('gps/filtered', 'gps/filtered'),
                ('odometry/gps', 'odometry/gps'),
                ('odometry/filtered', 'odometry/global')])

  # Start robot localization using an Extended Kalman filter...map->odom transform
  start_robot_localization_global_cmd = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_filter_node_map',
    output='screen',
    parameters=[robot_localization_file_path, 
    {'use_sim_time': use_sim_time}],
    remappings=[('odometry/filtered', 'odometry/global'),
                ('/set_pose', '/initialpose')])

  # Start robot localization using an Extended Kalman filter...odom->base_footprint transform
  start_robot_localization_local_cmd = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_filter_node_odom',
    output='screen',
    parameters=[robot_localization_file_path, 
    {'use_sim_time': use_sim_time}],
    remappings=[('odometry/filtered', 'odometry/local'),
                ('/set_pose', '/initialpose')])

  publish_map_to_odom_cmd = Node(package = "tf2_ros", 
                       executable = "static_transform_publisher",
                       arguments = ["0", "0", "0", "0", "0", "0", "map", "odom"])

  # Subscribe to the joint states of the robot, and publish the 3D pose of each link.
  start_robot_state_publisher_cmd = Node(
    condition=IfCondition(use_robot_state_pub),
    package='robot_state_publisher',
    executable='robot_state_publisher',
    namespace=namespace,
    parameters=[{'use_sim_time': use_sim_time, 
    'robot_description': Command(['xacro ', urdf_model])}],
    remappings=remappings,
    arguments=[default_urdf_model_path])

  start_joint_state_publisher_cmd = Node(
    package='joint_state_publisher',
    executable='joint_state_publisher',
    name='joint_state_publisher')

  # Launch RViz
  start_rviz_cmd = Node(
    condition=IfCondition(use_rviz),
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    output='screen',
    arguments=['-d', rviz_config_file])    

  # Launch the ROS 2 Navigation Stack
  start_ros2_navigation_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'bringup_launch.py')),
    launch_arguments = {'namespace': namespace,
                        'map': map_yaml_file,
                        'use_namespace': use_namespace,
                        'use_sim_time': use_sim_time,
                        'params_file': params_file,
                        'autostart': autostart}.items())

  # Create the launch description and populate
  ld = LaunchDescription()

  # Declare the launch options
  ld.add_action(declare_namespace_cmd)
  ld.add_action(declare_use_namespace_cmd)
  ld.add_action(declare_autostart_cmd)
  ld.add_action(declare_map_yaml_cmd)
  ld.add_action(declare_params_file_cmd)
  ld.add_action(declare_rviz_config_file_cmd)
  # ld.add_action(declare_sdf_model_path_cmd)
  # ld.add_action(declare_simulator_cmd)
  # ld.add_action(declare_slam_cmd)
  ld.add_action(declare_urdf_model_path_cmd)
  ld.add_action(declare_use_robot_state_pub_cmd)  
  ld.add_action(declare_use_rviz_cmd) 
  ld.add_action(declare_use_sim_time_cmd)
  # ld.add_action(declare_use_simulator_cmd)
  # ld.add_action(declare_world_cmd)

  # Add any actions
  # ld.add_action(start_gazebo_server_cmd)
  # ld.add_action(start_gazebo_client_cmd)

  # ld.add_action(spawn_entity_cmd)
  ld.add_action(start_imu_publisher_cmd)
  ld.add_action(start_ublox_gps_cmd)
  ld.add_action(start_vesc_driver_cmd)
  # ld.add_action(publish_map_to_odom_cmd)
  ld.add_action(start_robot_localization_global_cmd)
  ld.add_action(start_robot_localization_local_cmd)
  ld.add_action(start_robot_state_publisher_cmd)
  ld.add_action(start_joint_state_publisher_cmd)
  ld.add_action(start_navsat_transform_cmd)
  # ld.add_action(start_rviz_cmd)

  ld.add_action(start_ros2_navigation_cmd)

  return ld
