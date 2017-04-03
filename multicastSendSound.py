#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import socket
#import time
from contextlib import closing
import pyaudio

# 音声処理のパラメータ
RATE=44100
CHUNK=128

def main(stream,chunk):
    #local_address   = '192.168.1.8' # 送信側のPCのIPアドレス
    local_address   = '10.25.170.220' # 送信側のPCのIPアドレス
    multicast_group = '239.255.0.1' # マルチキャストアドレス
    port = 4000

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:

        # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_address))

        count = 0
        while True:
            #message = 'Hello world : {0}'.format(count).encode('utf-8')
            #print(message)
            message=stream.read(chunk,False)
            sock.sendto(message, (multicast_group, port))
            #count += 1
            #time.sleep(0.5)
    return

if __name__ == '__main__':
    audio=pyaudio.PyAudio()
    stream= audio.open(   format = pyaudio.paInt16,
        channels = 2,
        rate = RATE,
        frames_per_buffer = CHUNK,
        input = True)
    main(stream,CHUNK)
