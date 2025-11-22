#ifndef GNUNETUTIL_HPP
#define GNUNETUTIL_HPP

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
#include <linux/if_packet.h>
#include <net/if_arp.h>

#include <stdint.h>
#include <errno.h>
#include <vector>
#include <map>
#include <iomanip>

#include <stdio.h>
#include <sys/socket.h>
#include <ifaddrs.h>
#include <string.h>


#include <sys/socket.h>
#include <net/route.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <cstdlib>
#include <cstring>
#include <string>

#include <string>
#include <fstream>


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
                
                /*
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
                */
                ifa = ifa->ifa_next;
            }
        }
        freeifaddrs(interfaces);

        return result;
    }


    bool getLinkState(const std::string& ifname, bool& hasCarrier) const
    {
        std::string path = "/sys/class/net/" + ifname + "/carrier";
        std::ifstream f(path);

        if (!f.is_open()) {
            // No carrier file → interface may be virtual (lo, bridges, tunnels)
            return false;  
        }

        int value = -1;
        f >> value;
        if (value == 1) {
            hasCarrier = true;
        } else if (value == 0) {
            hasCarrier = false;
        } else {
            return false; // unexpected value
        }

        return true;
    }


    std::map<std::string, int> getActiveNetworkInterfaces() const {
        std::map<std::string, int> result;
        struct ifaddrs *ifaddr;
        int family, s;
        char host[NI_MAXHOST];

        if (getifaddrs(&ifaddr) == -1) {
            printf("Error: getifaddrs failed - %s\n", strerror(errno));
            return result;
        }



        for (struct ifaddrs *ifa = ifaddr; ifa != nullptr; ifa = ifa->ifa_next) {

            std::cout << "\nInterface: " << ifa->ifa_name << "\n";
            std::cout << "  Flags: 0x" << std::hex << ifa->ifa_flags << std::dec << "\n";

            if (ifa->ifa_addr) {
                int fam = ifa->ifa_addr->sa_family;

                if (fam == AF_INET || fam == AF_INET6) {
                    char addr[INET6_ADDRSTRLEN];
                    void* src = nullptr;

                    if (fam == AF_INET)
                        src = &((struct sockaddr_in*)ifa->ifa_addr)->sin_addr;
                    else
                        src = &((struct sockaddr_in6*)ifa->ifa_addr)->sin6_addr;

                    inet_ntop(fam, src, addr, sizeof(addr));
                    std::cout << "  Address: " << addr << "\n";
                }
                else if (fam == AF_PACKET) {
                    std::cout << "  Hardware / MAC layer entry\n";
                    struct sockaddr_ll *s = (struct sockaddr_ll*)ifa->ifa_addr;
                    std::cout << "  MAC: ";
                    for (int i = 0; i < s->sll_halen; i++) {
                        printf("%02x%s", (unsigned char)s->sll_addr[i],
                            (i+1 != s->sll_halen) ? ":" : "");
                    }
                }

                std::cout << "\n";
                std::string name(ifa->ifa_name);

                // Only process each interface once
                // Skip alternate AF_INET/AF_INET6 entries
                static std::string last;
                if (name == last) continue;
                last = name;

                std::cout << "Interface: " << name << "\n";

                bool carrier;
                if (getLinkState(name, carrier)) {
                    std::cout << "  Link state: "
                            << (carrier ? "UP (carrier detected)" : "DOWN (no carrier)")
                            << "\n";
                } else {
                    std::cout << "  Link state: (not available or virtual interface)\n";
                }

                std::cout << "Type: " << getInterfaceType(name) << std::endl;
                std::cout << "Gateway: " << getDefaultGatewayForInterface(name) << std::endl;
                unsigned int index = if_nametoindex(ifa->ifa_name);
                std::cout << "INDEX: " << index << std::endl;
                //bool dhcpEnabled = (getDhcpServer(name, index) != "");
                //if (dhcpEnabled) std::cout << "----DHCP enabled" << std::endl;
                std::cout << exec("ip a") << std::endl;

            } else {
                std::cout << "  (No address assigned)\n";
            }

        }


        


        /*
        for (struct ifaddrs *ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
            //if (ifa->ifa_addr == NULL)
            //    continue;

            family = ifa->ifa_addr->sa_family;

            if (family == AF_INET ) {
                std::string address = inet_ntoa(((struct sockaddr_in *)ifa->ifa_addr)->sin_addr);
                std::cout << "address: " << address <<std::endl;
                std::cout << "name: " << ifa->ifa_name << std::endl;
                std::cout << "data: " << ifa->ifa_data << std::endl;
                std::cout << "flags: " << ifa->ifa_flags << std::endl;
                //printInterfaceFlags(ifa->ifa_flags);
            } 
            if (ifa->ifa_addr->sa_family == AF_PACKET) {
                struct sockaddr_ll *s = (struct sockaddr_ll*)ifa->ifa_addr;
                std::cout << "  MAC: ";
                for (int i = 0; i < s->sll_halen; i++) {
                    printf("%02x%s", (unsigned char)s->sll_addr[i],
                        (i+1 != s->sll_halen) ? ":" : "");
                }
                std::cout << "\n";
            }
        }
        */



        freeifaddrs(ifaddr);
        return result;
    }

