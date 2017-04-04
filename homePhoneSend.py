#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# モジュールをインポートする
import pyaudio
import RPi.GPIO as GPIO
import os
import sys
import threading
import socket
import netifaces
from datetime import datetime
import time

# マルチキャスト関係のIP設定
INTERFACE='eth'
MULTICAST_GROUP = '239.255.0.1' # マルチキャストアドレス
PORT = 4000

# ボタンチェックするか否か
BUTTON_CHECK=True
#BUTTON_CHECK=False

# ピン番号の定義
BUTTON=21
LED=20

# daemon化するか否か
DAEMON=False
#DAEMON=True
PID_FILE='/var/run/homePhone.pid'

# 音声処理のパラメータ
RATE=44100
CHUNK=128

# タイムアウト
TIMEOUT=20

#グローバル変数
pinState = 0 # ボタンが押されているか否かを示す変数

def buttonCallBack(self):
    global pinState
    if (1==GPIO.input(BUTTON)):
        pinState=1
    else:
        pinState=2

# GPIOのピンの設定
def setup(button,led):
    # GPIOの初期化
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(button, GPIO.BOTH)
    GPIO.add_event_callback(button, buttonCallBack)
    GPIO.setup(led, GPIO.OUT)

# なにかのエラーで終了する場合は，PIDファイルを消去，GPIOの設定をリセット, オーディオをクローズ
def finish(sock,audio,stream,pidFile):
    sock.close()
    # ストリームをクローズ
    stream.stop_stream()
    stream.close()
    # オーディオデバイスをクローズ
    audio.terminate()
    # GPIO設定をリセット
    GPIO.cleanup()
    # ファイルを消す
    if os.path.exists(pidFile):
        os.remove(pidFile)
    sys.exit()

# daemon化する処理
def fork(button,led,initTime,timeout,pidFile,check,iface,sock,destAddr,port,stream,chunk):
    pid = os.fork()
    if pid > 0:
        f = open(pidFile,'w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()
    if pid == 0:
        loop(button,led,initTime,timeout,check,iface,sock,destAddr,port,stream,chunk)

# LEDの状態設定
def setLED(pin,flag):
    if (flag!=0) and (flag!=1):
        return
    if flag==1:
        time.sleep(1)
    GPIO.output(pin,flag)

# IPアドレスのリストの取得
# 出力例 : [{'addr': '127.0.0.1', 'netmask': '255.0.0.0', 'peer': '127.0.0.1'}]
def getIpAddress():
    ipList=[]
    for iface_name in netifaces.interfaces():
        iface_data = netifaces.ifaddresses(iface_name).get(netifaces.AF_INET)
        if iface_data!=None:
            iface_data[0]['dev'] = iface_name
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
        if filterString in dev:
            return addressInfo['addr']
    return ""


# ループの1ラウンド
def oneRound(instream,chunk,sock,destAddr,port):
    #global pinState
    if (instream.is_active()):
        input = instream.read(CHUNK,False)
        play=threading.Thread(target=dataOut, name="play", args=(sock,destAddr,port,input,))
        play.start()
        #if pinState!=0:
        #    play=threading.Thread(target=dataOut, name="play", args=(sock,destAddr,port,input,))
        #    play.start()

# メインのループ
def loop(button,led,initTime,timeout,check,iface,sock,destAddr,port,stream,chunk):
    global pinState
    setup(button,led)
    lastTime=initTime
    #print "last time = " , lastTime
    while True:
        if check:
            if pinState==1:
                ip=getIpAddress()
                localAddr=deviceFilter(ip,iface)
                pinState=3
                #localAddr='10.25.170.220' # 送信側のPCのIPアドレス
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(localAddr))
                ledth = threading.Thread(target=setLED, name="setLED", args=(led,1,))
                ledth.start()
                #print "send start"
                oneRound(stream,chunk,sock,destAddr,port)
            if pinState==2:
                pinState=0
                setLED(led,0)
                lastTime=int(datetime.now().strftime('%s'))
                #print "send finish"
            if pinState==3:
                oneRound(stream,chunk,sock,destAddr,port)
            else:
                currentTime=int(datetime.now().strftime('%s'))
                #print "current time = " , currentTime
                #print "last time = " , lastTime
                if timeout < (currentTime-lastTime):
                    return
                time.sleep(0.3)
                #oneRound(stream,chunk,sock,destAddr,port)
        else:
            oneRound(stream,chunk,sock,destAddr,port)

# パッファ分の音声を出力
def dataOut(sock,destAddr,port,data):
    sock.sendto(data, (destAddr, port))

# メイン
if __name__ == '__main__':
    #setup(BUTTON,LED)
    sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    audio=pyaudio.PyAudio()
    initTime=int(datetime.now().strftime('%s'))
    # 音声入力デバイスのオープン
    stream= audio.open(   format = pyaudio.paInt16,
            channels = 2,
            rate = RATE,
            frames_per_buffer = CHUNK,
            input = True) 
    if DAEMON:
        fork(BUTTON,LED,initTime,TIMEOUT,PID_FILE,BUTTON_CHECK,INTERFACE,sock,MULTICAST_GROUP,PORT,stream,CHUNK)
    else:
        try:
            loop(BUTTON,LED,initTime,TIMEOUT,BUTTON_CHECK,INTERFACE,sock,MULTICAST_GROUP,PORT,stream,CHUNK)
        except:
            finish(sock,audio,stream,PID_FILE)


