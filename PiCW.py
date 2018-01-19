#!/usr/bin/python3

# PiCW.py - Morse Code Keyer using GPIO of Raspberry Pi
#
#   Yoshihiro Kawamata
#       (kaw@on.rim.or.jp, ex JH0NUQ)

import readline
import re
import InputOutputPort as port
import KeyingControl   as key
import PaddleKeyer     as pdl
import MessageKeyer    as msg
import CwUtilities     as utl
import ConsoleCommands as cmd

# display command help
#
def cmd_help():
    print('''PiCW.py command help:

  "wpm", "cpm" ... set speed unit to words/minute

  numbers      ... set speed of paddle and message keyer

  some "<" or ">" characters
               ... change speed +/- 5% by numbers of character
                   "<" ... decrease speed
                   ">" ... increase speed
                   example: ">>>>" means "1.05*1.05*1.05*1.05", 1.216 (22% up)
                            "<<"   means "1/(1.05*1.05)",  0.907 (10% down)

  "iambic", "reverse-iambic", "bug", "reverse-bug", "sideswiper"
            ... set paddle action
                "reverse-*" will swap paddles as normal
  space + string
            ... send string by message keyer

  "quit", "exit", Ctrl-D
            ... terminate PiCW.py

  "?"       ... display this message

Note:
    Message keyer will be aborted by typing Ctrl-D
    or by pressing a straight key or any paddle lever.'''[:-1])

# command console
#
prompt_cpm = False  #  display speed with CPM
print("Welcome to picw.py")
print("  Type '?' for help.")
while True:
    # read user's input
    #
    try:
        line=input("\n"+utl.speedstr()+":")
    except KeyboardInterrupt:
        continue
    except EOFError:
        break

    # set speed of Message Keyer and Iambic Keyer
    # in WPM
    #
    if re.match(r"[0-9.]+", line):
        key.setspeed(utl.speed2float(line))

    # change speed by +/- 5%
    #
    elif re.match(r"[<>]+$", line):
        key.setspeed(key.getspeed()*pow(1.05, line.count('>')-line.count('<')))

    # send text message using MessageKeyer module
    #
    elif re.match(r" .+", line):
        msg.sendtext(line[1:])

    # other console commands
    #
    elif not cmd.parser(line):
        break

# termination processes
#
pdl.terminate()
port.terminate()
print()
print("Bye bye...")
