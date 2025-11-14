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
#include "wabash.hpp"
#include "Thread.hpp"

namespace py = pybind11;

namespace wabash {

PYBIND11_MODULE(_wabash, m)
{
    m.doc() = "pybind11 parallel processing plugin";

    py::class_<Thread>(m, "Thread")
        .def(py::init<const std::string&, const std::string&>())
        .def("start", &Thread::start)
        .def_readwrite("counter", &Thread::counter)
        .def_readwrite("last_pts", &Thread::last_pts)
        .def_readwrite("detections", &Thread::detections)
        .def_readwrite("frame", &Thread::frame)
        .def_readwrite("name", &Thread::name)
        .def_readwrite("filename", &Thread::filename)
        .def_readwrite("running", &Thread::running)
        .def_readwrite("reconnect", &Thread::reconnect)
        .def_readwrite("finish", &Thread::finish)
        .def_readwrite("showError", &Thread::showError);
 
    py::class_<Frame>(m, "Frame", py::buffer_protocol())
        .def(py::init<>())
        .def(py::init<const Frame&>())
        .def("is_null", &Frame::is_null)
        .def("pts", &Frame::pts)
        .def("width", &Frame::width)
        .def("height", &Frame::height)
        .def("stride", &Frame::stride)
        .def("channels", &Frame::channels)
        .def("mb_samples", &Frame::nb_samples)
        .def_buffer([](Frame &m) -> py::buffer_info {
            if (m.height() == 0 && m.width() == 0) {
                return py::buffer_info(
                    m.data(),
                    sizeof(float),
                    py::format_descriptor<float>::format(),
                    1,
                    { m.nb_samples() * m.channels() },
                    { sizeof(float) }
                );
            }
            else {
                py::ssize_t element_size = sizeof(uint8_t);
                std::string fmt_desc =  py::format_descriptor<uint8_t>::format();
                std::vector<py::ssize_t> dims = { m.height(), m.width(), 3};
                py::ssize_t ndim = dims.size();
                std::vector<py::ssize_t> strides = { (long)(sizeof(uint8_t) * m.stride()), (py::ssize_t)(sizeof(uint8_t) * ndim), sizeof(uint8_t) };
                return py::buffer_info(m.data(), element_size, fmt_desc, ndim, dims, strides);
            }
        });

    py::class_<AVRational>(m, "AVRational")
        .def(py::init<>())
        .def_readwrite("num", &AVRational::num)
        .def_readwrite("den", &AVRational::den);

    m.attr("__version__") = "0.0.2";

}

}