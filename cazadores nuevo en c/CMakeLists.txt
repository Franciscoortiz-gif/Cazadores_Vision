cmake_minimum_required(VERSION 3.15)
project(Cazadores_vision VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(FMT_DOC OFF CACHE INTERNAL "")
set(FMT_TEST OFF CACHE INTERNAL "")

set(OPENCV_DIR "$ENV{HOME}/opencv/build")

find_package(OpenCV REQUIRED)

add_executable(${PROJECT_NAME} src/cazadores.cpp)
add_subdirectory(3rdparty/fmt)
target_include_directories(${PROJECT_NAME} PRIVATE 
${OpenCV_INCLUDE_DIRS}
${CMAKE_SOURCE_DIR}/includes)
target_link_libraries(${PROJECT_NAME} PRIVATE ${OpenCV_LIBS})
target_link_libraries(${PROJECT_NAME} PRIVATE fmt::fmt)
