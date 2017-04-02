#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import RPi.GPIO as GPIO
import time

pinState=False
BUTTON=21


def button(pin):
    global pinState
    while True:
        val=GPIO.input(pin)
        #if (1==GPIO.input(pin)):
        print "val = ",val
        if (1==val):
            pinState=True
        else:
            pinState=False
        time.sleep(2)

def setup(pin):
    GPIO.setwarnings(False)
    GPIO.cleanup()
    # GPIO指定をGPIO番号で行う
    GPIO.setmode(GPIO.BCM)
    # GPIO21ピンを出力モードに設定
    GPIO.setup(pin, GPIO.IN)

def finish(pin):
    print "exception terminate"
    # GPIO設定をリセット
    GPIO.cleanup()
    sys.exit()

def loop():
    global pinState
    while True:
        if pinState:
            print "pin is HIGH"
        else:
            print "pin is LOW"
        time.sleep(3)


if __name__ == '__main__':
    setup(BUTTON)
    button = threading.Thread(target=button, name="button", args=(BUTTON,))
    button.start()
    loop()
