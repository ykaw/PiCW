# MemoryKeyer - Record/Replay real time keying

import time
import KeyingControl as key
import CwUtilities   as utl

recording=False
tstamp   =[]   # sequence of time stamp
keystat  =[]   # sequence of key operation
maxdelay =600  # Too long mark/space (sec) is truncated.
               #(disabled if maxdelay is non-positive)

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
    tstamp.append(tstamp[-1]+0.1)
    keystat.append(key.RELEASED)
    print('Stop recording.')
    return True

# replay recording
#
def replay(speed, barlen=0):
    if recording:
        print("? Now recording, can't replay")
        return False

    if not (0.0<speed and speed<=10):
        print('? Replay speed is too fast or too slow.')
        return False

    if not tstamp:
        return False

    print('Replay keying:', len(tstamp), 'marks and spaces...')

    # setups for progress bar
    #
    if 1<=barlen:
        progbar=utl.ProgressBar(barlen, int(len(tstamp)))
        progbar.begin()

        barstep=int(len(tstamp)/barlen)  # frequency of bar update
        barcount=0

    try:
        # replay loop
        #
        for i in range(len(tstamp)-1):
            if key.abort_requested():
                key.space()
                progbar.end(False)
                return False
            elif keystat[i]==key.PRESSED:
                key.mark()
            elif keystat[i]==key.RELEASED:
                key.space()

            if 1<=barlen:
                barcount += 1
                if barstep<barcount:
                    progbar.update(i)
                    barcount=0

            if 0<=maxdelay:
                time.sleep(min(maxdelay, (tstamp[i+1]-tstamp[i])/speed))
            else:
                time.sleep((tstamp[i+1]-tstamp[i])/speed)

        if 1<=barlen:
            # complete progressbar
            progbar.end(True)

    except KeyboardInterrupt:
        if 1<=barlen:
            print()
        key.space()

    return True
