#!/usr/bin/python3

# PiCW.py - Morse Code Keyer using GPIO of Raspberry Pi
#
#   Yoshihiro Kawamata
#       (kaw@on.rim.or.jp, ex JH0NUQ)

import readline
import InputOutputPort as port
import PaddleKeyer     as pdl
import CwUtilities     as utl
import ConsoleCommands as cmd

# command console
#
prompt_cpm = False  #  display speed with CPM
print("Welcome to PiCW.py")
print("  Type '?' for the short help.")
while True:
    # read user's input
    #
    try:
        line=input("\n"+utl.speedstr()+":")
    except KeyboardInterrupt:
        continue
    except EOFError:
        break

    if not cmd.parser(line):
        break

# termination processes
#
pdl.terminate()
port.terminate()
print()
print("Bye bye...")
