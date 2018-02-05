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


#----[ Timing Chart of Sending Morse Codes  ]-----------------------------------------------------------------------------------------------------------
#                                                                                                                                                      |
#                                                                                                                                                      |
# A dot                                                                                                                                                |
#                                                                                                                                                      |
#   Status |===MARK=====|   SPACE    |                                                                                                                 |
# Duration |<- dotlen ->|<- dotlen ->|                                                                                                                 |
# Function |......... dot() .........|                                                                                                                 |
#                                                                                                                                                      |
#                                                                                                                                                      |
# A dash                                                                                                                                               |
#                                                                                                                                                      |
#   Status  |================MARK==================|   SPACE    |                                                                                      |
# Duration  |<-------------- 3*dotlen ------------>|<- dotlen ->|                                                                                      |
# Function  |.................... dash() .......................|                                                                                      |
#                                                                                                                                                      |
#                                                                                                                                                      |
# A space between characters                                                                                                                           |
#                                                                                                                                                      |
#   Status  ===character MARK====|                SPACE                 |===character MARK====                                                         |
# Duration  dotlen or 3*dotlen ->|<- dotlen ->|<------ cgap-dotlen ---->|<- dotlen or 3*dotlen                                                         |
#                                |<------ cgap (cgaprate*dotlen) ------>|                                                                              |
#                                |<--------- normally 3*dotlen -------->|                                                                              |
# Function  ....................... txt.chars(ch) ......................|... txt.chars(ch) ....                                                        |
#           ......... dot() or dash() ........|........ cspc() .........|... dot() or dash() ..                                                        |
#                                                                                                                                                      |
#                                                                                                                                                      |
# A space between words                                                                                                                                |
#                                                                                                                                                      |
#   Status  ========word MARK====|                                          SPACE                                           |===word MARK=========     |
# Duration  dotlen or 3*dotlen ->|<- dotlen ->|<------ cgap-dotlen ---->|<- wgap-dotlen-2*cgap -->|<------ cgap-dotlen ---->|<- dotlen or 3*dotlen     |
#                                |<------ cgap (cgaprate*dotlen) ------>|                         |                         |                          |
#                                |<--------------------------------- normally 7*dotlen ------------------------------------>|                          |
# Function  ....................... txt.chars(ch) ......................|.................. txt.chars(' ') .................|... txt.chars(ch) ....    |
#           ......... dot() or dash() ........|........ cspc() .........|..........wspc().........|........ cspc() .........|... dot() or dash() ..    |
#                                                                                                                                                      |
#                                                                                                                                                      |
#-------------------------------------------------------------------------------------------------------------------------------------------------------


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
    global wpm, dotlen, cgap, wgap, cgap_rate, sendable_dots
    if not speed:
        return # even speed is 0

    if 0.0<speed and speed<=100.0:
        wpm=speed
        dotlen=wpm2sec(wpm)
        cgap=cgap_rate*dotlen
        wgap=7.0*cgap/3.0
        # max dots to send for fail-safe (60 sec)
        sendable_dots=max(int(60/2/dotlen), 1)

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
#
def cspc():
    sendspace(cgap-dotlen)

# output space between words
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
