#!/usr/bin/python3

# output dot and trailing space
#
def dit():
    print("=_", end='')

# output dash and trailing space
#
def dah():
    print("===_", end='')

# output space between characters
#
def csp():
    print("..", end='')

# output space between words
#
def wsp():
    print(",,", end='')


# function table for dot, dash, and word space
#
functab={'.': dit, '-': dah, ' ': wsp}

# table for morse code
#
codetab={'a': ".-",
         'b': "-...",
         'c': "-.-.",
         'd': "-..",
         'e': ".",
         'f': "..-.",
         'g': "--.",
         'h': "....",
         'i': "..",
         'j': ".---",
         'k': "-.-",
         'l': ".-..",
         'm': "--",
         'n': "-.",
         'o': "---",
         'p': ".--.",
         'q': "--.-",
         'r': ".-.",
         's': "...",
         't': "-",
         'u': "..-",
         'v': "...-",
         'w': ".--",
         'x': "-..-",
         'y': "-.--",
         'z': "--..",
         ' ': " ",
         '0': "-----",
         '1': ".----",
         '2': "..---",
         '3': "...--",
         '4': "....-",
         '5': ".....",
         '6': "-....",
         '7': "--...",
         '8': "---..",
         '9': "----.",
         '.': ".-.-.-",
         ',': "--..--",
         ':': "---...",
         '?': "..--..",
         "'": ".----.",
         '-': "-....-",
         '/': "-..-.",
         '(': "-.--.",
         ')': "-.--.-",
         '"': ".-..-.",
         '=': "-...-",
         '+': ".-.-.",
         '*': "-..-",
         '@': ".--.-."}

# make upper and lower case letters identical
#
codetab_upper = {}
for ch in codetab:
    if ch.islower():
        codetab_upper[ch.upper()] = codetab[ch]
codetab.update(codetab_upper)

# send characters as morse code
# ... multiple characters are concatenated as a single symbol
#     e.g. chars('SOS') sends "...___...", not "... ___ ...".
# ... An undefined character is treated as a space.
def chars(chrs):
    for ch in list(chrs):
        if ch in codetab:
            for dd in list(codetab[ch]):
                functab[dd]()
        else:
            wsp()
    csp()

# send string as a morse code
#
def morse(text):
    for ch in list(text):
        chars(ch)


# Test Code
#
morse('hr hr =')
print()
morse('vvv VVV vvv DE jh0nuq JH0NUQ JH0NUQ')
print()
morse('+')
print()
