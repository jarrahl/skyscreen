cmake_minimum_required(VERSION 2.8.4)
project(skyscreen_receiver)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES receiver.cpp)
add_executable(skyscreen_receiver ${SOURCE_FILES})