/********************************************************************
* wabash/include/Payload.hpp
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

#ifndef PAYLOAD_HPP
#define PAYLOAD_HPP

#include <sstream>
#include <random>
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <memory>
#include <mutex>
#include <thread>

namespace wabash {

static thread_local std::mt19937 gen(std::random_device{}());
std::uniform_int_distribution<int> dist(0, 255);

class Payload {
private:
    std::shared_ptr<uint8_t> m_data;
    int m_width  {0};
    int m_height {0};
    int m_depth  {0};
    int m_size   {0};
    int m_stride {0};
    std::mutex mutex;

public:
    explicit Payload(int width, int height, int depth) :   
        m_width(width), 
        m_height(height), 
        m_depth(depth),
        m_size(width * height * depth),
        m_stride(width)
    {
        m_data = std::shared_ptr<uint8_t>(
            static_cast<uint8_t*>(std::malloc(m_size)),
            [](uint8_t* p) { std::free(p); }
        );
        if (!m_data) throw std::bad_alloc();
        std::generate_n(m_data.get(), m_size, [&]() {
            return static_cast<uint8_t>(dist(gen));
        });
    }

    ~Payload() {
        std::cout << "payload destructor called" << std::endl;
    }

    Payload(const Payload& other) : 
        m_width(other.m_width), 
        m_height(other.m_height), 
        m_depth(other.m_depth),
        m_size(other.m_size),
        m_stride(other.m_stride), 
        m_data(other.m_data) 
    {
        //std::cout << "payload copy constructor" << std::endl;
    }

    Payload& operator=(const Payload& other) 
    {
        //std::cout << "payload copy assignment" << std::endl;
        if (this != &other) {
            m_width = other.m_width;
            m_height = other.m_height;
            m_depth = other.m_depth;
            m_stride = other.m_stride;
            m_size = other.m_size;
            m_data = other.m_data;
        }
        return *this;
    }

    Payload(Payload&& other) noexcept : 
        m_width(other.m_width), 
        m_height(other.m_height), 
        m_depth(other.m_depth),
        m_stride(other.m_stride),
        m_size(other.m_size), 
        m_data(std::move(other.m_data)) 
    {
        //std::cout << "payload move constructor" << std::endl;
    }

    Payload& operator=(Payload&& other) noexcept 
    {
        //std::cout << "payload move assignment" << std::endl;
        if (this != &other) {
            m_width = other.m_width;
            m_height = other.m_height;
            m_depth = other.m_depth;
            m_stride = m_width;
            m_size = m_width * m_height * m_depth;
            m_data = std::move(other.m_data);
        }
        return *this;
    }

    void refill() {
        //std::lock_guard<std::mutex> lock(mutex);
        std::generate_n(m_data.get(), m_size, [&]() {
            return static_cast<uint8_t>(dist(gen));
        });
    }

    void acquire_lock() {
        mutex.lock();
    }

    void release_lock() {
        mutex.unlock();
    }

    void show() {
        std::stringstream str;
        for (int w = 0; w < m_width; w++) {
            for (int h = 0; h < m_height; h++) {
                for (int d = 0; d < m_depth; d++) {
                    size_t loc = w * m_width + h * m_height + d * m_depth;
                    str << std::hex << std::setw(2) << std::setfill('0') << (int)m_data.get()[loc] << " ";
                }
            }
        }
        std::cout << str.str() << std::endl;
    }

    int      width()  const { return m_width;      }
    int      height() const { return m_height;     }
    int      depth()  const { return m_depth;      }
    int      stride() const { return m_stride;     }
    size_t   size()   const { return m_size;       } 
    uint8_t* data()   const { return m_data.get(); }

};

}

#endif // PAYLOAD_HPP