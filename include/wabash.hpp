#ifndef WABASH_HPP
#define WABASH_HPP

//#define SDL_MAIN_HANDLED

#include "Packet.hpp"
#include "Frame.hpp"
#include "Filter.hpp"
#include "Exception.hpp"
//#include "Display.hpp"
//#include "Audio.hpp"
#include "Reader.hpp"
#include "Decoder.hpp"
#include "Drain.hpp"
#include "Writer.hpp"

#include "Broadcaster.h"
#ifdef _WIN32
    #include "WinClient.h"
    #include "WinServer.h"
    #include "WinListener.h"
    #include "WinNetUtil.h"
#else
    #include "Client.h"
    #include "Server.h"
    #include "Listener.h"
#endif

#ifdef __APPLE__
    #include "MacNetUtil.h"
#endif

#ifdef __linux__
    #include "GnuNetUtil.h"
#endif

#endif // WABASH_HPP