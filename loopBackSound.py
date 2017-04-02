#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# モジュールをインポートする
import pyaudio
import RPi.GPIO as GPIO
#import time
import os
import sys
import threading

# ボタンチェックするか否か
BUTTON_CHECK=True
#BUTTON_CHECK=False

# ボタンが繋がったピン番号の定義
BUTTON=21

# ボタンのタイプ
BUTTON_TYPE=0 # プルダウン式
#BUTTON_TYPE=1 # プルアップ式

# チェックする間隔
INTERVAL=1

# daemon化するか否か
DAEMON=False
PID_FILE='/var/run/homePhone.pid'

# 音声処理のパラメータ
RATE=88200
CHUNK=1024

#グローバル変数
pinState=False # ボタンが押されているか否かを示す変数
#pinState=True # ボタンが押されているか否かを示す変数

def buttonCallBack(self):
    global stream
    while True:
        if (stream.is_active()):
            input = stream.read(CHUNK)
            output = stream.write(input)
        #if ((1==GPIO.input(BUTTON)) and (stream.is_active())):
        #    input = stream.read(CHUNK)
        #    output = stream.write(input)
        #else:
        #    break

# GPIOのピンの設定
def setup(pin,audio,rate,chunk):
    # GPIOの初期化
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pin, GPIO.RISING)
    GPIO.add_event_callback(pin, buttonCallBack)
    # 音声デバイスのオープン
    return audio.open(   format = pyaudio.paInt16,
      channels = 1,
      rate = rate,
      frames_per_buffer = chunk,
      input = True,
      output = True) # inputとoutputを同時にTrueにする

# なにかのエラーで終了する場合は，PIDファイルを消去，GPIOの設定をリセット, オーディオをクローズ
def finish(audio,stream,pin,pidFile):
    # オーディオデバイスをクローズ
    stream.stop_stream()
    stream.close()
    audio.terminate()
    # GPIO設定をリセット
    GPIO.cleanup()
    # ファイルを消す
    if os.path.exists(pidFile):
        os.remove(pidFile)
    sys.exit()

# daemon化する処理
def fork(check,pin,pidFile,stream,chunk):
    pid = os.fork()
    if pid > 0:
        f = open(pidFile,'w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()
    if pid == 0:
        loop(check,pin,stream,chunk)

# ループの1ラウンド
def oneRound(stream,chunk):
    return
    #if (stream.is_active()):
    #    input = stream.read(CHUNK)
    #    output = stream.write(input)

# メインのループ
def loop(check,pin,stream,chunk):
    global pinState
    while True:
        if check:
            if pinState:
                oneRound(stream,chunk)
        else:
            oneRound(stream,chunk)

# メイン
if __name__ == '__main__':
    audio=pyaudio.PyAudio()
    try:
        stream=setup(BUTTON,audio,RATE,CHUNK)
    except:
        finish(BUTTON,PID_FILE)
    if DAEMON:
        try:
            fork(BUTTON_CHECK,BUTTON,PID_FILE,stream,CHUNK)
        except:
            finish(audio,stream,BUTTON,PID_FILE)
    else:
        try:
            loop(BUTTON_CHECK,BUTTON,stream,CHUNK)
        except:
            finish(audio,stream,BUTTON,PID_FILE)


