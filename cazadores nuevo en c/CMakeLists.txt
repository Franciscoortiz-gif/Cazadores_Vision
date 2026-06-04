cmake_minimum_required(VERSION 3.15)
project(Cazadores_vision VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_C_COMPILER clang-23)
set(CMAKE_CXX_COMPILER clang++-23)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -O3)

set(OPENCV_DIR "$ENV{HOME}/opencv/build")

find_package(OpenCV REQUIRED)

add_executable(${PROJECT_NAME} src/cazadores.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE 
${OpenCV_INCLUDE_DIRS}
${CMAKE_SOURCE_DIR}/includes)
target_link_libraries(${PROJECT_NAME} PRIVATE ${OpenCV_LIBS})

