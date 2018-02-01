# InputOutputPort - interface to sense/control hardware port

import time

# This module uses RPi.GPIOlibrary.
#
import RPi.GPIO as GPIO

# use Broadcom's GPIO number of BCM2835
#
GPIO.setmode(GPIO.BCM)

# definition of ports
#   The numbers are Broadcom's GPIO number of BCM2835,
#   not RPi's assigned numbers.
#
In_A=23
In_B=24
In_C=25

Out_T=22  # TX Control line
Out_M=18  # PWM output - for side tone

# initialization of input ports
#
for port in [In_A, In_B, In_C]:
    # Input will be pulled-up.
    # So, to mark input port,
    # that pin should be contacted to GND,
    # via a current-limit resistor.
    #
    GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# initialization of TX control line
#
GPIO.setup(Out_T, GPIO.OUT)

# initialization of side tone
#
Freq_M=1500 # side tone frequency (Hz)
GPIO.setup(Out_M, GPIO.OUT)
pwm=GPIO.PWM(Out_M, Freq_M)
pwm.start(0)
pwm.ChangeFrequency(Freq_M)

# activate TX control line
#
def txline_on():
    GPIO.output(Out_T, GPIO.HIGH)

# deactivate TX control line
#
def txline_off():
    GPIO.output(Out_T, GPIO.LOW)

# activate side tone
#
def beep_on():
    pwm.ChangeDutyCycle(50)

# deacitivate side tone
#
def beep_off():
    pwm.ChangeDutyCycle(0)

# get side tone frequency
#
def get_beepfreq():
    return Freq_M

# get available side tone frequencies
#
#   In RPi.GPIO, Freq. of PWM output is
#   not discrete.
#
def get_avail_beepfreq():
    return []

# set side tone frequency
#
def set_beepfreq(hz):
    global Freq_M

    Freq_M=hz
    pwm.ChangeFrequency(Freq_M)

# table for callback functions by every input port
#   empty at initial state
#
cb={}

# bind callback function to input port
#   This function is interface between pigpio and our
#   abstraction layer.
#
#   func is a function which has only parameter: func(state)
#
def bind(in_port, func):

    # In RPi.GPIO,
    # a callback function can't know it was called by rise or fall.
    # So, GPIO.input() will be called in a fallback wrapper function 'func_both'
    # to check whether detected edge is rise or fall.
    # GPIO.input() sometimes returns 1 but the port is inactive.
    # Therefore, this function takes a few samples with short interval.
    #
    def func_both(port):
        stat=1
        for i in range(3):     # sampling 3 times
            time.sleep(0.003)  # at 3ms interval
            if GPIO.input(port)==0:
                stat=0  # if it occurs even once
        func(stat)

    if in_port in cb and cb[in_port]==1:
        GPIO.remove_event_detect(in_port)  #  unassign current callback if any
        cb[in_port]=0

    GPIO.add_event_detect(in_port, GPIO.BOTH, callback=func_both, bouncetime=25)
    cb[in_port]=1

# termination process for this module
#
def terminate():

    # set output to low level
    txline_off()
    beep_off()

    # unbound all callbacks
    #
    for in_port in cb.keys():
        if in_port in cb and cb[in_port] == 1:
            GPIO.remove_event_detect(cb[in_port])

    # close connection to pigpiod
    #
    GPIO.cleanup()
