# StraightKeyer - logic for a straight key

import InputOutputPort as port
import KeyingControl   as key
import MessageKeyer    as msg

# callback function
#
def action(state):
    if not actstat:
        return

    # almost pass-through
    #
    if state==key.PRESSED:
        if msg.active:
            msg.abort_request() # abort message keyer if active
        else:
            key.mark()
    elif state==key.RELEASED:
        key.space()

# initialization
#
def getaction():
    return not not actstat

def setaction(newact):
    global actstat

    if actstat != newact:
        actstat = not not newact
        if actstat:
            port.bind(port.In_C, action)
        else:
            port.bind(port.In_C, port.null_action)

actstat=False  # current status
setaction(True)
