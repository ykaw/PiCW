# PaddleKeyer - logic for paddles with squeezing

import threading
import InputOutputPort as port
import KeyingControl   as key
import StraightKeyer   as stk
import CwUtilities     as utl

# states of a paddle
#
PADDLE_NONE=0 # unknown
PADDLE_DOT =1
PADDLE_DASH=2

# global status and notifying event
# for iambic paddles
#
pressing_dot =False  # current state of dot paddle. True when the paddle is being pressed.
pressing_dash=False  # current state of dash paddle.
trig_paddle=PADDLE_NONE  # paddle invoked event
sqz_paddle=PADDLE_NONE   # squeezed paddle while keying

# this event object is used to notify any paddle pressed
# from the iambic callback function
# to iambic keying subthread
#
ev_trigger=threading.Event()

# subthread for iambic output
#
def keying_iambic():

    # send dot or dash
    #
    def send(k):
        if k==PADDLE_DOT:
            key.dot()
            # If Straight key is also being pressed,
            # decrease speed
            if stk.pressing and tune_speed:
                key.setspeed(key.getspeed()-0.5)
                print('<', utl.speedstr(), '>', sep='')
        elif k==PADDLE_DASH:
            key.dash()
            # increase speed as of dot
            if stk.pressing and tune_speed:
                key.setspeed(key.getspeed()+1.5)
                print('<', utl.speedstr(), '>', sep='')

    # returns opposite paddle
    #
    def flip(k):
        if k==PADDLE_DOT:
            return PADDLE_DASH
        elif k==PADDLE_DASH:
            return PADDLE_DOT

    global ev_terminate
    ev_terminate=False

    global sqz_paddle

    global modeB
    modeB=False  # default: mode A

    while True:
        # when idling,
        # wait for any paddle will be pressed
        ev_trigger.clear()
        ev_trigger.wait()
        key.abort_request() # request abort to message keyer

        if ev_terminate: # terminate this thread if requested
            return

        # sequences of keying
        #
        modeB_sqz=PADDLE_NONE  # first squeezed paddle of every event
        sendkey=trig_paddle    # send by triggered paddle

        # send squeezed key
        #   or keep pressing
        #
        global maxdotslen
        for i in range(maxdotslen):  # for fail-safe (60 sec max)
            sqz_paddle=PADDLE_NONE  # possibly changed while calling send()
            send(sendkey)

            # send last dot/dash ?
            #
            if modeB \
               and modeB_sqz==PADDLE_NONE \
               and pressing_dot and pressing_dash:
                modeB_sqz=sqz_paddle

            # determine next dot/dash
            #
            if not sqz_paddle==PADDLE_NONE:  # squeezed. send it
                sendkey=sqz_paddle

            # what to send, by status of pressing paddles
            #
            elif pressing_dot:
                if pressing_dash:  # pressing both
                    sendkey=flip(sendkey)
                else:              # pressing only dot
                    sendkey=PADDLE_DOT
            else:
                if pressing_dash:  # pressing only dash
                    sendkey=PADDLE_DASH
                else:              # pressing none
                    if modeB and not modeB_sqz==PADDLE_NONE:
                        send(flip(sendkey))
                    break

# callback function for iambic dot paddle
#
def dot_action(state):
    global pressing_dot, trig_paddle, sqz_paddle

    # paddle pressed
    if state==key.PRESSED:
        pressing_dot=True
        trig_paddle=PADDLE_DOT
        if sqz_paddle==PADDLE_NONE:
            sqz_paddle=PADDLE_DOT
        ev_trigger.set() # notify to iambic subthread
    # paddle released
    elif state==key.RELEASED:
        pressing_dot=False
        trig_paddle=PADDLE_NONE # ignore releasing

# callback function for iambic dash paddle
#
def dash_action(state):
    global pressing_dash, trig_paddle, sqz_paddle

    # paddle pressed
    if state==key.PRESSED:
        pressing_dash=True
        trig_paddle=PADDLE_DASH
        if sqz_paddle==PADDLE_NONE:
            sqz_paddle=PADDLE_DASH
        ev_trigger.set() # notify to iambic subthread
    # paddle released
    elif state==key.RELEASED:
        pressing_dash=False
        trig_paddle=PADDLE_NONE # ignore releasing

# property for every paddle type
#
#         paddle        ----------actions for-----------  Is speed
#         type          In_A             In_B             tunable?
typetab={'OFF':        [stk.null_action, stk.null_action, False],
         'IAMBIC':     [dot_action,      dash_action,     True],
         'IAMBIC-REV': [dash_action,     dot_action,      True],
         'BUG':        [dot_action,      stk.action,      False],
         'BUG-REV':    [stk.action,      dot_action,      False],
         'SIDESWIPER': [stk.action,      stk.action,      False]}

# set paddle type
#   returns True if setting succeeded
#
def settype(ptype):
    global paddle_type
    global tune_speed

    ptype=ptype.upper()
    if ptype in typetab.keys():
        port.bind(port.In_A, typetab[ptype][0])
        port.bind(port.In_B, typetab[ptype][1])
        paddle_type=ptype
        tune_speed=typetab[ptype][2]
        return True
    else:
        return False

# return paddle type
#
def gettype():
    return paddle_type

# activate iambic subthread
#
iambic=threading.Thread(target=keying_iambic)
iambic.start()

# initial port bindings
#
settype('IAMBIC')

# terminate process
#
def terminate():
    global ev_terminate

    # terminate iambic subthread
    #
    ev_terminate=True
    ev_trigger.set()
    iambic.join()
