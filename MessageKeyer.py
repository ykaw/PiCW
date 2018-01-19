# MessageKeyer - encode text string to morse keying

import sys
import InputOutputPort as port
import KeyingControl   as key

# function table for dot, dash, and word space
#
functab = {'.': key.dot, '-': key.dash, ' ': key.wspc}

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
            key.wspc()
    key.cspc()

# send string as a morse code
# ... substring such as {BT} represents concatenated symbol
#
def sendtext(text) :
    global active, abort

    concsym =False
    concword=''

    abort=False
    active = True
    for ch in list(text) :
        try:
            if abort:
                active=False
                return False
            sys.stdout.write(ch.upper())
            sys.stdout.flush()
            if concsym :
                if ch == '}' :
                    chars(concword)
                    concsym =False
                    concword=''
                else :
                    concword=concword + ch
            else :
                if ch == '{' :
                    concsym =True
                    concword=''
                else :
                    chars(ch)

        except KeyboardInterrupt:
            key.space()
            active=False
            return False

    # all text sent
    active=False
    return not abort

# statuses for abort sending
#
active=False  # true if sending
abort=False   # true if abort requested by other keyer

# store abort request
#
def abort_request():
    global abort
    abort=True
