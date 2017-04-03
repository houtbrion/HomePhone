#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import socket
from contextlib import closing
import pyaudio

# 音声処理のパラメータ
RATE=44100
CHUNK=128

def main(stream):
    #local_address   = '192.168.1.8' # 受信側のPCのIPアドレス
    local_address   = '10.25.170.220' # 受信側のPCのIPアドレス
    multicast_group = '239.255.0.1' # マルチキャストアドレス
    port = 4000
    bufsize = 4096

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.setsockopt(socket.IPPROTO_IP,
                        socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(multicast_group)
                             + socket.inet_aton(local_address))

        while True:
            #print(sock.recv(bufsize))
            stream.write(sock.recv(bufsize))
    return

if __name__ == '__main__':
    audio=pyaudio.PyAudio()
    stream= audio.open(   format = pyaudio.paInt16,
        channels = 2,
        rate = RATE,
        frames_per_buffer = CHUNK,
        output = True)
    main(stream)
