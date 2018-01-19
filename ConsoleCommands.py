# ConsoleCommands  -  commands called by command line parser

import re
import sys
import InputOutputPort as port
import KeyingControl   as key
import StraightKeyer   as stk
import MessageKeyer    as msg
import CwUtilities     as utl

# txline [off|on]
# sidetone [off|on]
# paddle [off|iambic|iambic-rev|bug|bug-rev|sideswiper]
# straight [off|on]
# kb
# send <file name>
# show
# unit [wpm|cpm]
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

    utl.with_keytyping(charfunc,
                       lambda ch : ch == '$')

def bye(act=None):
    return False

# command name and its function
#
cmds={'TX':       txline,
      'BEEP':     beep,
      'STRAIGHT': straight,
      'KB':       keyboard_send,
      'BYE':      bye,
      'EXIT':     bye,
      'QUIT':     bye}

# command line parser
#
def parser(line):
    params=re.findall(r"[0-9A-Za-z]+", line)
    cmd=params.pop(0).upper()
    if cmd in cmds.keys():
        return cmds[cmd](*params)
    else:
        print("Eh?")
        return True
