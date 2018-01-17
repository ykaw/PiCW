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

# parse console command
#   return False to end this program
#
def cmd_parser(line):
    if line == 'quit' or line == 'exit':
        return False
    else:
        sendtext(line)
    return True

# command console
#
print("Welcome to picw.py")
while True:
    try:
        line=input("\n{:.1f}WPM>".format(key.getspeed()))
    except KeyboardInterrupt:
        continue
    except EOFError:
        break

    # set speed of Message Keyer and Iambic Keyer
    # in WPM
    #
    if re.match(r"[0-9.]+$", line):
        key.setspeed(float(line))

    # send text message using MessageKeyer module
    #
    elif re.match(r" .+", line):
        msg.sendtext(line[1:])

    # other stuff ignored
    #
    elif not cmd_parser(line):
        break

# termination process
pdl.terminate()
port.terminate()
print()
print("Bye bye...")
