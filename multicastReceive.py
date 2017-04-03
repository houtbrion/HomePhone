#!/usr/bin/python
# -*- coding: utf-8 -*-

#from __future__ import print_function
from contextlib import closing

import socket
import netifaces

LOCAL   = '192.168.1.8' # 受信側のPCのIPアドレス
#LOCAL   = '10.25.170.220' # 受信側のPCのIPアドレス
MULTICAST = '239.255.0.1' # マルチキャストアドレス
PORT = 4000
BUFF_SIZE = 4096

def getIpAddress():
    ipList=[]
    for iface_name in netifaces.interfaces():
        iface_data = netifaces.ifaddresses(iface_name).get(netifaces.AF_INET)
        iface_data[0]['dev'] = iface_name
        #print(iface_data)
        ipList.extend(iface_data)
    return ipList

def addressFilter(ipList,filterString):
    for addressInfo in ipList:
        addr=addressInfo['addr']
        if filterString in addr:
            return addr
    return ""

def deviceFilter(ipList,filterString):
    for addressInfo in ipList:
        dev=addressInfo['dev']
        if filterString in dev:
            return addressInfo['addr']
    return ""

def main(bufsize,local_address,multicast_group,port):
    #local_address   = '192.168.1.8' # 受信側のPCのIPアドレス
    ##local_address   = '10.25.170.220' # 受信側のPCのIPアドレス
    #multicast_group = '239.255.0.1' # マルチキャストアドレス
    #port = 4000
    #bufsize = 4096

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(multicast_group) + socket.inet_aton(local_address))

        while True:
            #print(sock.recv(bufsize))
            data, addr = sock.recvfrom(bufsize)
            print " data = " , data
            if local_address==addr[0]:
                print "packet from local"
            #print " addr = " , addr[0]
    return

if __name__ == '__main__':
    ip=getIpAddress()
    local_ip=addressFilter(ip,'192.168')
    print local_ip
    local_ip=deviceFilter(ip,'eth')
    print local_ip
    #main(BUFF_SIZE,LOCAL,MULTICAST,PORT)
    main(BUFF_SIZE,local_ip,MULTICAST,PORT)
