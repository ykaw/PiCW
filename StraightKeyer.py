# StraightKeyer - logic for a straight key

import InputOutputPort as port
import KeyingControl   as key
import MessageKeyer    as msg

# callback function
#
def action(state):

    # almost pass-through
    #
    if state==key.PRESSED:
        if msg.active:
            msg.abort_request() # abort message keyer if active
        else:
            key.mark()
    elif state==key.RELEASED:
        key.space()

# initial port binding
#
port.bind(port.In_C, action)
