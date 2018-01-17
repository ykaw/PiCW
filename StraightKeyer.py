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
            port.mark()
    elif state==key.RELEASED:
        port.space()
