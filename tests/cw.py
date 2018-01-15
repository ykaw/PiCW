#!/usr/bin/python3

import pigpio
import time
import threading
import readline
import sys
import re

# connect to GPIO control daemon (pigpiod)
#
pi=pigpio.pi()
if not pi.connected:
    exit()

# initialization for GPIO input ports
#
port_dit=23
port_dah=24
port_stk=25

def init_gpio_input(port):
    pi.set_mode(port, pigpio.INPUT)
    pi.set_pull_up_down(port, pigpio.PUD_UP)
    pi.set_glitch_filter(port, 3000)

init_gpio_input(port_dit)
init_gpio_input(port_dah)
init_gpio_input(port_stk)

# initialization for GPIO PWM ports
#
port_pwm=18
pwm_freq=500 # (Hz)
pi.set_mode(port_pwm, pigpio.OUTPUT)
pi.hardware_PWM(port_pwm, pwm_freq, 0)
pi.set_PWM_frequency(port_pwm, pwm_freq)

def output_off():
    pi.set_PWM_dutycycle(port_pwm, 0)

def output_on():
    pi.set_PWM_dutycycle(port_pwm, 128)

output_off()

# set speed of iambic keying and sendtext()
#
def set_speed(wpm):
    # speed in words per minute
    #  The word is "PARIS ", which has 50 dot length.
    global ditlen
    ditlen=60/(50*wpm)

# get speed of iambic keying and sendtext()
# in wpm
#
def get_speed():
    global ditlen
    return 60/(50*ditlen)

set_speed(25)

# global status and notifying event
# for iambic paddles
#
dit_pressed =False   # current state of dit paddle. True when the paddle is being pressed.
dah_pressed =False   # current state of dah paddle.
sqz_paddles=[]       # a queue for squeezed paddle actions.
evt_pressed =0       # port of pressed paddle, 0 means both straight and iambic are idling
evt_terminate=False  # to terminate iambic subthread

# callback function for a straight key
#
def cb_stkey(port, level, tick):
    global evt_pressed
    # key pressed
    if level==0:
        evt_pressed=port_stk
        output_on()
    # key released
    elif level==1:
        evt_pressed=0
        output_off()

# activate cb_stkey callback
#
cb_stk=pi.callback(port_stk, pigpio.EITHER_EDGE, cb_stkey)

# this event object is used to notify any paddle pressed
# from the iambic callback function
# to iambic keying subthread
#
ev=threading.Event()

# subthread for iambic output
#
def keying_iambic():

    # send first dit or dah when iambic idling
    # then send trailing squeezed paddle actions
    #
    def output_with_squeezed(pressed):

        # send mark and space
        # by specified durations
        #
        def mark_and_space(mark, space):
            output_on()
            time.sleep(mark)
            output_off()
            time.sleep(space)

        global sqz_paddles
        sqz_paddles=[] # gathered squeezed presseds of dits or dahs

        # alt_paddle is next dit or dah
        # when two paddles are both pressed.

        # send first dit or dah
        #
        if pressed==port_dit:
            alt_paddle=port_dah
            mark_and_space(ditlen, ditlen)
        elif pressed==port_dah:
            alt_paddle=port_dit
            mark_and_space(3*ditlen, ditlen)

        # send trailing dits or dahs, if any
        #
        while sqz_paddles:
            pressed=sqz_paddles.pop(0)
            if pressed==port_dit:
                alt_paddle=port_dah
                mark_and_space(ditlen, ditlen)
            elif pressed==port_dah:
                alt_paddle=port_dit
                mark_and_space(3*ditlen, ditlen)

        # return next dit or dah
        #
        return(alt_paddle)

    while True:
        if evt_terminate:
            return
        # when idling,
        # wait for any paddle will be pressed
        #
        ev.clear()
        ev.wait()
        if evt_terminate:
            return

        # either of paddles were pressed
        #
        alt_paddle=output_with_squeezed(evt_pressed)

        # either or both paddle(s) are keeping to be pressed
        #
        while True:
            if dit_pressed and dah_pressed:
                alt_paddle=output_with_squeezed(alt_paddle)
            elif dit_pressed:
                alt_paddle=output_with_squeezed(port_dit)
            elif dah_pressed:
                alt_paddle=output_with_squeezed(port_dah)
            else:
                break

# activate iambic subthread
#
iambic=threading.Thread(target=keying_iambic)
iambic.start()

