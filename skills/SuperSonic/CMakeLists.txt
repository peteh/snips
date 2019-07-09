cmake_minimum_required(VERSION 3.1)
project(DeviceSwitch)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake_modules")

set(SOURCES
  src/Mosquitto.cpp  src/Mosquitto.h  
  src/RCSwitch.cpp  src/RCSwitch.h  
  src/SuperSonic.cpp  
  src/TcpServer.cpp  src/TcpServer.h
  src/sensors/DHT11Sensor.cpp  src/sensors/DHT11Sensor.h  
  src/sensors/UltraSonicSensorArray.cpp  src/sensors/UltraSonicSensorArray.h  
  src/sensors/UltraSonicSensor.cpp  src/sensors/UltraSonicSensor.h
  src/device/Device.cpp  src/device/Device.h
  src/device/RFDevice.cpp  src/device/RFDevice.h
  src/device/WOLDevice.cpp  src/device/WOLDevice.h
)
message("${SOURCES}")
add_executable(DeviceSwitch ${SOURCES})

add_definitions(-DRPI) 

find_package(Threads REQUIRED)
target_link_libraries(DeviceSwitch 
  Threads::Threads
  )

find_package(Mosquitto REQUIRED)
include_directories(${Mosquitto_INCLUDE_DIRS})
target_link_libraries(DeviceSwitch ${MOSQUITTO_LIBRARIES})

find_package(Mosquittopp REQUIRED)
include_directories(${Mosquittopp_INCLUDE_DIRS})
target_link_libraries(DeviceSwitch ${MOSQUITTOPP_LIBRARIES})

find_package(WiringPi REQUIRED)
include_directories(${WiringPi_INCLUDE_DIR})
target_link_libraries(DeviceSwitch ${WiringPi_LIBRARIES})

find_package(JsonCpp REQUIRED)
include_directories(${JsonCpp_INCLUDE_DIRS})
target_link_libraries(DeviceSwitch 
  JsonCpp::JsonCpp
  )


