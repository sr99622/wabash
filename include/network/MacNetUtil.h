#ifndef MACNETUTIL_HPP
#define MACNETUTIL_HPP

#include <arpa/inet.h>
#include <unistd.h>
#include <ifaddrs.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/sysctl.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netdb.h>
#include <net/if.h>
#include <net/if_dl.h>
#include <net/if_media.h>
#include <net/route.h>
#include <netinet/in.h>
#include <math.h>
#include <stdint.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <map>
#include <iomanip>
#include <cstdlib>
#include <cstring>
#include <string>
#include <SystemConfiguration/SystemConfiguration.h>
#include <CoreFoundation/CoreFoundation.h>

// Compute sockaddr padded size (macOS-safe)
#ifndef SA_SIZE
#define SA_SIZE(sa)  \
    ( ((sa)->sa_len > 0) ? \
      (1 + (((sa)->sa_len - 1) | (sizeof(uint32_t) - 1))) : \
      sizeof(uint32_t) )
#endif


namespace wabash 
{

class NetUtil {
public:


    NetUtil() { }
    ~NetUtil() { }

    void printInterfaceFlags(unsigned int flags) const {
        if (flags & IFF_UP)           std::cout << "UP ";
        if (flags & IFF_RUNNING)      std::cout << "RUNNING ";
        if (flags & IFF_LOOPBACK)     std::cout << "LOOPBACK ";
        if (flags & IFF_BROADCAST)    std::cout << "BROADCAST ";
        if (flags & IFF_POINTOPOINT)  std::cout << "P2P ";
        if (flags & IFF_MULTICAST)    std::cout << "MULTICAST ";
        if (flags & IFF_PROMISC)      std::cout << "PROMISC ";
        std::cout << std::endl;
    }

    std::vector<std::string> getIPAddress() const {
        char buf[128] = { 0 };
        std::vector<std::string> result;
        /*
        char *address;
        struct ifaddrs *interfaces = NULL;
        struct ifaddrs *ifa = NULL;
        int success = 0;
        success = getifaddrs(&interfaces);
        if (success == 0) {
            ifa = interfaces;
            while (ifa != NULL) {

                sa_family_t fam = ifa->ifa_addr->sa_family;


                
                if (fam == AF_LINK) {
                    struct sockaddr_dl *sdl = (struct sockaddr_dl *)ifa->ifa_addr;
                    unsigned char* ptr = (unsigned char *)LLADDR(sdl);
                    
                    printf("Interface: %s, MAC Address: %02x:%02x:%02x:%02x:%02x:%02x\n",
                        ifa->ifa_name, *ptr, *(ptr+1), *(ptr+2), *(ptr+3), *(ptr+4), *(ptr+5));             
                }
                ifa = ifa->ifa_next;
            }
        }
        freeifaddrs(interfaces);
        */
        return result;
    }

