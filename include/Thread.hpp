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
#include <array>
#include <memory>

#include "wabash.hpp"

namespace wabash {

class Thread {
public:
    std::function<void(const std::string& arg)> finish = nullptr;
    std::function<void(const std::string& name, const std::string& msgShow, const std::string& msgLog, ErrorTag tag)> showError = nullptr;
    bool running = false;
    bool reconnect = false;
    std::string name;
    std::string filename;
    uint64_t counter = 0;
    uint64_t last_pts = AV_NOPTS_VALUE;
    Frame frame;
    std::vector<std::array<double, 4>> detections;

    Thread(const std::string& name, const std::string& filename) : name(name), filename(filename) {
        av_log_set_level(AV_LOG_QUIET);
    }

    ~Thread() { }

    void run() {
        try {
            Reader reader(filename);
            int duration = (int)(1000 / reader.fps()); 
            Decoder decoder(&reader, AVMEDIA_TYPE_VIDEO);
            Filter filter(&decoder, "format=rgb24");
            while (running) {
                Packet pkt = reader.get_packet();
                if (pkt.is_null()) {
                    running = false;
                    break;
                }
                if (pkt.stream_index() == reader.video_stream_index) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(40));
                    filter.GetFrame(pkt, frame);
                    counter++;
                }
            }
            //std::cout << "done" << std::endl;
        }
        catch (const Exception& e) {
            switch (e.tag) {
            case NO_SUCH_FILE_OR_DIRECTORY:
                if (showError) {
                    std::stringstream str;
                    str << filename << " : No such file or directory";
                    showError(name, str.str(), e.what(), NO_SUCH_FILE_OR_DIRECTORY);
                }
                break;
            case END_OF_FILE:
                std::cout << "EOF" << std::endl;
                break;
            default:
                std::cout << "exception occurred: " << e.what() << std::endl;        
            }
        }
        catch (const std::exception& e) {
            std::cout << "caught unhandled exception: " << e.what() << std::endl;
        }
        
        if (finish) finish(name);
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

    void sample(int arg) {
        try {
            std::cout << "THREAD SAMPLE FUNCTION" << std::endl;
            //throw std::runtime_error("ERROR");
            //throw Exception("TEST EXCEPTION", 0);
            //float b = 10 / arg;
            //std::cout << "the value of b is: " << b << std::endl;
            Reader* reader;
            if (reader)
                reader->read();
        }
        catch (const std::exception& e) {
            std::cout << e.what() << std::endl;
        }
    }
};

}

#endif // THREAD_HPP