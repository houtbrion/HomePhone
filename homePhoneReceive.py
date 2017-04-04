#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import socket
from contextlib import closing
import pyaudio
import netifaces
import os
import sys
import RPi.GPIO as GPIO

# 音声処理のパラメータ
RATE=44100
CHUNK=128
#BUFF_SIZE = 384
BUFF_SIZE = 512
#BUFF_SIZE = 4096
#BUFF_SIZE = 768

# 自分のパケットを再生するか否かのフラグ
PLAY_LOCAL=True
#PLAY_LOCAL=False

# インターフェースの指定
INTERFACE='eth'

# 受信するアドレスの指定
MULTICAST = '239.255.0.1' # マルチキャストアドレス
PORT = 4000

# daemon化するか否か
DAEMON=False
#DAEMON=True
PID_FILE='/var/run/multicastReceiveSound.pid'

# タイムアウトの時間
TIMEOUT=20

# LEDピン
LED = 16 # GPIOの16番　ピン番号の36番

def getIpAddress():
    ipList=[]
    for iface_name in netifaces.interfaces():
        iface_data = netifaces.ifaddresses(iface_name).get(netifaces.AF_INET)
        if iface_data!=None:
            iface_data[0]['dev'] = iface_name
            ipList.extend(iface_data)
    return ipList

def deviceFilter(ipList,filterString):
    for addressInfo in ipList:
        dev=addressInfo['dev']
        if filterString in dev:
            return addressInfo['addr']
    return ""

def setLED(pin,flag):
    if (flag!=0) and (flag!=1):
        return
    GPIO.output(pin,flag)

# daemon化する処理
def fork(led,timeout, pidFile, iface,multicast,port,bsize,flag,stream,audio):
    pid = os.fork()
    if pid > 0:
        f = open(pidFile,'w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()
    if pid == 0:
        main(led,timeout,pidFile,iface,multicast,port,bsize,flag,stream,audio)

def main(led,timeout, pidFile,iface,multicast_group,port,bufsize,flag,stream,audio):
    ip=getIpAddress()
    local_address = deviceFilter(ip,iface)
    if local_address=='':
        return
    # GPIOの初期化
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led, GPIO.OUT)

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.bind(('', port))
        sock.setsockopt(socket.IPPROTO_IP,
                        socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(multicast_group)
                             + socket.inet_aton(local_address))
        setLED(led,1)

        while True:
            try:
                data, addr = sock.recvfrom(bufsize)
                if flag or (local_address!=addr[0]):
                    stream.write(data)
            except socket.timeout:
                finish(led,sock,audio,stream,pidFile)
                return
    return

def finish(led,sock,audio,stream,pidFile):
    sock.close()
    # ストリームをクローズ
    stream.stop_stream()
    stream.close()
    # オーディオデバイスをクローズ
    audio.terminate()
    # LEDを消す
    setLED(led,0)
    # GPIO設定をリセット
    GPIO.cleanup()
    # ファイルを消す
    if os.path.exists(pidFile):
        os.remove(pidFile)
    sys.exit()

if __name__ == '__main__':
    audio=pyaudio.PyAudio()
    stream= audio.open(   format = pyaudio.paInt16,
        channels = 2,
        rate = RATE,
        frames_per_buffer = CHUNK,
        output = True)
    if DAEMON:
        fork(LED,TIMEOUT, PID_FILE, INTERFACE,MULTICAST,PORT,BUFF_SIZE,PLAY_LOCAL,stream,audio)
    else:
        main(LED,TIMEOUT, PID_FILE, INTERFACE,MULTICAST,PORT,BUFF_SIZE,PLAY_LOCAL,stream,audio)
