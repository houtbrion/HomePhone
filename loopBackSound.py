#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# モジュールをインポートする
import pyaudio
import RPi.GPIO as GPIO
#import time
import os
import sys

# ボタンが繋がったピン番号の定義
BUTTON=20

# ボタンのタイプ
BUTTON_TYPE=0 # プルダウン式
#BUTTON_TYPE=1 # プルアップ式

# チェックする間隔
INTERVAL=1

# daemon化するか否か
DAEMON=False
PID_FILE='/var/run/homePhone.pid'

# 音声処理のパラメータ
RATE=44100
CHUNK=1024

# GPIOのピンの設定
def setup(pin,audio,rate,chunk):
    # GPIO指定をGPIO番号で行う
    GPIO.setmode(GPIO.BCM)
    # GPIO21ピンを出力モードに設定
    GPIO.setup(pin, GPIO.IN)
    return audio.open(	format = pyaudio.paInt16,
		channels = 1,
		rate = rate,
		frames_per_buffer = chunk,
		input = True,
		output = True) # inputとoutputを同時にTrueにする

# なにかのエラーで終了する場合は，PIDファイルを消去，GPIOの設定をリセット, オーディオをクローズ
def finish(pin,pidFile):
    # オーディオデバイスをクローズ
    stream.stop_stream()
    stream.close()
    p.terminate()
    # GPIO設定をリセット
    GPIO.cleanup()
    # ファイルを消す
    os.remove(pidFile)
    sys.exit()

# ボタンのチェック
def checkButton(pin):
    return GPIO.input(pin)

# daemon化する処理
def fork(pin,pidFile,stream,chunk):
    pid = os.fork()
    if pid > 0:
        f = open(pidFile,'w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()
    if pid == 0:
        loop(pin,stream,chunk)

# ループの1ラウンド
def oneRound(stream,chunk):
    if (stream.is_active()):
	input = stream.read(CHUNK)
	output = stream.write(input)

# メインのループ
def loop(pin,stream,chunk):
    while True:
        if (1==buttonCheck(pin)):
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
            fork(BUTTON,PID_FILE,stream,CHUNK)
        except:
            finish(BUTTON,PID_FILE)
    else:
        try:
            loop(BUTTON,stream,CHUNK)
        except:
            finish(BUTTON,PID_FILE)