    std::map<std::string, int> getActiveNetworkInterfaces() const {
        std::map<std::string, int> result;

        CFArrayRef ifs = SCNetworkInterfaceCopyAll();
        CFIndex count = CFArrayGetCount(ifs);
        std::cout << "interface count: " << count << std::endl;
        for (CFIndex i = 0; i < count; i++) {
            SCNetworkInterfaceRef item = (SCNetworkInterfaceRef)CFArrayGetValueAtIndex(ifs, i);
            std::string bsd = getStringFromRef(SCNetworkInterfaceGetBSDName(item));
            std::string displayName = getStringFromRef(SCNetworkInterfaceGetLocalizedDisplayName(item));
            std::string ip_address = getIPAddressForName(bsd);
            int priority = getInterfacePriority(bsd);
            std::string if_type = getStringFromRef(SCNetworkInterfaceGetInterfaceType(item));
            std::string hardware = getStringFromRef(SCNetworkInterfaceGetHardwareAddressString(item));
            CFArrayRef protocols = SCNetworkInterfaceGetSupportedProtocolTypes(item);
            std::string serviceID = getServiceIDForInterface(bsd);
            bool dhcp = dhcpEnabled(serviceID); 
            std::vector<std::string> dns = dnsForService(serviceID);
            std::cout << "bsd name:   " << bsd << "\n"
                      << "display:    " << displayName << "\n"
                      << "ip address: " << ip_address << "\n"
                      << "if_type:    " << if_type << "\n"
                      << "priority:   " << (priority < 0 ? "" : std::to_string(priority)) << "\n"
                      << "hardware:   " << hardware << "\n"
                      << "service:    " << serviceID << "\n"
                      << "dhcp:       " << dhcp << "\n";
            for (int j = 0; j < dns.size(); j++)
                std::cout << "dns " << j << ":      " << dns[j] << "\n";
            std::cout << std::endl;
            std::cout << "GATEWAY: " << gateway(bsd) << std::endl;
        }
        //CFShow(ifs);
        //oldSchoolInterfaces();
        //printInterfacePriority();
        //std::string gtwy = gateway();
        runShellCmd("");
        return result;
    }

    void runShellCmd(const std::string& cmd) const
    {
        std::array<char, 128> buffer;
        std::string result;
        // Open a pipe to the command, "r" indicates reading the output
        FILE* pipe = popen("netstat -rn | grep default | grep en0", "r");
        if (!pipe) {
            throw std::runtime_error("popen() failed!");
        }
        try {
            // Read the output line by line
            while (std::fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
                result += buffer.data();
            }
        } catch (...) {
            pclose(pipe);
            throw;
        }
        // Close the pipe and get the return status
        pclose(pipe);

        std::cout << "Output of 'ls -l':\n" << result;

    }

    std::string gateway(const std::string& name) const {
        std::string result;
        SCDynamicStoreRef store = nullptr;
        CFDictionaryRef globalIPv4 = nullptr;
        CFStringRef interfaceKey = nullptr;
        CFDictionaryRef interfaceIPv4 = nullptr;
        CFStringRef bsd = nullptr;
        try {
            if (name.empty())
                throw std::runtime_error("empty name");

            bsd = CFStringCreateWithCString(kCFAllocatorDefault, name.c_str(), kCFStringEncodingUTF8);

            if (!(interfaceKey = CFStringCreateWithFormat(NULL, NULL, CFSTR("State:/Network/Interface/%@/IPv4"), bsd)))
                throw std::runtime_error("CFStringCreateWithFormat returned nullptr");
            
            if (!(interfaceIPv4 = (CFDictionaryRef)SCDynamicStoreCopyValue(store, interfaceKey)))
                throw std::runtime_error("SCDynamicStoreCopyValue returned nullptr");

            CFShow(interfaceIPv4);
            
            CFArrayRef subnetMasks = (CFArrayRef)CFDictionaryGetValue(interfaceIPv4, CFSTR("SubnetMasks"));
            CFIndex count = CFArrayGetCount(subnetMasks);
            for (CFIndex i = 0; i < count; i++) {
                std::string mask = getStringFromRef((CFStringRef)CFArrayGetValueAtIndex(subnetMasks, i));
                std::cout << "mask: " << mask << std::endl;
            }
            CFArrayRef addresses = (CFArrayRef)CFDictionaryGetValue(interfaceIPv4, CFSTR("Addresses"));
            count = CFArrayGetCount(addresses);
            for (CFIndex i = 0; i < count; i++) {
                std::string address = getStringFromRef((CFStringRef)CFArrayGetValueAtIndex(addresses, i));
                std::cout << "address: " << address << std::endl;
            }
            CFArrayRef broadcastAddresses = (CFArrayRef)CFDictionaryGetValue(interfaceIPv4, CFSTR("BroadcastAddresses"));
            count = CFArrayGetCount(broadcastAddresses);
            for (CFIndex i = 0; i < count; i++) {
                std::string broadcastAddress = getStringFromRef((CFStringRef)CFArrayGetValueAtIndex(broadcastAddresses, i));
                std::cout << "broadcastAddress: " << broadcastAddress << std::endl;
            }
            
            if (!(store = SCDynamicStoreCreate(nullptr, CFSTR("gateway"), nullptr, nullptr)))
                throw std::runtime_error("SCDynamicStoreCreate returned nullptr");
            if (!(globalIPv4 = (CFDictionaryRef)SCDynamicStoreCopyValue(store, CFSTR("State:/Network/Global/IPv4"))))
                throw std::runtime_error("SCDynamicStoreCopyValue returned nullptr");
            CFShow(globalIPv4);
            CFStringRef router = (CFStringRef)CFDictionaryGetValue(globalIPv4, CFSTR("Router"));
            std::cout << "router: " << getStringFromRef(router) << std::endl;
            
        }
        catch (const std::exception& e) {
            std::cout << "gateway error: " << e.what() << std::endl;
        }

        if (store) CFRelease(store);
        if (globalIPv4) CFRelease(globalIPv4);
        if (interfaceIPv4) CFRelease(interfaceIPv4);
        if (interfaceKey) CFRelease(interfaceKey);
        if (bsd) CFRelease(bsd);
        return result;
    }

