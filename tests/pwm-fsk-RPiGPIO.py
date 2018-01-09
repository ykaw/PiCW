#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import random

def main():
    lowhz=400
    highhz=1000
    
    # 使用する出力ピン(GPIO)
    pwm_pin = 18

    # GPIOピンの定義
    GPIO.setmode(GPIO.BCM)        # GPIO番号で指定
    GPIO.setup(pwm_pin, GPIO.OUT)
    pwm = GPIO.PWM(pwm_pin, lowhz)
    freq = lowhz
    pwm.start(50)

    for i in range(5000):
        if random.randrange(0,2) == 1:
            if freq == lowhz:
                pwm.ChangeFrequency(highhz)
                freq = highhz
            else:
                pwm.ChangeFrequency(lowhz)
                freq = lowhz
        time.sleep(0.02)

    pwm.stop()
    # GPIOピンの設定解除
    GPIO.cleanup()

if __name__ == "__main__":
    main()
