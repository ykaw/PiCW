# ConsoleCommands  -  commands called by command line parser

import re
import sys
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

def txline(act=None):
    key.tx_enable=togglecmd(act, 'TX control', key.tx_enable)
    return True

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

def straight(act=None):
    stk.setaction(togglecmd(act, 'Straight key', stk.getaction()))
    return True

paddletype='IAMBIC' # kludge, yet
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

# transmit keyborad input directly
# and change speed interactively
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
    print("    '$' or <ESC>     - exit this mode.")
    print("    '<' or '>'       - change speed by 5%")
    print("    <BS> or <Delete> - send {HH}")

    utl.with_keytyping(charfunc,
                       lambda ch : ch == '$' or ch == "\x1b" or key.abort_requested())
    return True

# start/stop to record keying
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

# replay recorded keying
#
def play(speed=None):
    if speed==None:
        speed='1.0'
    if not re.match(r"[0-9.]+$", speed):
        return True
    speed=float(speed)

    mem.replay(speed)
    return True

# transmit the contents of file
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
                        return True
                else:
                    break
    except:
        print("? Can't open", filename)

    return True

# training mode
#
def training(*chartypes):

    #character type
    #
    number  ='0123456789'
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    symbol  ='()-.,:"+=/'+"'"

    letters=''
    for ctype in chartypes:
        if re.match(r"num", ctype, re.IGNORECASE):
            letters=letters+number
        elif re.match(r"alpha", ctype, re.IGNORECASE):
            letters=letters+alphabet
        elif re.match(r"sym", ctype, re.IGNORECASE):
            letters=letters+symbol
        elif re.match(r"all$", ctype, re.IGNORECASE):
            letters=number*3+alphabet*20+symbol

    # default character type
    #
    if letters=='':
        letters=number*3+alphabet*20+symbol

    # size of test
    #
    lines=10
    words=10
    chars=5

    print()
    print('Tranining mode: transmit', lines*words, 'words with', chars, 'letters...' )
    time.sleep(5)
    txt.sendstr('HR HR = ')
    print()
    for line in range(lines):
        for word in range(words):
            for char in range(chars):
                if key.abort_requested() or not txt.sendstr(random.choice(letters)):
                    print()
                    return True
            txt.sendstr(' ')
        print()
    txt.sendstr('+')

    print()
    return True

# display parameter settings
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

# change speed unit
#
def speed(act=None):
    if act==None:
        if utl.disp_cpm:
            print('Speed unit is CPM (characters per minute).')
        else:
            print('Speed unit is WPM (words per minute).')
        return True

    if act.upper()=='CPM':
        utl.disp_cpm=True
    elif act.upper()=='WPM':
        utl.disp_cpm=False
    else:
        return True

    if utl.disp_cpm:
        print('Speed unit changed to CPM (characters per minute).')
    else:
        print('Speed unit changed to WPM (words per minute).')

    return True

# load sequence of commands from a file
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

# display command help
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

tx [off|on]         :  disable/enable controlling line to transmitter

beep [off|on|freq]  :  disable/enable/set freqency of side tone

straight [off|on]   :  disable/enable straight key action

paddle [off|iambic|iambic-rev|bug|bug-rev|sideswiper]
                    :  disable paddle action
                       or enable the paddle by specified type
                       *-rev swaps dot/dash paddle.

kb                  :  enter keyboard transmit mode
                       By pressing <ESC> or '$',
                       you can exit from this mode.

xmit <file_name>    :  transmit contets of text file

recording [off|on]  :  start/stop record of keying

play [speed]        :  replay keying with the speed

training [alpha|num|symbol|all] ...
                    :  start training mode
                       transmit randomly-generated 100 words
                       alpha, num and symbol are type of characters.
                       'all' is same as 'training alpha num symbol'.

show                :  display settting parameters

speed [wpm|cpm]     :  set speed unit words or characters per a minute

load <file_name>    :  load console command from a file

help                :  display this help message

?                   :  display short help message

quit, exit, bye     :  exit from PiCW.py

Note:
    When computer transmits text message,
    you can break that by pressing Control-C
    or by pressing a straight key or any paddle lever.'''[:-1])

    return True

# display brief command help
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
paddle [off|iambic|iambic-rev|         |speed [wpm|cpm]     : toggle WPM/CPM
        bug|bug-rev|sideswiper]        |load <file_name>    : load config
                   : paddle action     |help                : display help
kb                 : keyboard transmit |?                   : display this
xmit <file_name>   : file transmit     |quit, exit, bye     : exit from PiCW.py
record [on|off]    : record keying     |
                                       |
==========================================[ Type 'help' for more details ]====='''[:-1])

    return True

def bye(act=None):
    return False

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
    # in WPM or CPM
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