    std::string getIPAddressForName(const std::string& name) const
    {
        struct ifaddrs *ifaddr = nullptr;
        std::string ip_address;

        try {
            if (name.empty()) throw std::runtime_error("empty name");
            if (getifaddrs(&ifaddr) == -1) throw std::runtime_error("getifaddr failure");
            for (struct ifaddrs *ifa = ifaddr; ifa != nullptr; ifa = ifa->ifa_next) {
                if (ifa->ifa_addr == nullptr)
                    continue;

                if (ifa->ifa_addr->sa_family == AF_INET && name == ifa->ifa_name) {
                    ip_address = inet_ntoa(((struct sockaddr_in *)ifa->ifa_addr)->sin_addr);
                } 
            }
        }
        catch (const std::exception& e) {
            std::cout << "getIPAddressForName error: " << e.what() << std::endl;
        }

        if (ifaddr) freeifaddrs(ifaddr);
        return ip_address;
    }

    void oldSchoolInterfaces() const
    {
        struct ifaddrs *ifaddr;
        int family, s;
        char host[NI_MAXHOST];

        if (getifaddrs(&ifaddr) == -1) {
            printf("Error: getifaddrs failed - %s\n", strerror(errno));
            return;
        }

        for (struct ifaddrs *ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
            if (ifa->ifa_addr == NULL)
                continue;

            family = ifa->ifa_addr->sa_family;

            if (family == AF_INET ) {
                std::string address = inet_ntoa(((struct sockaddr_in *)ifa->ifa_addr)->sin_addr);
                std::cout << "address: " << address <<std::endl;
                std::cout << "name: " << ifa->ifa_name << std::endl;
                std::cout << "data: " << ifa->ifa_data << std::endl;
                std::cout << "flags: " << ifa->ifa_flags << std::endl;
                printInterfaceFlags(ifa->ifa_flags);
            } 
        }
        freeifaddrs(ifaddr);
    }

