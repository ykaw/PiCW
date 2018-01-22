# ConsoleCommands  -  commands called by command line parser

import re
import sys
import subprocess
import time
import random; random.seed()
import InputOutputPort as port
import KeyingControl   as key
import StraightKeyer   as stk
import PaddleKeyer     as pdl
import TextKeyer       as txt
import MemoryKeyer     as mem
import CwUtilities     as utl

# function for toggling status - on and off
#
#     elsefunc() is a hook when ac isn't neigther 'on' or 'off'.
#
def togglecmd(act, label, stat, elsefunc=(lambda ac, lb, st: st)):
    if act==None:
        print(label,
              'is',
              'on.' if stat else 'off.')
        return stat
    elif act.upper()=='ON':
        print(label, 'enabled')
        return True
    elif act.upper()=='OFF':
        print(label, 'disabled')
        return False
    else:
        return elsefunc(act, label, stat)

# Console command - TX
#
def txline(act=None):
    key.tx_enable=togglecmd(act, 'TX control', key.tx_enable)
    return True

# Console command - BEEP
#
def beep(act=None):
    def func(ac, lb, st):
        if re.match(r"[0-9]+$", ac):
            freq=int(ac)
            if 0<freq and freq<20000:
                port.set_beepfreq(freq)
                print('Side tone set to', port.get_beepfreq(), 'Hz.')
        return st

    key.beep_enable=togglecmd(act, 'Side tone', key.beep_enable, func)
    if act==None:
        print('freq:', port.get_beepfreq(), 'Hz')
    return True

# Console Command - STRAIGHT
#
def straight(act=None):
    stk.setaction(togglecmd(act, 'Straight key', stk.getaction()))
    return True

paddletype='IAMBIC' # kludge, yet

# Console Command - PADDLE
#
def paddle(ptype=None):
    def settype(act_A, act_B):
        port.bind(port.In_A, act_A)
        port.bind(port.In_B, act_B)

    global paddletype

    if ptype==None:
        print('Paddle type is', paddletype)
        return True

    ptype=ptype.upper()
    if ptype=='OFF':          settype(stk.null_action, stk.null_action)
    elif ptype=='IAMBIC':     settype(pdl.dot_action,  pdl.dash_action)
    elif ptype=='IAMBIC-REV': settype(pdl.dash_action, pdl.dot_action)
    elif ptype=='BUG':        settype(pdl.dot_action,  stk.action)
    elif ptype=='BUG-REV':    settype(stk.action,      pdl.dot_action)
    elif ptype=='SIDESWIPER': settype(stk.action,      stk.action)
    else:
        print('? unknown paddle type -', ptype)
        print('  Paddle type is one of OFF, IAMBIC, IAMBIC-REV, BUG, BUG-REV and SIDESWIPER.')

    paddletype=ptype
    print('Paddle type is set to', paddletype)
    return True

# Console Command - KB
#
#     transmit keyboard input directly
#     and change speed interactively
#
def keyboard_send(act=None):
    def charfunc(ch):
        if ch=='>':
            key.setspeed(1.05*key.getspeed())
            print('<'+utl.speedstr()+'>', end='')
            sys.stdout.flush()
        elif ch=='<':
            key.setspeed(key.getspeed()/1.05)
            print('<'+utl.speedstr()+'>', end='')
            sys.stdout.flush()
        elif ch=="\x08" or ch=="\x7f":
            txt.sendstr('{HH}')
        else:
            txt.sendstr(ch)

    print('Entering keyboard transmission mode...')
    print("    '$', <ESC> or Ctrl-C  - exit this mode.")
    print("              (or Press straight or paddle.)")
    print("    '<' or '>'            - change speed by 5%")
    print("    <BS> or <Delete>      - send {HH}")

    # start transmission
    #
    utl.with_keytyping(charfunc,
                       lambda ch : ch == '$' or ch == "\x1b" or key.abort_requested())
    return True

# Console Command - RECORD
#
#     start/stop to record keying
#
def record(act=None):
    if act==None:
        print('Keying is ', '' if mem.recording else 'not ', 'being recorded.', sep='')
        return True

    if act.upper()=='ON':
        mem.recstart()
    elif act.upper()=='OFF':
        mem.recstop()

    return True

