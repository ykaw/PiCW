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

# definition and initialization of input ports
#   The numbers are Broadcom's GPIO number of BCM2835
#   not rpi's number
#
In_A=23
In_B=24
In_C=25

for port in [In_A, In_B, In_C]:
    pi.set_mode(port, pigpio.INPUT)
    pi.set_pull_up_down(port, pigpio.PUD_UP)
    pi.set_glitch_filter(port, 3000)

# definition and initialization of output ports
#
Out_M=18   # Monitor Port (PWM)
Freq_M=500 # Monitor Frequency (Hz)

pi.set_mode(Out_M, pigpio.OUTPUT)
pi.hardware_PWM(Out_M, Freq_M, 0)
pi.set_PWM_frequency(Out_M, Freq_M)

# activate TX control line
#
def txline_on():
    pass # not implemented yet

# deactivate TX control line
#
def txline_off():
    pass # not implemented yes

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

# termination process for this module
#
def terminate():

    # close connection to pigpiod
    #
    pi.stop()
