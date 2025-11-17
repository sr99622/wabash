#*******************************************************************************
# wabash/CMakeLists.txt
#
# Copyright (c) 2025 Stephen Rhodes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#******************************************************************************/

cmake_minimum_required(VERSION 3.17)

project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DSOCKLEN_T=socklen_t -D__STDC_CONSTANT_MACROS")

list(PREPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)

if(WIN32)
    add_compile_options(/EHsc /MT)
endif()

find_package(FFmpeg REQUIRED)
#find_package(SDL2 REQUIRED)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_wabash 
    src/wabash.cpp
)

target_link_libraries(_wabash PRIVATE 
    FFmpeg::FFmpeg
#    SDL2::SDL2
)

if(WIN32)
    target_link_libraries(_wabash PRIVATE
        wsock32
        ws2_32
    )
endif()

target_include_directories(_wabash SYSTEM PUBLIC
    include
    include/media
    include/network
)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    message("-- Setting run_path for Linux binaries")
    set_target_properties(_wabash PROPERTIES
        BUILD_RPATH "$ORIGIN"
        BUILD_RPATH_USE_ORIGIN TRUE
        INSTALL_RPATH "$ORIGIN"
        INSTALL_RPATH_USE_ORIGIN TRUE
    )
endif()

install(TARGETS _wabash DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/wabash")
install(
    DIRECTORY ${CMAKE_SOURCE_DIR}/wabash/
    DESTINATION wabash
    FILES_MATCHING
    PATTERN "*"
)
