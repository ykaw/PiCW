# MemoryKeyer - Record/Replay real time keying

import time
import KeyingControl as key

recording=False
tstamp=[]    # sequence of time stamp
keystat=[]   # sequence of key operation

# start recording
#
def recstart():
    global recording, tstamp, keystat
    
    if not recording:
        recording=True
        tstamp=[]
        keystat=[]

# stop recording
#
def recstop():
    global recording, tstamp, keystat

    if recording:
        tstamp.append(time.time())
        keystat.append(key.RELEASED)

        # sentinels
        #
        tstamp.append(time.time()+0.1)
        keystat.append(key.RELEASED)
        recording=False

# replay recording
#
def replay():
    if not recording and tstamp:
        try:
            for i in range(len(tstamp)-1):
                if keystat[i]==key.PRESSED:
                    key.mark()
                elif keystat[i]==key.RELEASED:
                    key.space()
                time.sleep(tstamp[i+1]-tstamp[i])
        except KeyboardInterrupt:
            key.space()
