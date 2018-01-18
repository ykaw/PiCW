# CwUtilities - misc functions, etc... 

def with_keytyping(charfunc, endfunc):
    import sys
    import tty
    import termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            ch=sys.stdin.read(1)
            if endfunc(ch):
                break
            else:
                charfunc(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
