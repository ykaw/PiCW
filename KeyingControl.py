# KeyingControl - Abstraction Layer for Keying

import time
import InputOutputPort as port
import MemoryKeyer     as mem

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
    global wpm, dotlen, cgap, wgap, cgap_rate
    if not speed:
        return # even speed is 0

    if 0.0<speed and speed<=100.0:
        wpm=speed
        dotlen=wpm2sec(wpm)
        cgap=cgap_rate*dotlen
        wgap=7.0*cgap/3.0

def getspeed():
    return wpm

cgap_rate=3.0

# cgaprate is number of dots
# between every letter
#
def setlettergap(gap):
    global cgap_rate
    cgap_rate=gap
    setspeed(getspeed()) # re-calculation

def getlettergap():
    return cgap_rate

# mark is the state when the transmission line is active.
#
def mark():
    if mem.recording:
        mem.tstamp.append(time.time())
        mem.keystat.append(PRESSED)
    if tx_enable:
        port.txline_on()
    if beep_enable:
        port.beep_on()

# space is the state when the transmission line is inactive.
#
def space():
    if mem.recording:
        mem.tstamp.append(time.time())
        mem.keystat.append(RELEASED)
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
def dot():
    sendmark(dotlen)
    sendspace(dotlen)

# send a pair of dash and trailing gap
#
def dash():
    sendmark(3.0*dotlen)
    sendspace(dotlen)

# send space between characters
#   dot/dash | gap(1) | cspc(2) | dot/dash
#            |<-----3 dots----->|
def cspc():
    sendspace(cgap-dotlen)

# output space between words
#   dot/dash | gap(1) | cspc(2) | wspc(2) | cspc(2) | dot/dash
#            |<---------------7 dots--------------->|
#
def wspc():
    sendspace(wgap+dotlen-cgap-cgap)

# flag to abort requested
#
abort=False

# store abort request
#
def abort_request():
    global abort
    abort=True

# return abort status
def abort_requested():
    return abort

# reset abort request
#
def reset_abort_request():
    global abort
    abort=False

# initialization
#
setspeed(18)
setlettergap(3.0)
port.set_beepfreq(800)
