#!/usr/bin/python3

import pigpio
import time

import threading

import readline

# initialization of GPIO
#
pi=pigpio.pi()
if not pi.connected:
    exit()

port_dit=25
port_dah=24
pi.set_mode(port_dit, pigpio.INPUT)
pi.set_mode(port_dah, pigpio.INPUT)
pi.set_pull_up_down(port_dit, pigpio.PUD_UP)
pi.set_pull_up_down(port_dah, pigpio.PUD_UP)
pi.set_glitch_filter(port_dit, 1000)
pi.set_glitch_filter(port_dah, 1000)

port_pwm=18
pwm_freq= 500
pi.set_mode(port_pwm, pigpio.OUTPUT)
pi.hardware_PWM(port_pwm, pwm_freq, 0)
pi.set_PWM_frequency(port_pwm, pwm_freq)
pi.set_PWM_dutycycle(port_pwm, 0)

# handlings for dits and dahs
#
wpm=3
ditlen=60/(50*wpm)

# global status
# and notifying event
#
dit_mark=False
dah_mark=False
evt_mark=0
sqz_mark=0

ev=threading.Event()

# subthread for iambic output
#
def keying_iambic():
    global dit_mark, dah_mark, evt_mark, sqz_mark
    global ev
    while True:
        print("waiting event...")
        ev.clear()
        ev.wait()
        sqz_mark=0
        print("----awake----------")
        print("dit_mark:", dit_mark)
        print("dah_mark:", dah_mark)
        print("evt_mark:", evt_mark)
        print("sqz_mark:", sqz_mark)
        time.sleep(5)
        print("----timeout--------")
        print("dit_mark:", dit_mark)
        print("dah_mark:", dah_mark)
        print("evt_mark:", evt_mark)
        print("sqz_mark:", sqz_mark)

iambic=threading.Thread(target=keying_iambic)
iambic.start()

# general callback function
#
def cb_func(port, level, tick):
    global dit_mark, dah_mark, evt_mark, sqz_mark
    global ev

    # paddle pressed
    if level==0:
        if port==port_dit:
            evt_mark=1
            dit_mark=True
        elif port==port_dah:
            evt_mark=2
            dah_mark=True
        if sqz_mark==0:
            sqz_mark=evt_mark
        # notify to iambic subthread
        ev.set()

    # paddle released
    elif level==1:
        if port==port_dit:
            dit_mark=False
        elif port==port_dah:
            dah_mark=False
 
# register callbacks
#
cb_dit=pi.callback(port_dit, pigpio.EITHER_EDGE, cb_func)
cb_dah=pi.callback(port_dah, pigpio.EITHER_EDGE, cb_func)

# command loop
#
try:
    while True:
        line=input('CW : ')
        print("--->", line)
    pi.set_PWM_dutycycle(port_pwm, 0)
    pi.stop()

except (EOFError, KeyboardInterrupt):
    pi.set_PWM_dutycycle(port_pwm, 0)
    pi.stop()
