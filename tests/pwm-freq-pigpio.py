#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pigpio
import time

def main():
    # 使用する出力ピン(GPIO)
    pwm_pin = 18

    freq=50

    # GPIOピンの定義
    pi = pigpio.pi()
    pi.set_mode(pwm_pin, pigpio.OUTPUT)
    pi.hardware_PWM(pwm_pin, freq, 500000)

    for i in range(100):
        pi.set_PWM_dutycycle(pwm_pin, 0)
        time.sleep(0.5)
        pi.set_PWM_frequency(pwm_pin, freq)
        print("freq set/get =", freq, "/", pi.get_PWM_frequency(pwm_pin))
        pi.set_PWM_dutycycle(pwm_pin, 128)
        time.sleep(2)
        freq=freq+50

    pi.set_PWM_dutycycle(pwm_pin, 0)
    pi.stop()

if __name__ == "__main__":
    main()
