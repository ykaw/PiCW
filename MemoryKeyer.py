# MemoryKeyer - Record/Replay real time keying

import time
import sys
import KeyingControl as key
import CwUtilities   as utl

recording=False
tstamp=[]    # sequence of time stamp
keystat=[]   # sequence of key operation

# start recording
#
def recstart():
    global recording, tstamp, keystat
    
    if recording:
        print('? Already recording...')
        return False

    print('Start recording ...')
    recording=True
    tstamp=[]
    keystat=[]
    return True

# stop recording
#
def recstop():
    global recording, tstamp, keystat

    if not recording:
        print('? Not recording, yet.')
        return False

    recording=False
    tstamp.append(tstamp[-1]+1)
    keystat.append(key.RELEASED)
    print('Stop recording.')
    return True

# replay recording
#
def replay(speed):
    if recording:
        print("? Now recording, can't replay")
        return False

    if not (0.0<speed and speed<=10):
        print('? Replay speed is too fast or too slow.')
        return False

    if not recording and tstamp:

        print('Replay keying:', len(tstamp), 'marks and spaces...')

        # setups for progress bar
        #
        barlen=72
        bar=utl.ProgressBar(barlen, int(len(tstamp)))
        print('|', '-' * barlen, '|', sep='')
        print('|', end=''); sys.stdout.flush()

        # frequency of bar update
        #
        barstep=int(len(tstamp)/barlen)

        barcount=0
        try:
            for i in range(len(tstamp)-1):
                if keystat[i]==key.PRESSED:
                    key.mark()
                elif keystat[i]==key.RELEASED:
                    key.space()

                #simple progress bar
                barcount += 1
                if barstep<barcount:
                    print('*' * bar.diff(i), end='') # update progressbar
                    sys.stdout.flush()
                    barcount=0
                time.sleep((tstamp[i+1]-tstamp[i])/speed)
            print('*' * bar.diff(int(len(tstamp))), '|', sep='')

        except KeyboardInterrupt:
            print()
            key.space()

        return True
