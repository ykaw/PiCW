#!/usr/bin/python3

import argparse
import sys
import InputOutputPort as port
import KeyingControl   as key
import TextKeyer       as txt

cmdopt = argparse.ArgumentParser()
cmdopt.add_argument("-s", type=int, default=25)
args = cmdopt.parse_args()

key.setspeed(args.s)

# termination process
#
def terminate():
    port.terminate()
    print()
    print("Bye bye...")

# main read loop
#
try :
    for line in sys.stdin :
        if not txt.sendstr(line):
            break

    terminate()

except KeyboardInterrupt :
    terminate()
