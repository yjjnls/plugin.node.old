cmake_minimum_required(VERSION 2.8.11)
project(case-converter-plugin)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_library(${PROJECT_NAME} SHARED converter.c)
#target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
