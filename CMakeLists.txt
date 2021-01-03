cmake_minimum_required(VERSION 3.0.2)
project(hydroponics)


find_package(catkin REQUIRED COMPONENTS 
  rospy
  std_msgs
  message_generation
)

## System dependencies are found with CMake's conventions
# find_package(Boost REQUIRED COMPONENTS system)



catkin_python_setup()


# Generate messages in the 'msg' folder
add_message_files(
  FILES
  Float64Stamped.msg
  LedTemperature.msg
  Ph.msg
  Ec.msg
)

# Generate services in the 'srv' folder
add_service_files(
  FILES
  RequestScalar.srv
  SetFloat.srv
  SetInt.srv
  SetRelay.srv
)


# Generate added messages and services with any dependencies listed here
generate_messages(
  DEPENDENCIES
  std_msgs  # Or other packages containing msgs
)

## Generate dynamic reconfigure parameters in the 'cfg' folder
# generate_dynamic_reconfigure_options(
#   cfg/DynReconf1.cfg
#   cfg/DynReconf2.cfg
# )


catkin_package(
  CATKIN_DEPENDS message_runtime
)
