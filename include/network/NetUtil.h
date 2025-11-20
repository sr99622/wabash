#ifndef NETUTIL_HPP
#define NETUTIL_HPP

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/stat.h>

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <ifaddrs.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <netdb.h>
#include <net/if.h>
#include <netinet/in.h>
#include <sys/time.h>

#include <stdint.h>
#include <errno.h>
#include <vector>
#include <map>
#include <iomanip>

#include <SystemConfiguration/SystemConfiguration.h>
#include <CoreFoundation/CoreFoundation.h>

#include <stdio.h>
#include <sys/socket.h>
#include <ifaddrs.h>
#include <net/if_dl.h>
#include <string.h>


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

            getAllDHCPservers();
        }
        catch (const std::exception& e) {
            std::cout << "ERROR: " << e.what() << std::endl;
        }

        if (set) CFRelease(set);
        if (prefs) CFRelease(prefs);
        if (order) CFRelease(order);
    }

    void print_dhcp_server_for_service(CFStringRef serviceID) const
    {

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
    
        try {
            // Build key: State:/Network/Service/<service-id>/DHCP
            CFStringRef dhcpKey = CFStringCreateWithFormat(
                NULL, NULL,
                CFSTR("State:/Network/Service/%@/DHCP"),
                serviceID
            );

            SCDynamicStoreRef store = SCDynamicStoreCreate(NULL, CFSTR("dhcp-reader"), NULL, NULL);
            CFDictionaryRef dhcpInfo = (CFDictionaryRef)SCDynamicStoreCopyValue(store, dhcpKey);

            std::cout << "show dhcp info" << std::endl;
            CFShow(dhcpInfo);
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


            if (dhcpInfo) {
                CFRelease(dhcpInfo);
            }

            CFRelease(store);
            CFRelease(dhcpKey);
        }
        catch (const std::exception& e) {
            std::cout << "ERROR: " << e.what() << std::endl;
        }
    }

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

};

}

#endif // NETUTIL_HPP



                /*
                else if ((fam == AF_INET || fam == AF_INET6) && temp_addr->ifa_data) {
                    struct ifa_data* ad = (struct ifa_data*)temp_addr->ifa_data;
                    std::cout << "  [ifa_data] packets=" << ad->ifa_packets
                            << " bytes="   << ad->ifa_bytes << "\n";
                }
                */

