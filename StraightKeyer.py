# StraightKeyer - logic for a straight key

import InputOutputPort as port
import KeyingControl   as key
import MessageKeyer    as msg

# callback function
#
def action(in_port, state, tick):

    # almost pass-through
    #
    if state==key.PRESSED:
        if msg.active:
            msg.aborttext() # abort message keyer if active
        else:
            key.mark()
    elif state==key.RELEASED:
        key.space()

# Initial port assignment
#
key.assign(port.In_C, action)
