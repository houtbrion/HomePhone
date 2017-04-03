#!/usr/bin/python
# -*- coding: utf-8 -*-
#from __future__ import print_function
import socket
#import time
#from contextlib import closing
import pyaudio

import threading

# 音声処理のパラメータ
RATE=44100
CHUNK=128

#local_address   = '192.168.1.8' # 送信側のPCのIPアドレス
LOCAL_IP   = '10.25.170.220' # 送信側のPCのIPアドレス
MULTICAST_GROUP = '239.255.0.1' # マルチキャストアドレス
PORT = 4000

def main(sock,multicast_group,port,stream,chunk):
    while True:
        message=stream.read(chunk,False)
        sound = threading.Thread(target=play, name="play", args=(message,sock,multicast_group,port,))
        sound.start()

def play(message,sock,multicast_group,port):
    sock.sendto(message, (multicast_group, port))

if __name__ == '__main__':
    audio=pyaudio.PyAudio()
    stream= audio.open(   format = pyaudio.paInt16,
        channels = 2,
        rate = RATE,
        frames_per_buffer = CHUNK,
        input = True)
    sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(LOCAL_IP))
    main(sock,MULTICAST_GROUP,PORT,stream,CHUNK)
