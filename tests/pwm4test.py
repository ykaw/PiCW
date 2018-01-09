#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pigpio
import time

class pwm:
    def __init__:
    def on:
    def off:
    def stop:

def main():
    lowhz=400
    highhz=1000
    
    # 使用する出力ピン(GPIO)
    pwm_pin = 18

    # GPIOピンの定義
    p = pigpio.pi()
    p.set_mode(pwm_pin, pigpio.OUTPUT)
    p.hardware_PWM(pwm_pin, lowhz, 0)

    freq = lowhz

    for i in range(5000):
        if random.randrange(0,2) == 1:
            if freq == lowhz:
                p.set_PWM_dutycycle(pwm_pin, 0)
                p.set_PWM_frequency(pwm_pin, highhz)
                p.set_PWM_dutycycle(pwm_pin, 128)
                freq = highhz
            else:
                p.set_PWM_dutycycle(pwm_pin, 0)
                p.set_PWM_frequency(pwm_pin, lowhz)
                p.set_PWM_dutycycle(pwm_pin, 128)
                freq = lowhz
        time.sleep(0.02)

    p.set_PWM_dutycycle(pwm_pin, 0)
    p.stop()

if __name__ == "__main__":
    main()
