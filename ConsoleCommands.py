# ConsoleCommands  -  commands called by command line parser

import re
import sys
import random; random.seed()
import InputOutputPort as port
import KeyingControl   as key
import StraightKeyer   as stk
import PaddleKeyer     as pdl
import MessageKeyer    as msg
import CwUtilities     as utl

# txline [off|on]
# sidetone [off|on]
# paddle [off|iambic|iambic-rev|bug|bug-rev|sideswiper]
# straight [off|on]
# kb
# send <file name>
# lesson
# show
# unit [wpm|cpm]
# load <file name>
# quit, exit, bye

# function for toggling status
#
def togglecmd(act, label, stat):
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

def txline(act=None):
    key.tx_enable=togglecmd(act, 'TX control', key.tx_enable)
    return True

def beep(act=None):
    key.beep_enable=togglecmd(act, 'side tone', key.beep_enable)
    return True

def straight(act=None):
    stk.setaction(togglecmd(act, 'straight key', stk.getaction()))
    return True

def paddle(type=None):
    def settype(act_A, act_B):
        port.bind(port.In_A, act_A)
        port.bind(port.In_B, act_B)

    if type==None:
        return True

    type=type.upper()
    if type=='OFF':
        settype(stk.null_action, stk.null_action)
    elif type=='IAMBIC':
        settype(pdl.dot_action,  pdl.dash_action)
    elif type=='IAMBIC-REV':
        settype(pdl.dash_action, pdl.dot_action)
    elif type=='BUG':
        settype(pdl.dot_action,  stk.action)
    elif type=='BUG-REV':
        settype(stk.action,      pdl.dot_action)
    elif type=='SIDESWIPER':
        settype(stk.action,      stk.action)

    return True

# transmit keyborad input directly
# change speed interactively
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
        else:
            msg.sendtext(ch)

    print("entering keyboard transmission mode...")
    print("    Type '$' to exit this mode.")
    print("    Type '<' to decrease transmission speed by 5%, '>' to increase respectively.")

    utl.with_keytyping(charfunc,
                       lambda ch : ch == '$')
    return True

# training mode
#
def training(act=None):
    chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    #chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ()-.,:"+=/'

    msg.sendtext('          ')
    print()
    msg.sendtext('HR HR = ')
    print()
    for line in range(10):
        for word in range(12):
            for char in range(5):
                if not msg.sendtext(random.choice(chars)):
                    print()
                    return True
            msg.sendtext(' ')
        print()
    msg.sendtext('+')
    print()

    return True

def bye(act=None):
    return False

# command name and its function
#
cmds={'TX':       txline,
      'BEEP':     beep,
      'STRAIGHT': straight,
      'PADDLE':   paddle,
      'KB':       keyboard_send,
      'TRAINING': training,
      'BYE':      bye,
      'EXIT':     bye,
      'QUIT':     bye}

# command line parser
#
def parser(line):
    params=re.findall(r"[^ 	]+", line)
    if params:
        cmd=params.pop(0).upper()
        if cmd in cmds.keys():
            return cmds[cmd](*params)
        else:
            print("Eh?")
            return True
    else:
        return True
