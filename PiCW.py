#!/usr/bin/python3

# pycw.py - Morse Code Keyer using GPIO of Raspberry Pi
#
#   Yoshihiro Kawamata
#       (kaw@on.rim.or.jp, ex JH0NUQ)

import readline
import re

import InputOutputPort as port
import KeyingControl   as key
import StraightKeyer   as stk
import PaddleKeyer     as pdl
import MessageKeyer    as msg

# setup for Straight Key
#
key.assign(port.In_C, stk.action)

# setup for Paddle Key
#
key.assign(port.In_A, pdl.dot_action)
key.assign(port.In_B, pdl.dash_action)

# command console
#
print("Welcome to picw.py")
while True:
    try:
        line=input("\n{:.1f}WPM>".format(key.getspeed()))
    except (EOFError, KeyboardInterrupt):
        break

    # set speed of Message Keyer and Iambic Keyer
    # in WPM
    #
    if re.match(r"^[0-9.]+$", line):
        key.setspeed(float(line))

    # send text message using MessageKeyer module
    #
    elif re.match(r"^ .+", line):
        msg.sendtext(line[1:])

    # other stuff ignored
    #
    else:
        pass # (more command required for the future)

# (termination process required)
