#!/usr/bin/python3

# PiCW_CheckPort.py
#   - a port monitoring daemon for TX control

import time
import sys
import InputOutputPort as port
import KeyingControl   as key
import StraightKeyer   as stk

# disable controlling all ports
#
port.bind(port.In_A, stk.null_action)
port.bind(port.In_B, stk.null_action)
port.bind(port.In_C, stk.null_action)

# monitoring TX control port
# for maxcount*interval seconds
#
# If TX control port being
# activated whole continuously,
# deactivate the port.

maxcount=30
interval=1

while True:
    while True:
        count=0
        for i in (range(maxcount)):
            stat=port.check_port(port.Out_T)
            sys.stdout.write(str(stat))
            sys.stdout.flush()
            if stat==1:
                count += 1
            time.sleep(1)
        print(' : {:02d}/{:02d}'.format(count, maxcount))
        if count==maxcount:
            key.space()
