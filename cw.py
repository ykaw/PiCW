import signal, time, random

# define and set the signal handler
def handler(signum, frame):
    global counter
    counter = counter + 1
    signal.setitimer(signal.ITIMER_REAL, 0.01)
signal.signal(signal.SIGALRM, handler)

# initialize counter and timer
counter = 0
signal.setitimer(signal.ITIMER_REAL, 0.01)

# main loop
print("Starting program...")
while True:
    time.sleep(10)
    print("wake up: ", counter)

# clean-ups
signal.setitimer(signal.ITIMER_REAL, 0)
