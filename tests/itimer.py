import signal, time, random

itimer_hz = 100

# define and set the signal handler
def handler(signum, frame):
    global counter
    counter = counter + 1
    # signal.setitimer(signal.ITIMER_REAL, 1.0/itimer_hz)
signal.signal(signal.SIGALRM, handler)

# initialize counter and timer
counter = 0
prev_cnt = 0
signal.setitimer(signal.ITIMER_REAL, 1.0/itimer_hz, 1.0/itimer_hz)

# main loop
print("Starting program...")
while True:
    time.sleep(10)
    print("wake up: ", counter-prev_cnt)
    prev_cnt=counter

# clean-ups
signal.setitimer(signal.ITIMER_REAL, 0)
