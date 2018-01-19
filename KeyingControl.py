# KeyingControl - Abstraction Layer for Keying

import time
import pigpio
import InputOutputPort as port

# key/paddle status
#   for callback functions
#
PRESSED =0
RELEASED=1

# control status for output
#
tx_enable  =True
beep_enable=True

# convert wpm to duration of a dot (sec)
#
def wpm2sec(speed):
    return 60/(50*speed)

# set speed of keying at
#  - text message keyer
#  - iambic keyer
#  - dots of bug keyer
#
def setspeed(speed):
    global wpm, dotlen
    if 0.0<speed and speed<=100.0:
        wpm=speed
        dotlen=wpm2sec(wpm)

def getspeed():
    return wpm

# set initial speed at default
#
setspeed(25)

# mark is the state when the transmission line is active.
#
def mark():
    if tx_enable:
        port.txline_on()
    if beep_enable:
        port.beep_on()

# space is the state when the transmission line is inactive.
#
def space():
    if tx_enable:
        port.txline_off()
    if beep_enable:
        port.beep_off()

# make transmission line active for sec
#
def sendmark(sec):
    mark()
    time.sleep(sec)

# make transmission line inactive for sec
#
def sendspace(sec):
    space()
    time.sleep(sec)

# send a pair of dot and trailing gap
#
def dot() :
    sendmark(dotlen)
    sendspace(dotlen)

# send a pair of dash and trailing gap
#
def dash() :
    sendmark(3.0*dotlen)
    sendspace(dotlen)

# send space between characters
#   dot/dash | gap(1) | cspc(2) | dot/dash
#            |<-----3 dots----->|
def cspc() :
    sendspace(2*dotlen)

# output space between words
#   dot/dash | gap(1) | cspc(2) | wspc(2) | cspc(2) | dot/dash
#            |<---------------7 dots--------------->|
#
def wspc() :
    sendspace(2*dotlen)
