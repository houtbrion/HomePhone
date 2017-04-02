#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# モジュールをインポートする
import RPi.GPIO as GPIO
import time
import os
import sys
import pyping
import netifaces

# LEDが繋がったピン番号の定義
LED=20

# チェックする間隔
INTERVAL=3

# daemon化するか否か
DAEMON=False
PID_FILE='/var/run/keepAliveLED.pid'

# pingする先のアドレス (ルータのアドレスを知っているのがベスト)
HOST='192.168.1.1'

# GPIOのピンの設定
def setup(pin):
    GPIO.setwarnings(False)
    GPIO.cleanup()
    # GPIO指定をGPIO番号で行う
    GPIO.setmode(GPIO.BCM)
    # GPIOピンを出力モードに設定
    GPIO.setup(pin, GPIO.OUT)
    # GPIOピンをLOWに設定
    GPIO.output(pin, 0)

# ネットワークにつながっているか否かのチェック
#   ルータへのpingが通るかどうかで判定する
def networkCheck(host):
    val = pyping.ping(host)
    if val.ret_code==0:
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
    print "exception terminate"
    # LEDのピンをLOWに設定
    GPIO.output(pin, 0)
    # GPIO設定をリセット
    GPIO.cleanup()
    # ファイルを消す
    if os.path.exists(pidFile):
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
        print "daemon"
        try:
            fork(LED,PID_FILE,INTERVAL,HOST)
        except:
            finish(LED,PID_FILE)
    else:
        try:
            loop(LED,INTERVAL,HOST)
        except:
            finish(LED,PID_FILE)
 