# Console Command - PLAY
#
#     replay recorded keying
#     with specified speed rate (default=1.0).
#
def play(speed=None):
    if speed==None:
        speed='1.0'
    if not re.match(r"[0-9.]+$", speed):
        return True
    speed=float(speed)

    mem.replay(speed,
               int(9*int(subprocess.check_output(['tput', 'cols']))/10))
               # progress bar is filled to 90% of width of terminal

    return True

# Console Command - XMIT
#
#     transmit the contents of file
#
def xmit_file(filename=None):
    if filename==None:
        return True

    try:
        with open(filename, 'rt') as infile:
            while True:
                line=infile.readline()
                if line:
                    if not (txt.sendstr(line)):
                        print()
                        return True
                else:
                    break
    except:
        print("? Can't open", filename)

    return True

# Console Command - TRAINING
#
#     training mode
#
def training(*chartypes):

    #character type
    #
    number  ='0123456789'
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    symbol  ='()-.,:"+=/'+"'"

    letters=''
    for ctype in chartypes:
        if re.match(r"all$", ctype, re.IGNORECASE):
            letters=number+alphabet+symbol
        elif re.match(r"n", ctype, re.IGNORECASE):
            letters=letters+number
        elif re.match(r"a", ctype, re.IGNORECASE):
            letters=letters+alphabet
        elif re.match(r"s", ctype, re.IGNORECASE):
            letters=letters+symbol

    # default character type
    #
    if letters=='':
        letters=number*3+alphabet*20+symbol
        # appearance: number:alhapet:symbol=3:20:1

    # size of test
    #
    lines=10  # total lines
    words=10  # words in a line
    maxwords=lines*words
    chars=5   # characters in a word

    print('Tranining mode: transmit', maxwords, 'words with', chars, 'letters...' )
    print()
    time.sleep(5)
    print('       : ', end='')
    txt.sendstr('HR HR = ')
    print()
    for line in range(lines):
        print('{:3d}/{:3d}: '.format(line*words+1, maxwords), end='')
        for word in range(words):
            for char in range(chars):
                if key.abort_requested() or not txt.sendstr(random.choice(letters)):
                    print()
                    return True
            txt.sendstr(' ')
        print()
    print('      : ', end='')
    txt.sendstr('+')

    print()
    return True

# Console Command - SHOW
#
#     display parameter settings
#
def show(act=None):
    print('Current setteings:')
    print('  Paddle and computer speed:',utl.speedstr())
    print('                 TX control:', 'ON' if key.tx_enable else 'OFF')
    print('                  Side tone:', 'ON' if key.beep_enable else 'OFF', ', freq', port.get_beepfreq(), 'Hz')
    print('               Straight key:', 'ON' if stk.getaction else 'OFF')
    print('              Paddle action:', paddletype)
    print('              Record keying:', 'ON' if mem.recording else 'OFF')
    return True

# Console Command - SPEED
#
#     change speed unit
#
def speed(act=None):
    if act==None:
        if utl.speed_unit=='CPM':
            print('Speed unit is CPM (characters per minute).')
        elif utl.speed_unit=='WPM':
            print('Speed unit is WPM (words per minute).')
        elif utl.speed_unit=='QRS':
            print('Speed unit is QRS (dot duration in seccond).')
        return True

    if act.upper()=='CPM':
        utl.speed_unit='CPM'
    elif act.upper()=='WPM':
        utl.speed_unit='WPM'
    elif act.upper()=='QRS':
        utl.speed_unit='QRS'
    else:
        print('? unknown speed unit')
        return True

    if utl.speed_unit=='CPM':
        print('Speed unit changed to CPM (characters per minute).')
    elif utl.speed_unit=='WPM':
        print('Speed unit changed to WPM (words per minute).')
    elif utl.speed_unit=='QRS':
        print('Speed unit changed to QRS (dot duration in seccond).')

    return True

# Console Command - LOAD
#
#     load sequence of commands from a file
#
def load_file(filename=None):
    if filename==None:
        return True

    try:
        with open(filename, 'rt') as infile:
            while True:
                cmdline=infile.readline()
                if cmdline:
                    parser(cmdline)
                else:
                    break
    except:
        print("? Can't open", filename)

    return True

