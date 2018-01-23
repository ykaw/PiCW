#!/usr/bin/python3

import argparse
import sys
import InputOutputPort as port
import KeyingControl   as key
import TextKeyer       as txt

cmdopt = argparse.ArgumentParser()
cmdopt.add_argument("-s", type=int, default=30)
cmdopt.add_argument("-f", type=int, default=500)
args = cmdopt.parse_args()

key.setspeed(args.s)
port.set_beepfreq(args.f)

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
