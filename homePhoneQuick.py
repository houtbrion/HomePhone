#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# モジュールをインポートする
import pyaudio
import RPi.GPIO as GPIO
import os
import sys
import threading
import socket

# マルチキャスト関係のIP設定
LOCAL_ADDRESS='10.25.170.220' # 送信側のPCのIPアドレス
MULTICAST_GROUP = '239.255.0.1' # マルチキャストアドレス
PORT = 4000

# ボタンチェックするか否か
BUTTON_CHECK=True
#BUTTON_CHECK=False

# ピン番号の定義
BUTTON=21
LED=20

# ボタンのタイプ
BUTTON_TYPE=0 # プルダウン式
#BUTTON_TYPE=1 # プルアップ式

# チェックする間隔
INTERVAL=1

# daemon化するか否か
DAEMON=False
PID_FILE='/var/run/homePhone.pid'

# 音声処理のパラメータ
#RATE=88200
RATE=44100
#CHUNK=1024
CHUNK=128

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
    GPIO.setup(led, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pin, GPIO.BOTH)
    GPIO.add_event_callback(pin, buttonCallBack)

# なにかのエラーで終了する場合は，PIDファイルを消去，GPIOの設定をリセット, オーディオをクローズ
def finish(sock,audio,pidFile):
    sock.close()
    # ストリームをクローズ
    instream.stop_stream()
    instream.close()
    # オーディオデバイスをクローズ
    audio.terminate()
    # GPIO設定をリセット
    GPIO.cleanup()
    # ファイルを消す
    if os.path.exists(pidFile):
        os.remove(pidFile)
    sys.exit()

# daemon化する処理
def fork(pidFile,check,sock,localAddr,destAddr,port,audio,chunk,led):
    pid = os.fork()
    if pid > 0:
        f = open(pidFile,'w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()
    if pid == 0:
        loop(check,sock,destAddr,port,audio,chunk,led)

# LEDの状態設定
def setLED(pin,flag):
    if (flag!=0) and (flag!=1):
        return
    #GPIO.output(pin,flag)

# ループの1ラウンド
def oneRound(instream,chunk,sock,destAddr,port):
    if (instream.is_active()):
        input = instream.read(CHUNK,False)
        play=threading.Thread(target=dataOut, name="play", args=(sock,destAddr,port,input,))
        play.start()

# メインのループ
#def loop(check,chunk):
def loop(check,sock,destAddr,port,stream,chunk,led):
    global pinState
    while True:
        if check:
            if pinState==1:
                pinState=3
                localAddr='10.25.170.220' # 送信側のPCのIPアドレス
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(localAddr))
                print "send start"
                setLED(led,1)
                oneRound(stream,chunk,sock,destAddr,port)
            if pinState==2:
                pinState=0
                print "send finish"
                setLED(led,0)
            if pinState==3:
                oneRound(stream,chunk,sock,destAddr,port)
        else:
            oneRound(stream,chunk,sock,destAddr,port)

# パッファ分の音声を出力
def dataOut(sock,destAddr,port,data):
    sock.sendto(data, (destAddr, port))

# メイン
if __name__ == '__main__':
    try:
        audio=pyaudio.PyAudio()
        setup(BUTTON,LED)
        sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 音声入力デバイスのオープン
        stream= audio.open(   format = pyaudio.paInt16,
            channels = 2,
            rate = RATE,
            frames_per_buffer = CHUNK,
            input = True) 
    except:
        finish(sock,stream,PID_FILE)
    if DAEMON:
        try:
            fork(PID_FILE,BUTTON_CHECK,sock,MULTICAST_GROUP,PORT,stream,CHUNK,LED)
        except:
            finish(sock,audio,stream,PID_FILE)
    else:
        try:
            loop(BUTTON_CHECK,sock,MULTICAST_GROUP,PORT,stream,CHUNK,LED)
        except:
            finish(sock,audio,stream,PID_FILE)


