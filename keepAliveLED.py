#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# モジュールをインポートする
import RPi.GPIO as GPIO
import time
import os
import sys
import pyping

# LEDが繋がったピン番号の定義
LED=18

# チェックする間隔
INTERVAL=10

# daemon化するか否か
DAEMON=False
PID_FILE='/var/run/keepAliveLED.pid'

# pingする先のアドレス (ルータのアドレスを知っているのがベスト)
HOST='192.168.0.1'

# GPIOのピンの設定
def setup(pin):
    # GPIO指定をGPIO番号で行う
    GPIO.setmode(GPIO.BCM)
    # GPIO21ピンを出力モードに設定
    GPIO.setup(pin, GPIO.OUT)

# ネットワークにつながっているか否かのチェック
#   ルータへのpingが通るかどうかで判定する
def networkcheck(host):
    ret=pyping.ping(host)
    if (0==ret):
        return True
    return False

def setLED(pin,flag):
    if flag:
        # LEDのピンをHIGHに設定
        GPIO.output(pin, 1)
    else:
        # LEDのピンをLOWに設定
        GPIO.output(pin, 0)

# なにかのエラーで終了する場合は，PIDファイルを消去，LEDを消して，GPIOの設定をリセット
def finish(pin,pidFile):
    # LEDのピンをLOWに設定
    GPIO.output(pin, 0)
    # GPIO設定をリセット
    GPIO.cleanup()
    # ファイルを消す
    os.remove(pidFile)
    sys.exit()

def loop(pin,interval,host):
    while True:
        if networkCheck(host):
            setLED(pin,1)
        else:
            setLED(pin,0)
        # 1秒待つ
        time.sleep(interval)

def fork(pin,pidFile,interval,host):
    pid = os.fork()
    if pid > 0:
        f = open(pidFile,'w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit()
    if pid == 0:
        loop(pin,interval,host)

if __name__ == '__main__':
    setup(LED)
    if DAEMON:
        try:
            fork(LED,PID_FILE,INTERVAL,HOST)
        except:
            finish(LED,PID_FILE)
    else:
        try:
            loop(LED,INTERVAL,HOST)
        except:
            finish(LED,PID_FILE)
 
