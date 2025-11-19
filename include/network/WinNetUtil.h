#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/stat.h>

#include <ws2tcpip.h>
#include <winsock2.h>
#include <wincrypt.h>
#include <iphlpapi.h>
#include <fcntl.h>
#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "ws2_32.lib")

#include <stdint.h>
#include <errno.h>
#include <vector>
#include <map>

namespace wabash
{

class NetUtil
{
public:
    WSAData wsaData = { 0 };

    NetUtil() {
        int result = NO_ERROR;
        if (result = WSAStartup(MAKEWORD(2, 2), &wsaData) != NO_ERROR) 
            error("server wsa startup exception", result);
    }

    ~NetUtil() {
        if (wsaData.wVersion) WSACleanup();
    }


    std::vector<std::string> getIPAddress() const {
        char buf[128] = { 0 };
        std::string result;
        std::vector<std::string> results;

        DWORD dwSize = 0;
        
        PMIB_IPADDRTABLE pIPAddrTable = (MIB_IPADDRTABLE *) malloc(sizeof(MIB_IPADDRTABLE));
        if (pIPAddrTable) {
            if (GetIpAddrTable(pIPAddrTable, &dwSize, 0) == ERROR_INSUFFICIENT_BUFFER) {
                free(pIPAddrTable);
                pIPAddrTable = (MIB_IPADDRTABLE *) malloc(dwSize);
            }
            if (pIPAddrTable == NULL) {
                return results;
            }
        }

        DWORD dwRetVal = 0;
        if ((dwRetVal = GetIpAddrTable(pIPAddrTable, &dwSize, 0)) != NO_ERROR) {
            return results;
        }

        IN_ADDR IPAddr;
        int p = 0;
        while (p < (int)pIPAddrTable->dwNumEntries) {
            IPAddr.S_un.S_addr = (u_long)pIPAddrTable->table[p].dwAddr;
            strcpy(buf, inet_ntoa(IPAddr));
            results.push_back(std::string(buf));
            p++;
        }

        if (pIPAddrTable) {
            free(pIPAddrTable);
            pIPAddrTable = nullptr;
        }

        return results;
    }

    DWORD GetNetworkPriority(DWORD interfaceIndex) const {
        DWORD result = -1;
        MIB_IPINTERFACE_ROW row;
        InitializeIpInterfaceEntry(&row);
        row.Family = AF_INET;
        row.InterfaceIndex = interfaceIndex;

        DWORD dwRetVal = GetIpInterfaceEntry(&row);
        if (dwRetVal == NO_ERROR) {
            //printf("Interface Index: %d\n", row.InterfaceIndex);
            //printf("Metric: %d\n", row.Metric);
            result = row.Metric;
        } else {
            printf("GetIpInterfaceEntry failed with error: %d\n", dwRetVal);
        }
        return result;
    }

    std::map<std::string, int> getActiveNetworkInterfaces() const {
        PIP_ADAPTER_INFO pAdapterInfo;
        PIP_ADAPTER_INFO pAdapter = NULL;
        DWORD dwRetVal = 0;
        int count = 0;
        std::map<std::string, int> result;

        ULONG ulOutBufLen = sizeof (IP_ADAPTER_INFO);
        pAdapterInfo = (IP_ADAPTER_INFO *) malloc(sizeof (IP_ADAPTER_INFO));
        if (pAdapterInfo == NULL) {
            printf("Error allocating memory needed to call GetAdaptersinfo\n");
            return result;
        }

        if (GetAdaptersInfo(pAdapterInfo, &ulOutBufLen) == ERROR_BUFFER_OVERFLOW) {
            free(pAdapterInfo);
            pAdapterInfo = (IP_ADAPTER_INFO *) malloc(ulOutBufLen);
            if (pAdapterInfo == NULL) {
                printf("Error allocating memory needed to call GetAdaptersinfo\n");
                return result;
            }
        }

        DWORD highest_priority = 0xFFFFFFFF;
        if ((dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen)) == NO_ERROR) {
            pAdapter = pAdapterInfo;
            while (pAdapter) {
                if (strcmp(pAdapter->IpAddressList.IpAddress.String, "0.0.0.0")) {
                    char interface_info[1024] = {0};
                    //sprintf(interface_info, "%s - %s", pAdapter->IpAddressList.IpAddress.String, pAdapter->Description);
                    sprintf(interface_info, "%s", pAdapter->IpAddressList.IpAddress.String);
                    //printf("Network interface info %s\n", interface_info);
                    //printf("Combo Index: %d\n", pAdapter->ComboIndex);
                    
                    std::cout << pAdapter->Description << std::endl;
                    
                    //GetNetworkPriority(pAdapter->ComboIndex);
                    
                    // this is giving weird error cannot convert 'this' pointer from 'const wabash::NetUtil' to 'wabash::NetUtil &'
                    DWORD priority = GetNetworkPriority(pAdapter->ComboIndex);
                    printf("Priority: %d\n", priority);




                    /*
                    printf("Priority: %d\n", priority);

                    if (priority < highest_priority) {
                        highest_priority = priority;
                        //strncpy(onvif_session->primary_network_interface, interface_info, min(strlen(interface_info), sizeof(onvif_session->primary_network_interface)));
                    }
                    */

                    std::cout << "interface info: " << interface_info << std::endl;
                    //result.push_back(interface_info);
                    result.insert({interface_info, priority});

                    //strncpy(onvif_session->active_network_interfaces[count], interface_info, min(strlen(interface_info), 1024));
                    count += 1;
                }
                pAdapter = pAdapter->Next;
            }
        } 
        else {
            printf("GetAdaptersInfo failed with error: %d", dwRetVal);
        }
        if (pAdapterInfo)
            free(pAdapterInfo);

        //printf("Primary Interface: %s\n", onvif_session->primary_network_interface);
        return result;
    }

    const std::string errorToString(int err) {
        wchar_t *lpwstr = nullptr;
        FormatMessage(
            FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
            nullptr, err, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPWSTR)&lpwstr, 0, nullptr
        );
        int size = WideCharToMultiByte(CP_UTF8, 0, lpwstr, -1, NULL, 0, NULL, NULL);
        std::string output(size, 0);
        WideCharToMultiByte(CP_UTF8, 0, lpwstr, -1, &output[0], size, NULL, NULL);
        LocalFree(lpwstr);
        return output;
    }

    void error(const std::string& msg, int err) {
        std::stringstream str;
        str << msg << " : " << errorToString(err);
        throw std::runtime_error(str.str());
    }

};

    
}