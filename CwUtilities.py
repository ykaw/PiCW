# CwUtilities - misc functions, etc... 

import sys

#
# Both don't work as expected yet.
#

def getc():
    return sys.stdin.read(1)

def getch():
    import tty
    import termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
