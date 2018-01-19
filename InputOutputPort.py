# InputOutputPort - interface to sense/control hardware port

# This module uses pigpio library.
#   http://abyz.me.uk/rpi/pigpio/
#
import pigpio

# connect to pigpiod daemon
#
pi=pigpio.pi()
if not pi.connected:
    exit()

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
    pi.set_mode(port, pigpio.INPUT)

    # Input will be pulled-up.
    # So, to mark input port,
    # that pin should be contacted to GND,
    # via a current-limit resistor.
    #
    pi.set_pull_up_down(port, pigpio.PUD_UP)

    # anti-chattering
    # The tolerance is 3ms.
    #
    pi.set_glitch_filter(port, 3000)

# and initialization of output ports
#
pi.set_mode(Out_T, pigpio.OUTPUT)

Freq_M=500 # side tone frequency (Hz)
pi.set_mode(Out_M, pigpio.OUTPUT)
pi.hardware_PWM(Out_M, Freq_M, 0)
pi.set_PWM_frequency(Out_M, Freq_M)

# activate TX control line
#
def txline_on():
    pi.write(Out_T, 1)

# deactivate TX control line
#
def txline_off():
    pi.write(Out_T, 0)

# activate side tone
#
def beep_on():
    pi.set_PWM_dutycycle(Out_M, 128)

# deacitivate side tone
#
def beep_off():
    pi.set_PWM_dutycycle(Out_M, 0)

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
    if in_port in cb:
        cb[in_port].cancel()  #  unassign current callback if any

    cb[in_port]=pi.callback(in_port, pigpio.EITHER_EDGE, lambda p, s, t: func(s))

# termination process for this module
#
def terminate():

    # set output to low level
    txline_off()
    beep_off()

    # unbound all callbacks
    #
    for in_port in cb.keys():
        if in_port in cb:
            cb[in_port].cancel()

    # close connection to pigpiod
    #
    pi.stop()
