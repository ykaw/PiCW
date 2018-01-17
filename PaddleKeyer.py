# PaddleKeyer - logic for paddles with squeezing

import threading
import InputOutputPort as port
import KeyingControl   as key
import MessageKeyer    as msg

PADDLE_NONE=0
PADDLE_DOT =1
PADDLE_DASH=2

# global status and notifying event
# for iambic paddles
#
dot_pressed =False       # current state of dot paddle. True when the paddle is being pressed.
dash_pressed =False      # current state of dash paddle.
sqz_paddles=[]           # a queue for squeezed paddle actions.
evt_pressed =PADDLE_NONE # port of pressed paddle
                         # PADDLE_NONE means both straight and iambic are idling

# this event object is used to notify any paddle pressed
# from the iambic callback function
# to iambic keying subthread
#
ev=threading.Event()

# subthread for iambic output
#
def keying_iambic():

    # send first dot or dash when iambic idling
    # then send trailing squeezed paddle actions
    #
    def output_with_squeezed(pressed):
        global sqz_paddles
        sqz_paddles=[] # gathered squeezed presseds of dots or dashes

        # alt_paddle is next dot or dash
        # when two paddles are both pressed.

        # send first dot or dash
        #
        if pressed==PADDLE_DOT:
            alt_paddle=PADDLE_DASH
            key.dot()
        elif pressed==PADDLE_DASH:
            alt_paddle=PADDLE_DOT
            key.dash()

        # send trailing dots or dashes, if any
        #
        while sqz_paddles:
            pressed=sqz_paddles.pop(0)
            if pressed==PADDLE_DOT:
                alt_paddle=PADDLE_DASH
                key.dot()
            elif pressed==PADDLE_DASH:
                alt_paddle=PADDLE_DOT
                key.dash()

        # return next dot or dash
        #
        return(alt_paddle)

    global ev_terminate
    ev_terminate=False

    while True:
        # when idling,
        # wait for any paddle will be pressed
        #
        ev.clear()
        ev.wait()

        # terminate this thread if requested
        #
        if ev_terminate:
            return

        # request abort to message keyer
        #
        if msg.active:
            msg.aborttext()
            continue

        # either of paddles were pressed
        #
        alt_paddle=output_with_squeezed(evt_pressed)

        # either or both paddle(s) are keeping to be pressed
        #
        while True:
            if dot_pressed and dash_pressed:
                alt_paddle=output_with_squeezed(alt_paddle)
            elif dot_pressed:
                alt_paddle=output_with_squeezed(PADDLE_DOT)
            elif dash_pressed:
                alt_paddle=output_with_squeezed(PADDLE_DASH)
            else:
                break

# activate iambic subthread
#
iambic=threading.Thread(target=keying_iambic)
iambic.start()

# terminate iambic subthread
#
def terminate():
    global ev_terminate
    ev_terminate=True
    ev.set()
    iambic.join()

# callback function for iambic dot paddle
#
def dot_action(port, level, tick):
    global dot_pressed, dash_pressed, evt_pressed, sqz_paddles

    # paddle pressed
    if level==0:
        dot_pressed=True
        evt_pressed=PADDLE_DOT
        sqz_paddles.append(evt_pressed)
        ev.set() # notify to iambic subthread
    # paddle released
    elif level==1:
        dot_pressed=False
        evt_pressed=PADDLE_NONE

# callback function for iambic dash paddle
#
def dash_action(port, level, tick):
    global dot_pressed, dash_pressed, evt_pressed, sqz_paddles

    # paddle pressed
    if level==0:
        dash_pressed=True
        evt_pressed=PADDLE_DASH
        sqz_paddles.append(evt_pressed)
        ev.set() # notify to iambic subthread
    # paddle released
    elif level==1:
        dash_pressed=False
        evt_pressed=PADDLE_NONE
