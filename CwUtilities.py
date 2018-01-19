# CwUtilities - misc functions, etc... 

import sys
import tty
import termios
import KeyingControl   as key

def with_keytyping(charfunc, endfunc):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            ch=sys.stdin.read(1)
            if endfunc(ch):
                break
            else:
                charfunc(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# speed unit to display
#
disp_cpm=False # Use wpm if false

# return speed string to display
#
def speedstr():
    if disp_cpm:
        return "{:.1f}CPM".format(5.0*key.getspeed())
    else:
        return "{:.1f}WPM".format(key.getspeed())

# conver user's input string to float
#
def speed2float(speed):
    if disp_cpm:
        float(speed)/5.0
    else:
        float(speed)
