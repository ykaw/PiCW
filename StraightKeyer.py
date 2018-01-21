# StraightKeyer - logic for a straight key

import InputOutputPort as port
import KeyingControl   as key
import TextKeyer       as txt

# callback function
#
def action(state):
    # almost pass-through
    #
    if state==key.PRESSED:
        key.abort_request() # request to abort message keyer
        key.mark()
    elif state==key.RELEASED:
        key.space()


# callback function to do nothing
#
def null_action(port):
    key.abort_request()

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
            port.bind(port.In_C, null_action)

actstat=False  # current status
setaction(True)
