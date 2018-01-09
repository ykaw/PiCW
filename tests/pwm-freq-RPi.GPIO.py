#!/usr/bin/python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time

def main():
    # 使用する出力ピン(GPIO)
    pwm_pin = 18

    freq=50

    # GPIOピンの定義

    GPIO.setmode(GPIO.BCM)        # GPIO番号で指定
    GPIO.setup(pwm_pin, GPIO.OUT)
    pwm = GPIO.PWM(pwm_pin, freq)
    pwm.start(50)

    for i in range(100):
        pwm.ChangeDutyCycle(0)
        time.sleep(0.5)
        pwm.ChangeFrequency(freq)
        print "freq set =", freq
        pwm.ChangeDutyCycle(50)
        time.sleep(2)
        freq=freq+50

    pwm.ChangeDutyCycle(0)
    pwm.stop()

if __name__ == "__main__":
    main()
