cmake_minimum_required(VERSION 3.15)
project(Cazadores_vision VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(ASIO_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/asio/include)
set(asio_FOUND True)
set(OPENCV_DIR "$ENV{HOME}/opencv/build")

find_package(OpenCV REQUIRED)
find_library(HUATENG_LIB NAMES MVSDK PATHS ${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/HuanTeng)

add_executable(${PROJECT_NAME} src/cazadores.cpp
src/Read_Camera.cpp
)

include_directories(${ASIO_INCLUDE_DIR})
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/Crow)
target_include_directories(${PROJECT_NAME} PRIVATE 
${OpenCV_INCLUDE_DIRS}
${CMAKE_SOURCE_DIR}/includes
${CAMERALIB})
target_link_libraries(${PROJECT_NAME} PRIVATE 
${OpenCV_LIBS}
${HUATENG_LIB}
)

target_link_libraries(${PROJECT_NAME} PRIVATE Crow::Crow)
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/public" 
     DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")