# Console Command - HELP
#
#     display command help
#
def display_help(act=None):
    print('''PiCW.py command help:

a number:
            set speed of paddle and message keyer directly

some "<" or ">" characters:
            change speed by numbers of character
                "<" ... 5% slower
                ">" ... 5% faster

            example:  ">>>>" means 1.05*1.05*1.05*1.05 = 1.216
                             ... 22% faster
                        "<<" means 1/1.05/1.05 = 0.907
                             ... 10% slower

text string beginning with a space:
            transmit the text string directly
            Note: You can send ...-. by the notation {VA} .
                  {eeetet} is also OK.

tx [OFF|ON]         :  disable/enable controlling line to transmitter

beep [OFF|ON|freq]  :  disable/enable or set freqency[Hz] of side tone

straight [OFF|ON]   :  disable/enable straight key action

paddle [OFF|IAMBIC|IAMBIC-REV|BUG|BUG-REV|SIDESWIPER]
                    :  disable paddle action
                       or enable the paddle by specified type
                       *-rev swaps dot/dash paddle.

kb                  :  enter keyboard transmit mode
                       By pressing <ESC> or '$',
                       you can exit from this mode.

xmit <file_name>    :  transmit contets of text file

recording [OFF|ON]  :  start/stop record of keying

play [speed]        :  replay keying with the speed

training [A|N|S|ALL] ...
                    :  start training mode
                       transmit randomly-generated 100 words
                       A)lpha, N)um and S)ymbol are type of characters.
                       'training all' is same as 'training a n s'.

show                :  display settting parameters

speed [WPM|CPM|QRS] :  set speed unit words or characters per a minute

load <file_name>    :  load console command from a file

help                :  display this help message

?                   :  display short help message

quit, exit, bye     :  exit from PiCW.py

Note:
    When computer transmits text message,
    you can break that by pressing Control-C
    or by pressing a straight key or any paddle lever.'''[:-1])

    return True

# Console Command - HELP
#
#     display brief command help
#
def display_short_help(act=None):
    print('''=====[ PiCW.py commands ]======================================================
                                       |
number   : set speed                   |
"<", ">" : slower/faster               |
" "text  : transmit text directly      |
                                       |
                                       |
tx [off|on]        : TX control line   |play [speed]        : replay keying
beep [off|on|freq] : side tone         |training <CHARTYPES>: training mode
straight [off|on]  : straight key      |show                : display settings
paddle [off|iambic|iambic-rev|bug|     |speed [WPM|CPM|QRS] : toggle WPM/CPM/QRS
        bug-rev|sideswiper]            |load <file_name>    : load config
                   : paddle action     |help                : display help
kb                 : keyboard transmit |?                   : display this
xmit <file_name>   : file transmit     |quit, exit, bye     : exit from PiCW.py
record [on|off]    : record keying     |
                                       |
==========================================[ Type 'help' for more details ]====='''[:-1])

    return True

# Console Command - BYE, QUIT, EXIT
#
def bye(act=None):
    return False

# stub for unimplemented commands
#
def not_imp(act=None):
    print("Sorry, this command isn't implemented yet.")
    return True

# command name and its function
#
cmds={'TX':       txline,
      'BEEP':     beep,
      'STRAIGHT': straight,
      'PADDLE':   paddle,
      'KB':       keyboard_send,
      'XMIT':     xmit_file,
      'RECORD':   record,
      'PLAY':     play,
      'TRAINING': training,
      'SHOW':     show,
      'SPEED':    speed,
      'LOAD':     load_file,
      'HELP':     display_help,
      '?':        display_short_help,
      'BYE':      bye,
      'EXIT':     bye,
      'QUIT':     bye}

# command line parser
#
def parser(line):
    # set speed of Message Keyer and Iambic Keyer
    # in WPM, CPM or QRS
    #
    if re.match(r"[0-9.]+", line):
        key.setspeed(utl.speed2float(line))
        return True

    # change speed by +/- 5%
    #
    elif re.match(r"[<>]+$", line):
        key.setspeed(key.getspeed()*pow(1.05, line.count('>')-line.count('<')))
        return True

    # send text message using TextKeyer module
    #
    elif re.match(r" .+", line):
        key.reset_abort_request()
        txt.sendstr(line[1:])
        print()
        return True

    # call console commands
    #
    else:
        params=re.findall(r"[^\x00-\x20]+", line)
        if params:
            cmd=params.pop(0).upper()
            if cmd in cmds.keys():
                key.reset_abort_request()
                return cmds[cmd](*params)
            else:
                print("? Eh")
                return True
        else:
            return True
