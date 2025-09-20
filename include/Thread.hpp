/********************************************************************
* wabash/include/Thread.hpp
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

#ifndef THREAD_HPP
#define THREAD_HPP

#include <thread>
#include <sstream>
#include <functional>
#include <random>
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <vector>

#include "Payload.hpp"

namespace wabash {

std::vector<std::vector<int>> resolutions = { { 640,  360, 3},
                                              {1280,  720, 3},
                                              {1920, 1080, 3},
                                              {2560, 1440, 3},
                                              {3840, 2160, 3} };

class Thread {
public:
    std::function<bool(const Payload& payload, const std::string& arg)> callback = nullptr;
    std::function<void(const std::string& arg)> finish = nullptr;
    bool running = false;
    std::string name;

    Payload* payload{nullptr};

    Thread(const std::string& name) : name(name) { }

    ~Thread() {
        if (payload) delete payload;
        std::cout << "thread destructor called" << std::endl;
    }

    void setPayload(int w, int h, int d) {
        if (payload) delete payload;
        payload = new Payload(w, h, d);
    }

    void run() {
        try {
            while (running) {
                if (!payload) { 
                    std::vector<int> dims = resolutions[static_cast<int>(dist(gen) * 5 / 256)];
                    payload = new Payload(dims[0], dims[1], dims[2]);
                }
                else {
                    payload->refill();
                }
                if (callback) {
                    if (callback(*payload, name)) {
                        break;
                    }
                }
            }
            if (finish) finish(name);
        }
        catch (const std::exception& e) {
            std::cout << e.what() << std::endl;
        }
    }

    void start() {
        try {
            running = true;
            std::thread thread([&]() { run(); });
            thread.detach();
        }
        catch (const std::exception& e) {
            std::cout << e.what() << std::endl;
        }
    }
};

}

#endif // THREAD_HPP