    int getInterfacePriority(const std::string& name) const
    {
        SCPreferencesRef prefs = nullptr;
        SCNetworkSetRef set = nullptr;
        CFArrayRef order = nullptr;
        int priority = -1;

        try {
            if (name.empty()) 
                throw std::runtime_error("empty name");

            if (!(prefs = SCPreferencesCreate(NULL, CFSTR("ifprio"), NULL)))
                throw std::runtime_error("NULL");

            if (!(set = SCNetworkSetCopyCurrent(prefs)))
                throw std::runtime_error("NULL");

            if (!(order = SCNetworkSetGetServiceOrder(set)))
                throw std::runtime_error("NULL");

            for (CFIndex i = 0; i < CFArrayGetCount(order); i++) {
                CFStringRef sid = (CFStringRef)CFArrayGetValueAtIndex(order, i);
                SCNetworkServiceRef service = SCNetworkServiceCopy(prefs, sid);
                SCNetworkInterfaceRef iface = SCNetworkServiceGetInterface(service);
                CFStringRef bsdName = SCNetworkInterfaceGetBSDName(iface);
                if (!bsdName) continue;

                if (name == getStringFromRef(bsdName))
                    priority = i;
            }
        }
        catch (const std::exception& e) {
            std::cout << "getInterfacePriority error: " << e.what() << std::endl;
        }

        if (set) CFRelease(set);
        if (prefs) CFRelease(prefs);
        if (order) CFRelease(order);

        return priority;
    }

    std::string getServiceIDForInterface(const std::string& if_name) const 
    {
        std::string result;
        SCPreferencesRef prefs = nullptr;
        CFArrayRef services = nullptr;

        try {
            if (!(prefs = SCPreferencesCreate(NULL, CFSTR("NetworkServiceLister"), NULL)))
                throw std::runtime_error("SCPreferencesCreate return nullptr");
            if (!(services = SCNetworkServiceCopyAll(prefs)))
                throw std::runtime_error("SCNetworkServiceCopyAll returned nullptr");

            CFIndex count = CFArrayGetCount(services);
            for (CFIndex i = 0; i < count; i++) {
                SCNetworkServiceRef service = (SCNetworkServiceRef)CFArrayGetValueAtIndex(services, i);
                CFStringRef serviceID = SCNetworkServiceGetServiceID(service);
                SCNetworkInterfaceRef iface = SCNetworkServiceGetInterface(service);
                if (!iface) continue;
                CFStringRef bsdName = SCNetworkInterfaceGetBSDName(iface);
                if (!bsdName) continue;
                if (if_name == getStringFromRef(bsdName)) {
                    result = getStringFromRef(serviceID);
                }
            }
        }
        catch (const std::exception& e) {
            std::cout << "getServiceIDForInterface error: " << e.what() << std::endl;
        }

        if (prefs) CFRelease(prefs);
        if (services) CFRelease(services);
        return result;
    }

    std::string getStringFromRef(CFStringRef arg) const 
    {
        char buf[1024];
        CFStringGetCString(arg, buf, sizeof(buf), kCFStringEncodingUTF8);
        return buf;
    }

