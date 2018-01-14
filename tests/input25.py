#!/usr/bin/python3

import pigpio as pig
import time
import sys

pi = pig.pi()
if not pi.connected:
    exit()

input_pin = 25
pi.set_mode(input_pin, pig.INPUT)
pi.set_pull_up_down(input_pin, pig.PUD_UP)
pi.set_glitch_filter(input_pin, 500)

pwm_pin = 18
pwm_freq= 500
pi.set_mode(pwm_pin, pig.OUTPUT)
pi.hardware_PWM(pwm_pin, pwm_freq, 0)
pi.set_PWM_frequency(pwm_pin, pwm_freq)
pi.set_PWM_dutycycle(pwm_pin, 0)

def cbfn_spc(gpio, level, tick):
    pi.set_PWM_dutycycle(pwm_pin, 0)
    sys.stdout.write('R')
    sys.stdout.flush()

def cbfn_mark(gpio, level, tick):
    pi.set_PWM_dutycycle(pwm_pin, 128)
    sys.stdout.write('P')
    sys.stdout.flush()

cb_spc  = pi.callback(input_pin, pig.RISING_EDGE,  cbfn_spc)
cb_mark = pi.callback(input_pin, pig.FALLING_EDGE, cbfn_mark)

try:
    while True:
        time.sleep(1)
    pi.set_PWM_dutycycle(pwm_pin, 0)
    pi.stop()

except KeyboardInterrupt:
    pi.set_PWM_dutycycle(pwm_pin, 0)
    pi.stop()
