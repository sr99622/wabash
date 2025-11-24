#ifndef ADAPTER_HPP
#define ADAPTER_HPP

namespace wabash
{

class Adapter
{
public:
    std::string name;
    std::string description;
    std::string ip_address;
    std::string gateway;
    std::string broadcast;
    std::string netmask;
    std::vector<std::string> dns;
    std::string mac_address;
    std::string type;
    bool dhcp;
    bool up;
    int priority;
};

}

#endif // ADAPTER_HPP

