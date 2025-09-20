/********************************************************************
* wabash/src/wabash.cpp
*
* Copyright (c) 2025  Stephen Rhodes
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*********************************************************************/

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "Thread.hpp"
#include "Payload.hpp"

namespace py = pybind11;

namespace wabash {

PYBIND11_MODULE(_wabash, m)
{
    m.doc() = "pybind11 parallel processing plugin";

    py::class_<Thread>(m, "Thread")
        .def(py::init<const std::string&>())
        .def("start", &Thread::start)
        .def("setPayload", &Thread::setPayload)
        .def_readwrite("name", &Thread::name)
        .def_readwrite("running", &Thread::running)
        .def_readwrite("callback", &Thread::callback)
        .def_readwrite("finish", &Thread::finish);
 
    py::class_<Payload>(m, "Payload", py::buffer_protocol())
        .def(py::init<int, int, int>())
        .def("show", &Payload::show)
        .def("width", &Payload::width)
        .def("height", &Payload::height)
        .def("depth", &Payload::depth)
        .def("stride", &Payload::stride)
        .def_buffer([](Payload &m) -> py::buffer_info {
            py::ssize_t element_size = sizeof(uint8_t);
            std::string fmt_desc =  py::format_descriptor<uint8_t>::format();
            std::vector<py::ssize_t> dims = { m.height(), m.width(), m.depth() };
            py::ssize_t ndim = dims.size();
            std::vector<py::ssize_t> strides = { m.stride(), ndim, 1 };
            return py::buffer_info(m.data(), element_size, fmt_desc, ndim, dims, strides);
        });

    m.attr("__version__") = "0.0.0";

}

}