    bool dhcpEnabled(const std::string& serviceID) const
    {
        SCDynamicStoreRef store = nullptr;
        CFDictionaryRef dhcpInfo = nullptr;
        CFStringRef dhcpKey = nullptr;
        bool result = false;

        try {
            if (serviceID.empty())
                throw std::runtime_error("empty service id");
            // Build key: State:/Network/Service/<service-id>/DHCP
            dhcpKey = CFStringCreateWithFormat(
                NULL, NULL,
                CFSTR("State:/Network/Service/%@/DHCP"),
                CFStringCreateWithCString(nullptr, serviceID.c_str(), kCFStringEncodingUTF8)
            );

            if (!(store = SCDynamicStoreCreate(NULL, CFSTR("dhcp-reader"), NULL, NULL)))
                throw std::runtime_error("SCDynamicStoreCreate returned nullptr");
            if (!(dhcpInfo = (CFDictionaryRef)SCDynamicStoreCopyValue(store, dhcpKey)))
                throw std::runtime_error("dhcp returned nullptr");

            //std::cout << "show dhcp info" << std::endl;
            //CFShow(dhcpInfo);
            result = true;
            /*
            CFIndex count = CFDictionaryGetCount(dhcpInfo);
            std::cout << "dictionary count: " << count << std::endl;

            std::vector<const void*> keys(count);
            std::vector<const void*> values(count);
            CFDictionaryGetKeysAndValues(dhcpInfo, keys.data(), values.data());
            for (CFIndex i = 0; i < count; i++) {
                CFStringRef key = (CFStringRef)keys[i];
                CFTypeRef value = values[i];
                //std::cout << "KEY: " << key << std::endl;
                char buf[64];
                CFStringGetCString(key, buf, sizeof(buf), kCFStringEncodingUTF8);
                std::cout << "BUF: " << buf << std::endl;
                std::string friendlyName = dhcpOptionFriendlyNames[buf];
                std::cout << "friendly name: " << friendlyName << std::endl;
                if (CFGetTypeID(value) == CFDataGetTypeID()) {
                    CFDataRef data = (CFDataRef)value;
                    const UInt8* b = CFDataGetBytePtr(data);
                    CFIndex len = CFDataGetLength(data);
                    std::cout << "LEN: " << len << std::endl;
                    if (len == 4) {
                        printf("%u.%u.%u.%u\n", b[0], b[1], b[2], b[3]);
                    }
                    else {
                        printf("(%ld bytes raw data)\n", len);
                        std::stringstream str;
                        for (int j = 0; j < len; j++) {
                            str << std::uppercase << std::hex << std::setw(2) << std::setfill('0') << (int)b[j];
                            if (j < len - 1) str << "-";
                        }
                        std::cout << "STR: " << str.str() << std::endl;
                        std::cout << "RAW: " << b << std::endl;
                    }
                }
                else if (CFGetTypeID(value) == CFNumberGetTypeID()) {
                    int num = 0;
                    CFNumberGetValue((CFNumberRef)value, kCFNumberIntType, &num);
                    printf("$d\n", num);
                }
                else {
                    CFShow(value);
                }
            }
            */
        }
        catch (const std::exception& e) {
            //std::cout << "ERROR: " << e.what() << std::endl;
        }

        if (dhcpInfo) CFRelease(dhcpInfo);
        if (store) CFRelease(store);
        if (dhcpKey) CFRelease(dhcpKey);
        return result;
    }

    std::string getDefaultGateway() const
    {
        int mib[6] = {
            CTL_NET,
            PF_ROUTE,
            0,
            AF_INET,
            NET_RT_FLAGS,
            RTF_GATEWAY
        };

        size_t len = 0;
        if (sysctl(mib, 6, NULL, &len, NULL, 0) < 0)
            return "";

        char* buf = (char*)malloc(len);
        if (!buf) return "";

        if (sysctl(mib, 6, buf, &len, NULL, 0) < 0) {
            free(buf);
            return "";
        }

        char* end = buf + len;
        char* next = buf;

        while (next < end) {
            struct rt_msghdr* rtm = (struct rt_msghdr*)next;
            struct sockaddr* sa = (struct sockaddr*)(rtm + 1);

            struct sockaddr_in* gateway = nullptr;
            struct sockaddr_in* dest = nullptr;

            for (int i = 0; i < RTAX_MAX; i++) {
                if (rtm->rtm_addrs & (1 << i)) {

                    if (sa->sa_family == AF_INET) {
                        if (i == RTAX_GATEWAY)
                            gateway = (struct sockaddr_in*)sa;
                        else if (i == RTAX_DST)
                            dest = (struct sockaddr_in*)sa;
                    }

                    sa = (struct sockaddr*)((char*)sa + SA_SIZE(sa));
                }
            }

            if (gateway && dest && dest->sin_addr.s_addr == 0) {
                char addr[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &gateway->sin_addr, addr, sizeof(addr));
                free(buf);
                return addr;
            }

            next += rtm->rtm_msglen;
        }

        free(buf);
        return "";
    }

    bool isInterfaceUp(const std::string& ifname) const
    {
        struct ifaddrs* ifaddr;

        if (getifaddrs(&ifaddr) == -1)
            return false;

        bool up = false;

        for (struct ifaddrs* ifa = ifaddr; ifa; ifa = ifa->ifa_next) {
            if (!ifa->ifa_name) continue;

            if (ifname == ifa->ifa_name) {
                printFlags(ifa->ifa_flags);
                std::cout << std::endl;
                if (ifa->ifa_flags & (IFF_UP | IFF_RUNNING))
                    up = true;
                break;
            }
        }

        freeifaddrs(ifaddr);
        return up;
    }

