# ConsoleCommands  -  commands called by command line parser

import re
import subprocess
import time
import readline
import os
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

# Console Command - PADDLE
#
def paddle(ptype=None):
    if ptype==None:
        print('Paddle type is ', pdl.gettype(), '.', sep='')
        return True

    if pdl.settype(ptype):
        print('Paddle type is set to ', pdl.gettype(), '.', sep='')
    else:
        print('? unknown paddle type -', ptype)
        print('  Paddle type is one of ' , ', '.join(sorted(pdl.typetab.keys())), '.', sep='')
    return True

# Console Command - IAMBIC
#
#     set iambic operation mode
#
def iambic(mode=None):
    if mode==None:
        print('Iambic operation mode is type', 'B.' if pdl.modeB else 'A.')
        return True

    if mode.upper()=='A':
        pdl.modeB=False
        print('Iambic operation mode is set to A.')
    elif mode.upper()=='B':
        pdl.modeB=True
        print('Iambic operation mode is set to B.')

    return True

# Console Command - KB
#
#     transmit keyboard input directly
#     and change speed interactively
#
def kb_send(act=None):
    def charfunc(ch):
        if ch=="\x08" or ch=="\x7f":
            txt.sendstr('[HH]')
        else:
            txt.sendstr(ch)


    print('Entering keyboard transmission mode...')
    print("    '$', <ESC> or Ctrl-C  - exit this mode.")
    print("              (or Press straight or paddle.)")
    print("    '<' or '>'            - change speed by 0.5WPM")
    print("    <BS> or <Delete>      - send [HH]")

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

    if act.upper() in ['ON', 'START']:
        mem.recstart()
    elif act.upper() in ['OFF', 'STOP']:
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
def xmit_file(*filenames):
    if len(filenames)==0:
        print('? no file name given')
        return True

    for txtfile in filenames:
        try:
            with open(txtfile, 'rt') as message:
                while True:
                    line=message.readline()
                    if line:
                        if not (txt.sendstr(line)):
                            print()
                            return True
                    else:
                        break
        except:
            print("? Can't open", txtfile)

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
    symbol  ='.,:?-/()"=+*@'+"'"

    letters=''
    for ctype in chartypes:
        if ctype in 'Nn':
            letters=letters+number
        elif ctype in 'Aa':
            letters=letters+alphabet
        elif ctype in 'Ss':
            letters=letters+symbol
        else:
            for ch in ctype:
                if ch.upper() in number+alphabet+symbol:
                    letters=letters+ch

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
    print('       : ', end='')
    txt.sendstr('+')

    print()
    return True

# Console Command - SHOW
#
#     display parameter settings
#
def show(act=None):
    print('Current settings:')
    print('  Paddle and computer speed:', utl.speedstr())
    print('   Gap between every letter:', key.getlettergap(), 'of dots.')
    print('                 TX control:', 'ON' if key.tx_enable else 'OFF')
    print('                  Side tone:', 'ON' if key.beep_enable else 'OFF', ', freq', port.get_beepfreq(), 'Hz')
    print('               Straight key:', 'ON' if stk.getaction() else 'OFF')
    print('                Paddle type:', pdl.gettype())
    print('                Iambic Type:', 'Mode B' if pdl.modeB else 'Mode A')
    print('              Record keying:', 'ON' if mem.recording else 'OFF')
    return True

# Console Command - SPEED
#
#     change speed unit
#
def speed(act=None):
    def unitword (unit):
        try:
            return {'CPM': 'character per minute',
                    'WPM': 'words per minute',
                    'QRS': 'dot duration in second'}[unit]
        except:
            return ''

    if act==None:
        print('Speed unit is ', utl.speed_unit, ' (',
              unitword(utl.speed_unit), ').', sep='')
        return True

    if act.upper() in ('CPM', 'WPM', 'QRS'):
        utl.speed_unit=act.upper()
    else:
        print('? unknown speed unit')
        return True

    print('Speed unit is set to ', utl.speed_unit, ' (',
          unitword(utl.speed_unit), ').', sep='')
    return True

# Console Command - LETTERGAP
#
#     change space length between letters
#    (also word gap changed)
#
def lettergap(gaprate=None):
    if gaprate==None:
        print('letter gap is', key.getlettergap(), 'times of dot length.')
        return True

    if not re.match(r"[0-9.]+$", gaprate) or float(gaprate)<=0:
        return True

    key.setlettergap(float(gaprate))
    print('letter gap is set to', key.getlettergap(), 'times of dot length.')

    return True

