cmake_minimum_required(VERSION 3.10)
project(lab6_opencv CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED)
find_library(V4L2_LIB v4l2)

include_directories(include ${OpenCV_INCLUDE_DIRS})

set(SOURCES
    src/main.cpp
    src/CameraProvider.cpp
    src/KeyProcessor.cpp
    src/FrameProcessor.cpp
    src/Display.cpp
)

add_executable(lab6 ${SOURCES})
target_link_libraries(lab6 ${OpenCV_LIBS} ${V4L2_LIB})
