#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyping
import netifaces

# IPアドレスのリストの取得
# 出力例 : [{'addr': '127.0.0.1', 'netmask': '255.0.0.0', 'peer': '127.0.0.1'}]
def getIpAddress():
    ipList=[]
    for iface_name in netifaces.interfaces():
        iface_data = netifaces.ifaddresses(iface_name).get(netifaces.AF_INET))
        iface_data['dev'] = iface_name
        print(iface_data)
        ipList.extend(iface_data)
    return ipList

# IPアドレスのリストをフィルタして，特定のアドレスを取り出す
# 出力例 : '127.0.0.1'
def addressFilter(ipList,filterString):
    for addressInfo in ipList:
        addr=addressInfo['addr']
        if filterString in addr:
            return addr
    return ""

# IPアドレスのリストをフィルタして，特定のデバイスのアドレスを取り出す
# 出力例 : '127.0.0.1'
def deviceFilter(ipList,filterString):
    for addressInfo in ipList:
        dev=addressInfo['dev']
        if filterString in addr:
            return addressInfo['addr']
    return ""


if __name__ == '__main__':
    ip=getIpAddress()
    local_ip=addressFilter(ip,'192.168')
    print local_ip
    local_ip=deviceFilter(ip,'eth')
    print local_ip
    val = pyping.ping('192.168.1.1')
