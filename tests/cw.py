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

# initialization for GPIO input ports
#
port_dit=23
port_dah=24
port_stk=25
pi.set_mode(port_dit, pigpio.INPUT)
pi.set_mode(port_dah, pigpio.INPUT)
pi.set_mode(port_stk, pigpio.INPUT)
pi.set_pull_up_down(port_dit, pigpio.PUD_UP)
pi.set_pull_up_down(port_dah, pigpio.PUD_UP)
pi.set_pull_up_down(port_stk, pigpio.PUD_UP)
pi.set_glitch_filter(port_dit, 3000)
pi.set_glitch_filter(port_dah, 3000)
pi.set_glitch_filter(port_stk, 3000)

# initialization for GPIO PWM ports
#
port_pwm=18
pwm_freq= 500
pi.set_mode(port_pwm, pigpio.OUTPUT)
pi.hardware_PWM(port_pwm, pwm_freq, 0)
pi.set_PWM_frequency(port_pwm, pwm_freq)
pi.set_PWM_dutycycle(port_pwm, 0)

# speed in words per minute
#  The word is "PARIS ", which has 50 dot length.
#
wpm=20
ditlen=60/(50*wpm)

# callback function for a straight key
#
def cb_stkey(port, level, tick):
    # key pressed
    if level==0:
        pi.set_PWM_dutycycle(port_pwm, 128)
    # key released
    elif level==1:
        pi.set_PWM_dutycycle(port_pwm, 0)
 
# register callbacks
#
cb_stk=pi.callback(port_stk, pigpio.EITHER_EDGE, cb_stkey)

# global status and notifying event
# for iambic paddles
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
            pi.set_PWM_dutycycle(port_pwm, 128)
            time.sleep(mark)
            pi.set_PWM_dutycycle(port_pwm, 0)
            time.sleep(space)

        global ditlen
        global sqz_marks

        sqz_marks=[]
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

# callback function for iambic paddles
#
def cb_iambic(port, level, tick):
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
        ev.set() # notify to iambic subthread
    # paddle released
    elif level==1:
        if port==port_dit:
            dit_mark=False
        elif port==port_dah:
            dah_mark=False
 
# register callbacks
#
cb_dit=pi.callback(port_dit, pigpio.EITHER_EDGE, cb_iambic)
cb_dah=pi.callback(port_dah, pigpio.EITHER_EDGE, cb_iambic)

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
