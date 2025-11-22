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

        char *address;
        struct ifaddrs *interfaces = NULL;
        struct ifaddrs *ifa = NULL;
        int success = 0;
        success = getifaddrs(&interfaces);
        if (success == 0) {
            ifa = interfaces;
            while (ifa != NULL) {

                sa_family_t fam = ifa->ifa_addr->sa_family;
                
                if (fam == AF_LINK && ifa->ifa_data) {
                    struct if_data* d = (struct if_data*)ifa->ifa_data;
                    std::cout << "  [if_data] MTU=" << d->ifi_mtu
                            << " RX=" << d->ifi_ipackets
                            << " TX=" << d->ifi_opackets << "\n";

                    struct sockaddr_dl *sdl = (struct sockaddr_dl *)ifa->ifa_addr;
                    unsigned char* ptr = (unsigned char *)LLADDR(sdl);
                    
                    printf("Interface: %s, MAC Address: %02x:%02x:%02x:%02x:%02x:%02x\n",
                        ifa->ifa_name, *ptr, *(ptr+1), *(ptr+2), *(ptr+3), *(ptr+4), *(ptr+5));             
                }
                ifa = ifa->ifa_next;
            }
        }
        freeifaddrs(interfaces);
        return result;
    }

    std::map<std::string, int> getActiveNetworkInterfaces() const {
        std::map<std::string, int> result;

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
        printInterfacePriority();
        return result;
    }

    void printInterfacePriority() const
    {
        SCPreferencesRef prefs = nullptr;
        SCNetworkSetRef set = nullptr;
        CFArrayRef order = nullptr;

        try {
            prefs = SCPreferencesCreate(NULL, CFSTR("ifprio"), NULL);
            if (!prefs) throw std::runtime_error("NULL");

            set = SCNetworkSetCopyCurrent(prefs);
            if (!set) throw std::runtime_error("NULL");

            order = SCNetworkSetGetServiceOrder(set);
            if (!order) throw std::runtime_error("NULL");

            std::cout << "Service Order (priority):\n";
            for (CFIndex i = 0; i < CFArrayGetCount(order); i++) {
                CFStringRef sid = (CFStringRef)CFArrayGetValueAtIndex(order, i);
                SCNetworkServiceRef service = SCNetworkServiceCopy(prefs, sid);

                char buf[256];
                if (CFStringGetCString(sid, buf, sizeof(buf), kCFStringEncodingUTF8)) {
                    std::cout << "  " << i << ": " << buf << "\n";
                }

                SCNetworkInterfaceRef iface = SCNetworkServiceGetInterface(service);
                CFStringRef bsdName = SCNetworkInterfaceGetBSDName(iface);
                std::cout << "NAME: " << bsdName << std::endl;

                if (bsdName && CFStringGetCString(bsdName, buf, sizeof(buf), kCFStringEncodingUTF8)) {
                    std::cout << "Priority " << i << " → interface " << buf << "\n";
                }
            }

            //getAllDHCPservers();
        }
        catch (const std::exception& e) {
            std::cout << "ERROR: " << e.what() << std::endl;
        }

        if (set) CFRelease(set);
        if (prefs) CFRelease(prefs);
        if (order) CFRelease(order);

        dothings();
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
                CFStringRef serviceName = SCNetworkServiceGetName(service);
                CFStringRef serviceID = SCNetworkServiceGetServiceID(service);
                SCNetworkInterfaceRef iface = SCNetworkServiceGetInterface(service);
                if (!iface) continue;
                CFStringRef bsdName = SCNetworkInterfaceGetBSDName(iface);
                if (!bsdName) continue;
                char nameBuf[64] = { 0 };
                CFStringGetCString(bsdName, nameBuf, sizeof(nameBuf), kCFStringEncodingUTF8);
                if (if_name == nameBuf) {
                    char idBuf[256];
                    CFStringGetCString(serviceID, idBuf, sizeof(idBuf), kCFStringEncodingUTF8);
                    result = idBuf;
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

    bool dhcpEnabled(const std::string& serviceID) const
    {
        /*
        std::unordered_map<std::string, std::string> dhcpOptionFriendlyNames = {
            {"Option_1",  "SubnetMask"},
            {"Option_3",  "Router"},
            {"Option_6",  "DNSServer"},
            {"Option_15", "DomainName"},
            {"Option_28", "BroadcastAddress"},
            {"Option_51", "LeaseTime"},
            {"Option_53", "MessageType"},
            {"Option_54", "ServerIdentifier"},  // <- your DHCP server
            {"Option_58", "RenewalTime"},
            {"Option_59", "RebindTime"},
            {"Option_61", "ClientIdentifier"}
        };
        */

        SCDynamicStoreRef store = nullptr;
        CFDictionaryRef dhcpInfo = nullptr;
        CFStringRef dhcpKey = nullptr;
        bool result = false;

        try {
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

            std::cout << "show dhcp info" << std::endl;
            CFShow(dhcpInfo);
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
            std::cout << "ERROR: " << e.what() << std::endl;
        }

        if (dhcpInfo) CFRelease(dhcpInfo);
        if (store) CFRelease(store);
        if (dhcpKey) CFRelease(dhcpKey);
        return result;
    }

    /*
    void getAllDHCPservers() const
    {
        SCDynamicStoreRef store = SCDynamicStoreCreate(NULL, CFSTR("dhcp-reader"), NULL, NULL);
        CFArrayRef serviceIDs = SCDynamicStoreCopyKeyList(store, CFSTR("State:/Network/Service/.+"));

        if (!serviceIDs) {
            std::cout << "did not find service ids" << std::endl;
            return;
        }

        CFIndex count = CFArrayGetCount(serviceIDs);
        std::cout << "service id count: " << count << std::endl;

        for (CFIndex i = 0; i < count; i++) {
            CFStringRef key = (CFStringRef)CFArrayGetValueAtIndex(serviceIDs, i);
            
            if (!CFStringHasSuffix(key, CFSTR("/IPv4"))) {
                std::cout << "NOT IPV4" << std::endl;
                continue;
            }

            // Extract the service ID from the path
            // Key looks like: State:/Network/Service/<id>/IPv4
            CFArrayRef parts = CFStringCreateArrayBySeparatingStrings(
                NULL, key, CFSTR("/")
            );

            if (CFArrayGetCount(parts) >= 4) {
                CFStringRef serviceID = (CFStringRef)CFArrayGetValueAtIndex(parts, 3);
                std::cout << "wtf 1: " << serviceID << std::endl;
                print_dhcp_server_for_service(serviceID);
                std::cout << "wtf 2" << std::endl;
            }

            CFRelease(parts);
        }

        CFRelease(serviceIDs);
        CFRelease(store);
    }
    */

    void dothings() const
    {
        std::cout << "DO THINGS" << std::endl;
        CFArrayRef ifs = SCNetworkInterfaceCopyAll();
        CFIndex count = CFArrayGetCount(ifs);
        CFShow(ifs);

        for (CFIndex i = 0; i < count; i++) {
            SCNetworkInterfaceRef item = (SCNetworkInterfaceRef)CFArrayGetValueAtIndex(ifs, i);
            CFStringRef bsd = SCNetworkInterfaceGetBSDName(item);
            CFShow(bsd);
            char buf[64];
            CFStringGetCString(bsd, buf, sizeof(buf), kCFStringEncodingUTF8);
            std::cout << "BSD NAME: " << buf << std::endl;
            std::string serviceID = getServiceIDForInterface(buf);
            if (!serviceID.empty()) {
                std::cout << "_____FOUND SERVICE ID______" << serviceID << std::endl;
                //printDNSForService(serviceID);
                std::cout << dnsForService(serviceID) << std::endl;
                //print_dhcp_server_for_service(serviceID);
                if (dhcpEnabled(serviceID)) 
                    std::cout << "DHCP ENABLED" << std::endl;
                else
                    std::cout << "DHCP NOT ENABLED" << std::endl;
            }
            else {
                std::cout << "NO SERVICE ID FOUND" << std::endl;
            } 
            //bool is_up = isInterfaceUp(buf);
            bool is_up = interfaceHasLink(buf);
            std::cout << "IS INTERFACE UP: " << is_up << std::endl;
            CFStringRef displayName = SCNetworkInterfaceGetLocalizedDisplayName(item);
            CFStringGetCString(displayName, buf, sizeof(buf), kCFStringEncodingUTF8);
            std::cout << "DISPLAY NAME: " << buf << std::endl;
            CFStringRef hardware = SCNetworkInterfaceGetHardwareAddressString(item);
            CFStringGetCString(hardware, buf, sizeof(buf), kCFStringEncodingUTF8);
            std::cout << "HARDWARE: " << buf << std::endl;
            CFStringRef if_type = SCNetworkInterfaceGetInterfaceType(item);
            CFShow(if_type);
            CFArrayRef protocols = SCNetworkInterfaceGetSupportedProtocolTypes(item);
            CFShow(protocols);
            //CFDictionaryRef configuration = SCNetworkInterfaceGetConfiguration(item);
            //CFShow(configuration);
            std::string defaultGateway = getDefaultGateway();
            std::cout << "default gateway: " << defaultGateway << std::endl;
        }
        std::cout << "THINGS DONE: " << count << std::endl;
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
            //{IFF_DRV_OACTIVE, "DRV_OACTIVE"},
            {IFF_SIMPLEX, "SIMPLEX"},
            {IFF_LINK0, "LINK0"},
            {IFF_LINK1, "LINK1"},
            {IFF_LINK2, "LINK2"},
            {IFF_MULTICAST, "MULTICAST"},
            //{IFF_LQM_ENABLED, "LQM_ENABLED"},
            //{IFF_LQM_DEGRADED, "LQM_DEGRADED"},
            //{IFF_LQM_NA, "LQM_NA"},
            //{IFF_CANTCONFIG, "CANTCONFIG"},
            //{IFF_PPROMISC, "PPROMISC"},
            //{IFF_MONITOR, "MONITOR"},
            //{IFF_STANDBY, "STANDBY"},
            //{IFF_EEE, "EEE"},
            //{IFF_DRV_RUNNING, "DRV_RUNNING"},
            //{IFF_WAKE_ON_MAGIC_PACKET, "WAKE_ON_MAGIC_PACKET"},
            //{IFF_INTERFACEID, "INTERFACEID"},
            //{IFF_ROUTER, "ROUTER"},
            //{IFF_DETACHING, "DETACHING"},
            //{IFF_TENTATIVE, "TENTATIVE"},
            //{IFF_DUPLICATED, "DUPLICATED"},
        };

        for (auto& f : list) {
            if (flags & f.flag)
                std::cout << f.name << " ";
        }
    }

    std::string dnsForService(const std::string& serviceID) const {
        SCDynamicStoreRef store = nullptr;
        CFDictionaryRef dnsInfo = nullptr;
        CFStringRef dnsKey = nullptr;
        CFArrayRef servers = nullptr;
        std::string result;
        
        try {
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
                char buf[256];
                if (CFStringGetCString(server, buf, sizeof(buf), kCFStringEncodingUTF8)) {
                    printf("DNS Server: %s\n", buf);
                    result = buf;
                }
            }
        }
        catch (const std::exception& e) {
            std::cout << "DNSForService error: " << e.what() << std::endl;
        }

        if (dnsInfo) CFRelease(dnsInfo);
        if (store) CFRelease(store);
        if (dnsKey) CFRelease(dnsKey);
        return result;
    }

};

}

#endif // MACNETUTIL_HPP



                /*
                else if ((fam == AF_INET || fam == AF_INET6) && temp_addr->ifa_data) {
                    struct ifa_data* ad = (struct ifa_data*)temp_addr->ifa_data;
                    std::cout << "  [ifa_data] packets=" << ad->ifa_packets
                            << " bytes="   << ad->ifa_bytes << "\n";
                }
                */