# Console Command - LOAD
#
#     load sequence of commands from a file
#
def load_file(filename=None):
    if filename==None:
        print('? no file name given')
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
#     display command long_help
#
def long_help(act=None):
    print('''PiCW.py command help:

a number:
            set speed of paddle and message keyer directly

some "<" or ">" characters:
            change speed by numbers of character
                "<" ... 0.5WPM slower
                ">" ... 0.5WPM faster

            example:  ">>>>>>" means 3.0WPM faster
                         "<<<" means 1.5WPM slower

text string beginning with a space:
            transmit the text string directly
            Note: You can send ...-. by the notation [VA] .
                  [eeetet] is also OK.

tx [OFF|ON]         :  disable/enable controlling line to transmitter

beep [OFF|ON|freq]  :  disable/enable or set freqency[Hz] of side tone

straight [OFF|ON]   :  disable/enable straight key action

paddle [OFF|IAMBIC|IAMBIC-REV|BUG|BUG-REV|SIDESWIPER]
                    :  disable paddle action
                       or enable the paddle by specified type
                       *-rev swaps dot/dash paddle.

iambic [A|B]        :  operation mode of imabic paddle

kb                  :  enter keyboard transmit mode
                       By pressing <ESC> or '$',
                       you can exit from this mode.

xmit <file_name> ...:  transmit contents of text file

recording [OFF|ON|STOP|START]
                    :  start/stop record of keying
                       OFF and STOP are the same,
                       ON and START, too.

play [speed]        :  replay keying with the speed

training [A|N|S|string] ...
                    :  start training mode
                       transmit randomly-generated 100 words
                       A)lpha, N)um and S)ymbol are type of characters.
                       string is characters to be trained.

show                :  display settting parameters

speed [WPM|CPM|QRS] :  set speed unit words or characters per a minute

lettergap [gapratio]:  set gap duration between letters
                       gapratio is a times of dot duration

load <file_name>    :  load console command from a file

help                :  display this help message

?                   :  display short help message

quit, exit, bye     :  exit from PiCW.py

Note:
    When computer transmits text message,
    you can break that by pressing Control-C
    or by pressing a straight key or any paddle lever.

    By pressing sraight key and dot paddle simultaneously,
    speed of paddle keying goes slow down.
    Straight key and dash paddle, speed up. '''),

    return True

# Console Command - HELP
#
#     display brief command help
#
def short_help(act=None):
    print('''=====[ PiCW.py commands ]======================================================
                                       |
number   : set speed                   |
"<", ">" : slower/faster               |
" "text  : transmit text directly      |
                                       |record [on|off|start: record keying
tx [off|on]         : TX control line  |       |stop]
beep [off|on|freq]  : side tone        |play [speed]        : replay keying
straight [off|on]   : straight key     |training <CHARTYPES>: training mode
paddle [off|iambic|iambic-rev|bug|     |show                : display settings
        bug-rev|sideswiper]            |speed [WPM|CPM|QRS] : toggle speed unit
                    : paddle action    |lettergap [gapratio]: letter gap length
iambic [a|b]        : iambic mode      |load <file_name>    : load config
kb                  : keyboard transmit|help                : display help
xmit <file_name> ...: file transmit    |?                   : display this
                                       |quit, exit, bye     : exit from PiCW.py
                                       |
==========================================[ Type 'help' for more details ]=====''')

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
#   key:   name of command
#   FN:  called function
#   ARG: parameter to be completed, ARG_FILE means file completion
#
FN  =1
ARG =2
ARG_FILE=3

cmds={'TX':        {FN: txline,     ARG: ['OFF', 'ON']},
      'BEEP':      {FN: beep,       ARG: ['OFF', 'ON']+[str(freq)
                                                        for freq
                                                        in port.get_avail_beepfreq()]},
      'STRAIGHT':  {FN: straight,   ARG: ['OFF', 'ON']},
      'PADDLE':    {FN: paddle,     ARG: sorted(pdl.typetab.keys())},
      'IAMBIC':    {FN: iambic,     ARG: ['A', 'B']},
      'KB':        {FN: kb_send,    ARG: None},
      'XMIT':      {FN: xmit_file,  ARG: ARG_FILE},
      'RECORD':    {FN: record,     ARG: ['OFF', 'ON', 'START', 'STOP']},
      'PLAY':      {FN: play,       ARG: None},
      'TRAINING':  {FN: training,   ARG: None},
      'SHOW':      {FN: show,       ARG: None},
      'SPEED':     {FN: speed,      ARG: ['CPM', 'WPM', 'QRS']},
      'LETTERGAP': {FN: lettergap,  ARG: None},
      'LOAD':      {FN: load_file,  ARG: ARG_FILE},
      'HELP':      {FN: long_help,  ARG: None},
      '?':         {FN: short_help, ARG: None},
      'BYE':       {FN: bye,        ARG: None},
      'EXIT':      {FN: bye,        ARG: None},
      'QUIT':      {FN: bye,        ARG: None}}

