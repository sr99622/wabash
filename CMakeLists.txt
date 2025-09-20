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

project(wabash VERSION 0.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D__STDC_CONSTANT_MACROS")

if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    add_compile_options(/EHsc /MT)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
    set(BUILD_SHARED_LIBS TRUE)
endif()

add_definitions(-w)

add_subdirectory(pybind11)

pybind11_add_module(_wabash 
    src/wabash.cpp
)

target_include_directories(_wabash SYSTEM PUBLIC
    include
)

install(TARGETS _wabash DESTINATION wabash)
install(FILES wabash/__init__.py DESTINATION wabash)