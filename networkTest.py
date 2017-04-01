#!/usr/bin/python
# -*- coding: utf-8 -*-



import netifaces

# IPアドレスのリストの取得
# 出力例 : [{'addr': '127.0.0.1', 'netmask': '255.0.0.0', 'peer': '127.0.0.1'}]
def getIpAddress():
    ipList=[]
    for iface_name in netifaces.interfaces():
        iface_data = netifaces.ifaddresses(iface_name)
        print(iface_data.get(netifaces.AF_INET))
        ipList.extend(iface_data.get(netifaces.AF_INET))
    return ipList


# IPアドレスのリストをフィルタして，特定のアドレスを取り出す
# 出力例 : '127.0.0.1'
def addressFilter(ipList,filterString):
    for addressInfo in ipList:
        addr=addressInfo['addr']
        if filterString in addr:
            return addr
    return ""


if __name__ == '__main__':
    ip=getIpAddress()
    local_ip=addressFilter(ip,'192.168')
    print local_ip
