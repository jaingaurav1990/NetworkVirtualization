import sys
import time
import threading
import socket
import signal
doCleanup = False

class exThread(threading.Thread):
    def __init__(self, threadId):
        threading.Thread.__init__(self)
        self.threadId = threadId

    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('', 3333))
        finally:
            s.recvfrom(4)
            s.close()
            print "Thread's finally clause being executed" 
            sys.exit() # Same as thread.exit()

cond = True
def func():
    pass

try:
    th = exThread(1)
    th.daemon = True
    th.start()
    while True:
        time.sleep(9000)
        if cond:
            func()
except KeyboardInterrupt:
    print "Ctrl-C caught by main thread"
    sys.exit(0)
finally:
    print "Executing the finally clause from main thread"
