#!/usr/bin/python3

# PiCW.py - Morse Code Keyer using GPIO of Raspberry Pi
#
#   Yoshihiro Kawamata
#       (kaw@on.rim.or.jp, ex JH0NUQ)

import readline
import os.path
import InputOutputPort as port
import PaddleKeyer     as pdl
import CwUtilities     as utl
import MemoryKeyer     as mem
import ConsoleCommands as cmd

print("Welcome to PiCW.py")
print("  Type '?' for the short help.")

# load initial configuration file
#
initfile=os.path.expanduser('~/.picwrc')
try:
    if os.path.exists(initfile):
        print()
        cmd.load_file(initfile)
except:
    pass

# command console
#
while True:
    # read user's input
    #
    try:
        line=input("\n"+utl.speedstr()+\
                   ('/REC' if mem.recording else '')+\
                   ':')
        print()
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