/*
#include <string>
#include <fstream>
#include <iostream>
#include <sys/stat.h>

#include <net/if_arp.h>   // ARPHRD_* constants
*/

    // Utility to check if a path exists
    bool pathExists(const std::string& path) const
    {
        struct stat st;
        return (stat(path.c_str(), &st) == 0);
    }

    // Reads /sys/class/net/<iface>/type
    int readIfType(const std::string& ifname) const
    {
        std::string path = "/sys/class/net/" + ifname + "/type";
        std::ifstream f(path);
        if (!f.is_open())
            return -1;

        int t = -1;
        f >> t;
        return t;
    }

    std::string exec(const char* cmd) const {
        // Buffer to read chunks of output
        std::array<char, 128> buffer;
        std::string result;
        // Open the pipe and ensure it closes automatically using unique_ptr
        std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
        if (!pipe) {
            throw std::runtime_error("popen() failed!");
        }
        // Read data in chunks until the end of the stream
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
            result += buffer.data();
        }
        return result;
    }

    std::string getInterfaceType(const std::string& ifname) const
    {
        std::string base = "/sys/class/net/" + ifname;

        // 1. Read ARPHRD type
        int t = readIfType(ifname);

        // 2. Detect known sysfs class-based types
        if (pathExists(base + "/bridge"))
            return "bridge";

        if (pathExists(base + "/bonding"))
            return "bond";

        if (pathExists(base + "/tun_flags"))
            return "tun/tap";

        if (pathExists(base + "/wireless"))
            return "wireless";  // wext-style

        if (pathExists(base + "/phy80211"))
            return "wireless";  // nl80211-style

        if (pathExists(base + "/vlan"))
            return "vlan";

        if (pathExists(base + "/brport"))
            return "bridge-port";

        if (pathExists(base + "/macvtap") ||
            pathExists(base + "/macvlan"))
            return "macvlan/macvtap";

        if (pathExists(base + "/tun_flags"))
            return "tun/tap";

        // 3. Interpret ARPHRD types
        switch (t) {
            case ARPHRD_LOOPBACK: return "loopback";
            case ARPHRD_ETHER:    return "ethernet";
    #ifdef ARPHRD_IEEE80211
            case ARPHRD_IEEE80211: return "wifi (802.11 raw)";
    #endif
            case ARPHRD_NONE:     return "virtual (no physical device)";
            case ARPHRD_INFINIBAND: return "infiniband";
            case ARPHRD_PPP:      return "ppp";
            case ARPHRD_TUNNEL:   return "ipip tunnel";
            case ARPHRD_SIT:      return "sit tunnel";
            case ARPHRD_IEEE802154: return "802.15.4 (low-power wireless)";
        }

        // 4. Unknown fallback
        return "unknown";
    }