    bool interfaceHasLink(const char* ifname) const {
        int s = socket(AF_INET, SOCK_DGRAM, 0);
        if (s < 0) return false;

        struct ifmediareq ifm;
        memset(&ifm, 0, sizeof(ifm));
        strncpy(ifm.ifm_name, ifname, sizeof(ifm.ifm_name));

        if (ioctl(s, SIOCGIFMEDIA, &ifm) < 0) {
            close(s);
            return false;
        }
        close(s);

        // Check status
        if (ifm.ifm_status & IFM_AVALID) {
            if (ifm.ifm_status & IFM_ACTIVE)
                return true;   // cable plugged, link negotiated
        }
        return false;
    }

    void printFlags(unsigned int flags) const
    {
        struct { unsigned int flag; const char* name; } list[] = {
            {IFF_UP, "UP"},
            {IFF_BROADCAST, "BROADCAST"},
            {IFF_DEBUG, "DEBUG"},
            {IFF_LOOPBACK, "LOOPBACK"},
            {IFF_POINTOPOINT, "POINTOPOINT"},
            {IFF_NOTRAILERS, "NOTRAILERS"},
            {IFF_RUNNING, "RUNNING"},
            {IFF_NOARP, "NOARP"},
            {IFF_PROMISC, "PROMISC"},
            {IFF_ALLMULTI, "ALLMULTI"},
            {IFF_SIMPLEX, "SIMPLEX"},
            {IFF_LINK0, "LINK0"},
            {IFF_LINK1, "LINK1"},
            {IFF_LINK2, "LINK2"},
            {IFF_MULTICAST, "MULTICAST"},
        };

        for (auto& f : list) {
            if (flags & f.flag)
                std::cout << f.name << " ";
        }
    }

    std::vector<std::string> dnsForService(const std::string& serviceID) const {
        SCDynamicStoreRef store = nullptr;
        CFDictionaryRef dnsInfo = nullptr;
        CFStringRef dnsKey = nullptr;
        CFArrayRef servers = nullptr;
        std::vector<std::string> result;
        
        try {
            if (serviceID.empty())
                throw std::runtime_error("service id is empty");
            if (!(store = SCDynamicStoreCreate(nullptr, CFSTR("dns-reader"), nullptr, nullptr)))
                throw std::runtime_error("SCDynamicStoreCreate returned nullptr");

            CFStringRef dnsKey = CFStringCreateWithFormat(
                nullptr, nullptr,
                CFSTR("State:/Network/Service/%@/DNS"),
                CFStringCreateWithCString(nullptr, serviceID.c_str(), kCFStringEncodingUTF8)
            );

            if (!(dnsInfo = (CFDictionaryRef)SCDynamicStoreCopyValue(store, dnsKey)))
                throw std::runtime_error("dnsInfo returned nullptr");

            if (!(servers = (CFArrayRef)CFDictionaryGetValue(dnsInfo, CFSTR("ServerAddresses"))))
                throw std::runtime_error("servers returned nullptr");

            CFIndex count = CFArrayGetCount(servers);
            for (CFIndex i = 0; i < count; i++) {
                CFStringRef server = (CFStringRef)CFArrayGetValueAtIndex(servers, i);
                result.push_back(getStringFromRef(server));
            }
        }
        catch (const std::exception& e) {
            //std::cout << "DNSForService error: " << e.what() << std::endl;
        }

        if (dnsInfo) CFRelease(dnsInfo);
        if (store) CFRelease(store);
        if (dnsKey) CFRelease(dnsKey);
        return result;
    }

};

}

#endif // MACNETUTIL_HPP
