cmake_minimum_required(VERSION 3.8)
project(fra2mo_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install the necessary folders 
install(DIRECTORY
  urdf
  meshes
  launch
  conf
  meshes
  models
  worlds
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

#Install the joy_to_cmdvel script
ament_package()
install(
  PROGRAMS src/joy_to_cmdvel.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME joy_to_cmdvel
)