/*
#include <string>
#include <fstream>
#include <sstream>
#include <arpa/inet.h>
*/

    std::string getDefaultGatewayForInterface(const std::string& ifname) const
    {
        std::ifstream routeFile("/proc/net/route");
        if (!routeFile.is_open()) {
            return "";
        }

        std::string line;
        // Skip the header line
        std::getline(routeFile, line);

        while (std::getline(routeFile, line)) {
            std::istringstream iss(line);
            std::string iface, destinationHex, gatewayHex;
            unsigned int flags, refCnt, use, metric, mask, mtu, win, irtt;

            if (!(iss >> iface >> destinationHex >> gatewayHex >>
                flags >> refCnt >> use >> metric >> mask >> mtu >> win >> irtt))
            {
                continue;
            }

            // Only consider rows for our interface
            if (iface != ifname)
                continue;

            // Destination must be default (00000000)
            if (destinationHex != "00000000")
                continue;

            // Must be a gateway and route must be up
            //const unsigned int RTF_UP = 0x0001;
            //const unsigned int RTF_GATEWAY = 0x0002;
            if (!(flags & RTF_UP) || !(flags & RTF_GATEWAY))
                continue;

            // Convert hex to IP (little-endian!)
            unsigned long gateway;
            std::stringstream ss;
            ss << std::hex << gatewayHex;
            ss >> gateway;

            struct in_addr addr;
            addr.s_addr = gateway;  // already little-endian

            return std::string(inet_ntoa(addr));
        }

        return "";  // No default gateway found
    }


    std::string getDhcpServer_systemd(int ifindex) const
    {
        std::string path = "/run/systemd/netif/leases/" + std::to_string(ifindex);
        std::ifstream f(path);
        if (!f.is_open())
            return "";

        std::string line;
        while (std::getline(f, line)) {
            if (line.rfind("SERVER_ADDRESS=", 0) == 0) {
                return line.substr(strlen("SERVER_ADDRESS="));
            }
        }
        return "";
    }

    std::string getDhcpServer_NM(const std::string& iface) const
    {
        std::string path = "/var/lib/NetworkManager/dhclient-" + iface + ".lease";
        std::ifstream f(path);
        if (!f.is_open())
            return "";

        std::string line;
        while (std::getline(f, line)) {
            auto pos = line.find("dhcp-server-identifier");
            if (pos != std::string::npos) {
                auto start = line.find_first_of("0123456789", pos);
                auto end   = line.find(";", start);
                return line.substr(start, end - start);
            }
        }
        return "";
    }


    bool exists(const std::string& p) const {
        struct stat st;
        return stat(p.c_str(), &st) == 0;
    }

    std::string getDhcpServer(const std::string& iface, int ifindex) const
    {
        // 1. systemd-networkd
        if (exists("/run/systemd/netif/leases")) {
            std::string v = getDhcpServer_systemd(ifindex);
            if (!v.empty())
                return v;
        }

        // 2. NetworkManager
        if (exists("/var/lib/NetworkManager")) {
            std::string v = getDhcpServer_NM(iface);
            if (!v.empty())
                return v;
        }

        // 3. ISC dhclient
        std::string dhclientLease =
            "/var/lib/dhcp/dhclient." + iface + ".leases";
        if (exists(dhclientLease)) {
            std::string v = getDhcpServer_NM(iface); // same parser
            if (!v.empty())
                return v;
        }

        // 4. dhcpcd
        std::string dhcpcdLease =
            "/run/dhcpcd/" + iface + ".lease";
        if (exists(dhcpcdLease)) {
            std::string v = getDhcpServer_NM(iface); // same parser
            if (!v.empty())
                return v;
        }

        return ""; // no DHCP detected
    }


};

}

#endif // GNUNETUTIL