# create completion function
# for GNU readline
#
class rlComplete():

    # return candidates of filecompletion
    # from given path
    #
    def cand_path(self, path):
        # split path into dirname and basename
        #
        try:
            lastslash=[i for i in range(len(path)) if path[i]=='/'][-1]
            if lastslash==0:  # only slash at head
                dirpart='/'
                basepart=path[1:]
            else:
                dirpart=path[:lastslash]
                basepart=path[lastslash+1:]
        except IndexError:  # no slash in path
            dirpart='.'
            basepart=path

        candidates=[]  # return value

        # scan dirpart and pick up
        # candidates in it
        #
        if os.path.isdir(dirpart):
            for f in os.listdir(dirpart):
                if f.startswith(basepart):
                    cand=dirpart+'/'+f
                    if os.path.isdir(cand):
                        cand=cand+'/'
                    if cand.startswith('//'):
                        cand=cand[1:]
                    if cand.startswith('./'):
                        cand=cand[2:]
                    candidates.append(cand)
        return candidates

    # constructor
    #
    def __init__(self, cmds):
        self.cmds=cmds
        self.cmdnames=sorted(self.cmds.keys())
        self.enable()

    # get and return candidates
    #
    def getcand(self, text, state):
        if not self.enabled:
            return None

        try:
            if readline.get_line_buffer()[0] in ' <>':
                return None
        except:
            pass

        try:
            cmd=''
            cmd=readline.get_line_buffer().split()[0]
        except:
            pass

        if state==0:
            if 0<readline.get_begidx():
                # completing second word (parameter)
                try:
                    if isinstance(self.cmds[cmd.upper()][ARG], list):
                        # select from prepared argument list
                        if text=='':
                            self.matches=[value
                                          for value in self.cmds[cmd.upper()][ARG]]
                        else:
                            self.matches=[value
                                          for value in self.cmds[cmd.upper()][ARG]
                                          if value.startswith(text.upper())]
                    elif self.cmds[cmd.upper()][ARG]==ARG_FILE:
                        # get candidates of file path
                        self.matches=self.cand_path(text)
                    else:
                        self.matches=[]
                except:
                    self.matches=[]
            else:
                # completing first word (command)
                if text=='':
                    self.matches=[name+' '
                                  for name in self.cmdnames]
                else:
                    self.matches=[name+' '
                                  for name in self.cmdnames
                                  if name.startswith(text.upper())]

        try:
            retval=self.matches[state]
        except IndexError:
            retval=None

        return retval

    # disable completion temporarily
    #
    def disable(self):
        self.enabled=False

    # enable completion again
    #
    def enable(self):
        self.enabled=True

# setups for TAB completion
#
compl=rlComplete(cmds)
readline.set_completer(compl.getcand)
readline.set_completer_delims(re.sub(r'[-@%=+:,./]',  # these characters are
                                     '',              # OK for file names
                                     readline.get_completer_delims()))
readline.parse_and_bind('tab: complete')  # enable TAB for completion

# debug stuff
#
#import sys
# for debug rlComplete
#print(port.get_avail_beepfreq())
#print(sorted(pdl.typetab.keys()))
#sys.exit()
#
# for debug rlComplete
#   ... any error caused by rlComplete
#       is captured in readline
#
#compl.getcand('', 0)         # test for getcand() state transient
#print(compl.cand_path('t'))  # test for cand_path()
#sys.exit()

# command line parser
#
def parser(line):
    # set speed of Message Keyer and Iambic Keyer
    # in WPM, CPM or QRS
    #
    if re.match(r"[0-9.]+", line):
        try:
            key.setspeed(utl.speed2float(line))
        except:
            pass # in case of float() fails
        return True

    # change speed by +/- 0.5WPM
    #
    elif re.match(r"[<>]+$", line):
        key.setspeed(key.getspeed()+(0.5*(line.count('>')-line.count('<'))))
        return True

    # send text message using TextKeyer module
    #
    elif re.match(r" .+", line):
        key.reset_abort_request()
        txt.sendstr(line[1:])
        return True

    # call console commands
    #
    else:
        params=re.findall(r"[^\x00-\x20]+", line)
        if params:
            cmd=params.pop(0).upper()
            if cmd in cmds.keys():
                key.reset_abort_request()
                return cmds[cmd][FN](*params)
            else:
                print("? Eh")
                return True
        else:
            return True
