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

#include <SystemConfiguration/SystemConfiguration.h>
#include <CoreFoundation/CoreFoundation.h>


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
        struct ifaddrs *temp_addr = NULL;
        int success = 0;
        success = getifaddrs(&interfaces);
        if (success == 0) {
            temp_addr = interfaces;
            while (temp_addr != NULL) {

                sa_family_t fam = temp_addr->ifa_addr->sa_family;
                
                address = inet_ntoa(((struct sockaddr_in *)temp_addr->ifa_addr)->sin_addr);
                if (strcmp(address, "127.0.0.1") != 0)
                    strcpy(buf, address);
                std::cout << "address: " << address <<std::endl;
                std::cout << "name: " << temp_addr->ifa_name << std::endl;
                std::cout << "data: " << temp_addr->ifa_data << std::endl;
                std::cout << "flags: " << temp_addr->ifa_flags << std::endl;
                printInterfaceFlags(temp_addr->ifa_flags);

                if (fam == AF_LINK && temp_addr->ifa_data) {
                    struct if_data* d = (struct if_data*)temp_addr->ifa_data;
                    std::cout << "  [if_data] MTU=" << d->ifi_mtu
                            << " RX=" << d->ifi_ipackets
                            << " TX=" << d->ifi_opackets << "\n";
                }
                /*
                else if ((fam == AF_INET || fam == AF_INET6) && temp_addr->ifa_data) {
                    struct ifa_data* ad = (struct ifa_data*)temp_addr->ifa_data;
                    std::cout << "  [ifa_data] packets=" << ad->ifa_packets
                            << " bytes="   << ad->ifa_bytes << "\n";
                }
                */


                temp_addr = temp_addr->ifa_next;
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
        int count = 0;

        if (getifaddrs(&ifaddr) == -1) {
            printf("Error: getifaddrs failed - %s\n", strerror(errno));
            return;
        }

        for (struct ifaddrs *ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
            if (ifa->ifa_addr == NULL)
                continue;

            family = ifa->ifa_addr->sa_family;

            if (family == AF_INET ) {
                s = getnameinfo(ifa->ifa_addr, 
                        sizeof(struct sockaddr_in),
                        host, NI_MAXHOST,
                        NULL, 0, NI_NUMERICHOST);

                if (s != 0) {
                    printf("getnameinfo() failed: %s\n", gai_strerror(s));
                    continue;
                }

                //if (strcmp(host, "127.0.0.1")) {
                    std::cout << "HOST: " << host << std::endl;
                    //strcpy(onvif_session->active_network_interfaces[count], host);
                    //strcat(onvif_session->active_network_interfaces[count], " - ");
                    //strcat(onvif_session->active_network_interfaces[count], ifa->ifa_name);
                    count += 1;
                //}
            } 
        }
        freeifaddrs(ifaddr);

        printInterfacePriority();

        return result;
    }

    void printInterfacePriority() const
    {
        // Load system network preferences
        SCPreferencesRef prefs = SCPreferencesCreate(NULL, CFSTR("ifprio"), NULL);
        if (!prefs) return;

        // Get current network set
        SCNetworkSetRef set = SCNetworkSetCopyCurrent(prefs);
        if (!set) {
            CFRelease(prefs);
            return;
        }

        // Get service order (priority list)
        CFArrayRef order = SCNetworkSetGetServiceOrder(set);
        if (!order) {
            CFRelease(set);
            CFRelease(prefs);
            return;
        }

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

            //char buf[256];
            if (bsdName && CFStringGetCString(bsdName, buf, sizeof(buf), kCFStringEncodingUTF8)) {
                std::cout << "Priority " << i << " → interface " << buf << "\n";
            }

            // buf == temp_addr->ifa_name

        }

        CFRelease(set);
        CFRelease(prefs);
    }


};

}

#endif // NETUTIL_HPP