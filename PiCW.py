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

# display command help
#
def cmd_help():
    print('''
PiCW.py command help:

  "wpm", "cpm" ... set speed unit to words/minute

  numbers      ... set speed of paddle and message keyer

  some "<" or ">" characters
               ... change speed +/- 5% by numbers of character
                   "<" ... decrease speed
                   ">" ... increase speed
                   example: ">>>>" means "1.05*1.05*1.05*1.05", 1.216 (22% up)
                            "<<"   means "1/(1.05*1.05)",  0.907 (10% down)

  "iambic", "reverse-iambic", "bug", "reverse-bug", "sidewiper"
            ... set paddle action
                "reverse-*" will swap paddles as normal
  space + string
            ... send string by message keyer

  "quit", "exit", Ctrl-D
            ... terminate PiCW.py

  "?"       ... display this message

Note:
    Message keyer will be aborted by typing Ctrl-D
    or by pressing a straight key or any paddle lever.
'''[:-1])

# parse console command
#   return False to end this program
#
def cmd_parser(line):
    global prompt_cpm
    if line == 'quit' or line == 'exit':
        return False
    elif line == 'cpm':
        prompt_cpm=True
    elif line == 'wpm':
        prompt_cpm=False
    elif line == 'iambic':
        key.assign(port.In_A, pdl.dot_action)
        key.assign(port.In_B, pdl.dash_action)
    elif line == 'reverse-iambic':
        key.assign(port.In_A, pdl.dash_action)
        key.assign(port.In_B, pdl.dot_action)
    elif line == 'bug':
        key.assign(port.In_A, pdl.dot_action)
        key.assign(port.In_B, stk.action)
    elif line == 'reverse-bug':
        key.assign(port.In_A, stk.action)
        key.assign(port.In_B, pdl.dot_action)
    elif line == 'sidewiper':
        key.assign(port.In_A, stk.action)
        key.assign(port.In_B, stk.action)
    elif line == '?':
        cmd_help()
    return True

# command console
#
prompt_cpm = False  #  display speed with CPM
print("Welcome to picw.py")
print("  Type '?' for help.")
while True:
    try:
        if prompt_cpm:
            line=input("\n{:.1f}CPM:".format(5.0*key.getspeed()))
        else:
            line=input("\n{:.1f}WPM:".format(key.getspeed()))
    except KeyboardInterrupt:
        continue
    except EOFError:
        break

    # set speed of Message Keyer and Iambic Keyer
    # in WPM
    #
    if re.match(r"[0-9.]+$", line):
        if prompt_cpm:
            key.setspeed(float(line)/5.0)
        else:
            key.setspeed(float(line))

    # change speed by +/- 5%
    #
    elif re.match(r"[<>]+$", line):
        key.setspeed(key.getspeed()*pow(1.05, line.count('>')-line.count('<')))

    # send text message using MessageKeyer module
    #
    elif re.match(r" .+", line):
        msg.sendtext(line[1:])

    # other stuffs
    #
    elif not cmd_parser(line):
        break

# termination process
pdl.terminate()
port.terminate()
print()
print("Bye bye...")