# callback function for iambic paddles
#
def cb_iambic(port, level, tick):
    global dit_pressed, dah_pressed, evt_pressed, sqz_paddles

    # paddle pressed
    if level==0:
        if port==port_dit:
            dit_pressed=True
        elif port==port_dah:
            dah_pressed=True
        evt_pressed=port
        sqz_paddles.append(evt_pressed)
        ev.set() # notify to iambic subthread
    # paddle released
    elif level==1:
        if port==port_dit:
            dit_pressed=False
        elif port==port_dah:
            dah_pressed=False
        evt_pressed=0

# activate cb_iambic callbacks
#
cb_dit=pi.callback(port_dit, pigpio.EITHER_EDGE, cb_iambic)
cb_dah=pi.callback(port_dah, pigpio.EITHER_EDGE, cb_iambic)

# output dot and trailing
#
def dit() :
    output_on()
    time.sleep(ditlen)
    output_off()
    time.sleep(ditlen)

# output dash and trailing
#
def dah() :
    output_on()
    time.sleep(3*ditlen)
    output_off()
    time.sleep(ditlen)

# output space between characters
#
def csp() :
    time.sleep(2*ditlen)

# output space between words
#
def wsp() :
    time.sleep(2*ditlen)

# function table for dot, dash, and word space
#
functab = {'.': dit, '-': dah, ' ': wsp}

# table for morse code
#
# referring:
#     ITU-T Recommendation F.1, Operational provisions for the international
#     public telegram service, Division B, I. Morse code.
#
#     ITU-R M.1677-1, International Morse code,
#     http://www.itu.int/rec/R-REC-M.1677-1-200910-I/, 2009.
#
codetab = {'a': ".-",      'b': "-...",    'c': "-.-.",    'd': "-..",     'e': ".",
           'f': "..-.",    'g': "--.",     'h': "....",    'i': "..",      'j': ".---",
           'k': "-.-",     'l': ".-..",    'm': "--",      'n': "-.",      'o': "---",
           'p': ".--.",    'q': "--.-",    'r': ".-.",     's': "...",     't': "-",
           'u': "..-",     'v': "...-",    'w': ".--",     'x': "-..-",    'y': "-.--",
           'z': "--..",
           ' ': " ",
           '0': "-----",   '1': ".----",   '2': "..---",   '3': "...--",   '4': "....-",
           '5': ".....",   '6': "-....",   '7': "--...",   '8': "---..",   '9': "----.",
           '.': ".-.-.-",  ',': "--..--",  ':': "---...",  '?': "..--..",  "'": ".----.",
           '-': "-....-",  '/': "-..-.",   '(': "-.--.",   ')': "-.--.-",  '"': ".-..-.",
           '=': "-...-",   '+': ".-.-.",   '*': "-..-",    '@': ".--.-."}
#
# make upper and lower case letters identical
#
codetab_upper = {}
for ch in codetab :
    if ch.islower() :
        codetab_upper[ch.upper()] = codetab[ch]
codetab.update(codetab_upper)

# send characters as morse code
# ... multiple characters are concatenated as a single symbol
#     e.g. chars('SOS') sends "...___...", not "... ___ ...".
# ... An undefined character is treated as a space.
#
def chars(chrs) :
    for ch in list(chrs) :
        if ch in codetab :
            for dd in list(codetab[ch]) :
                functab[dd]()
        else :
            wsp()
    csp()

# send string as a morse code
# ... substring such as {BT} represents concatenated symbol
#
def sendtext(text) :
    concsym  = False
    concword = ''
    for ch in list(text) :
        if evt_pressed !=0:
            return
        sys.stdout.write(ch.upper())
        sys.stdout.flush()
        if concsym :
            if ch == '}' :
                chars(concword)
                concsym  = False
                concword = ''
            else :
                concword = concword + ch
        else :
            if ch == '{' :
                concsym  = True
                concword = ''
            else :
                chars(ch)

def cmd_parser(line):
    if line == 'quit' or line == 'exit':
        return False
    if re.match(r"^[0-9.]+$", line):
        set_speed(float(line))
    else:
        sendtext(line)
    return True

def terminate():
    global evt_terminate

    # iambic subthread
    evt_terminate = True
    ev.set()
    iambic.join()

    # callbacks
    cb_stk.cancel()
    cb_dit.cancel()
    cb_dah.cancel()

    # pigpio related
    output_off()
    pi.stop()

# console
#
try:
    while True:
        line=input("\n" + str(get_speed()) + ' WPM : ')
        if not cmd_parser(line):
            break
    terminate()

except (EOFError, KeyboardInterrupt):
    terminate()
