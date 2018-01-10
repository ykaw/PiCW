#!/usr/bin/python3

import argparse
import pigpio
import time
import sys

cmdopt = argparse.ArgumentParser()
cmdopt.add_argument("-s", type=int, default=25)
cmdopt.add_argument("-f", type=int, default=500)
args = cmdopt.parse_args()

# PWM output stuffs
#
pwm_out = 18
pwm_freq = args.f

pi = pigpio.pi()
pi.set_mode(pwm_out, pigpio.OUTPUT)
pi.hardware_PWM(pwm_out, pwm_freq, 0)
pi.set_PWM_frequency(pwm_out, pwm_freq)
pi.set_PWM_dutycycle(pwm_out, 0)

def beep(sec) :
    pi.set_PWM_dutycycle(pwm_out, 128)
    time.sleep(sec)
    pi.set_PWM_dutycycle(pwm_out, 0)

def beepfinish() :
    pi.set_PWM_dutycycle(pwm_out, 0)
    pi.stop()


# speed in words per minute
#  The word is "PARIS ", which has 50 dot length.
#
wpm = args.s
ditlen = 60/(50*wpm) # dot length in second

# output dot and trailing
#
def dit() :
    beep(ditlen)
    time.sleep(ditlen)

# output dash and trailing
#
def dah() :
    beep(3*ditlen)
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
def morse(text) :
    concsym  = False
    concword = ''
    for ch in list(text) :
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

# main read loop
#
try :
    for line in sys.stdin :
        morse(line)

    beepfinish()

except KeyboardInterrupt :
    beepfinish()
