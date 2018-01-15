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
pi.set_glitch_filter(port_dit, 3000)
pi.set_glitch_filter(port_dah, 3000)

port_pwm=18
pwm_freq= 500
pi.set_mode(port_pwm, pigpio.OUTPUT)
pi.hardware_PWM(port_pwm, pwm_freq, 0)
pi.set_PWM_frequency(port_pwm, pwm_freq)
pi.set_PWM_dutycycle(port_pwm, 0)

# handlings for dits and dahs
#
wpm=20
ditlen=60/(50*wpm)

# global status
# and notifying event
#
dit_mark =False
dah_mark =False
evt_mark =0
sqz_marks=[]

ev=threading.Event()

# subthread for iambic output
#
def keying_iambic():
    def output_with_squeezed(mark):
        def mark_and_space(mark, space):
            global pi
            global sqz_marks
            sqz_marks=[]
            pi.set_PWM_dutycycle(port_pwm, 128)
            time.sleep(mark)
            saved_sqz_marks=sqz_marks
            pi.set_PWM_dutycycle(port_pwm, 0)
            time.sleep(space)
            sqz_marks=saved_sqz_marks
        global ditlen
        global sqz_marks
        if mark==1:
            alt_mark=2
            mark_and_space(ditlen, ditlen)
        elif mark==2:
            alt_mark=1
            mark_and_space(3*ditlen, ditlen)
        while sqz_marks:
            mark=sqz_marks.pop(0)
            if mark==1:
                alt_mark=2
                mark_and_space(ditlen, ditlen)
            elif mark==2:
                alt_mark=1
                mark_and_space(3*ditlen, ditlen)
        return(alt_mark)

    global ditlen
    global dit_mark, dah_mark, evt_mark, sqz_marks
    global ev
    while True:
        ev.clear()
        ev.wait()
        next_mark=output_with_squeezed(evt_mark)

        while True:
            if dit_mark and dah_mark:
                next_mark=output_with_squeezed(next_mark)
            elif dit_mark:
                next_mark=output_with_squeezed(1)
            elif dah_mark:
                next_mark=output_with_squeezed(2)
            else:
                break

iambic=threading.Thread(target=keying_iambic)
iambic.start()

# callback function for press/release paddles
#
def cb_func(port, level, tick):
    global dit_mark, dah_mark, evt_mark, sqz_marks
    global ev

    # paddle pressed
    if level==0:
        if port==port_dit:
            evt_mark=1
            dit_mark=True
        elif port==port_dah:
            evt_mark=2
            dah_mark=True
        sqz_marks.append(evt_mark)
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
        line=input(str(wpm) + ' WPM : ')
        wpm=float(line)
        ditlen=60/(50*wpm)
    pi.set_PWM_dutycycle(port_pwm, 0)
    pi.stop()

except (EOFError, KeyboardInterrupt):
    pi.set_PWM_dutycycle(port_pwm, 0)
    pi.stop()
