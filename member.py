import socket
import threading
import networking
import time
from time import gmtime, strftime
import sys, getopt
# Every node starts life as a normal member
LOGFILE = "log.txt"
LISTEN_PORT = 9797
SEEDS = "seeds.txt"
COORDINATOR_CHECK_INTERVAL = 5 # 5 seconds
Coordinator = ''

class handleMessage(threading.Thread):
    def __init__(self, (clientSocket, address), logfile):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.address = address
        self.logfile = logfile

    def run(self):
        MSGTYPE_LEN = 4
        msgType = networking.perfectReceive(MSGTYPE_LEN, self.clientSocket)
        # msgType is either JOIN, LEAV OR LOOK (Coordinator Lookup)
        # Following two characters denote length of nodename
        if msgType == 'JOIN' or msgType == 'LEAV':
            name_len = str(networking.perfectReceive(NAMELEN_HDR, self.clientSocket))  # NAMELEN_HDR is 2 characters. Example: 25
            nodeName = networking.perfectReceive(name_len, self.clientSocket)
            if msg == 'JOIN':
                addMember(nodeName)
                logEvent('JOIN', nodeName, self.logfile)
            else:
                removeMembers(nodeName)
                logEvent('JOIN', nodeName, self.logfile)
        elif msgType == 'LKUP':
            print "Received LKUP message"
            global Coordinator
            if Coordinator != '':
                networking.perfectSend('RPLY', self.clientSocket)
                networking.perfectSend(str(len(Coordinator)), self.clientSocket)
                networking.perfectSend(Coordinator, self.clientSocket)
            else:
                networking.perfectSend('NONE', self.clientSocket)


class listener(threading.Thread):
    def __init__(self, threadId, name, port, logFile):
            threading.Thread.__init__(self)
            self.threadId = threadId
            self.name = name
            self.port = port
            self.logFile = logFile

    def run(self):
            try:
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                serverSocket.bind(('', self.port))
                serverSocket.listen(5)
            except:
                print "ERROR: messageHandler thread not listening on socket\n"

            while 1:
                clientSocket, address = serverSocket.accept()
                print "INFO: Got new connection req from a member\n"
                servingThread = handleMessage((clientSocket, address), self.logFile)
                servingThread.start()


def coordinatorLookup():
    global Coordinator # Reference the global variable (Very Important)
    f = open(SEEDS, 'r')
    me = networking.getHostname()
    for x in range (1,2):
        for node in f:
            node = node.strip() # Remove leading and trailing whitespace
            if node != me:
                print "Checking if " + node + " knows the coordinator"
                conn = networking.getConnection(node, LISTEN_PORT)
                if conn != None:
                    conn.sendall('LKUP')
                    response = networking.perfectReceive(4, conn)
                    if response == 'RPLY':
                        nameLen = int(networking.perfectReceive(2, conn))
                        Coordinator = networking.perfectReceive(nameLen, conn)
                        networking.closeConnection(conn)
                    elif response == 'NONE':
                        networking.closeConnection(conn)
        
            # print "Coordinator :" + Coordinator
            if Coordinator != '':
                print "Found Coordinator"
                break
        
        if Coordinator == '':
            # Retry to query for  coordinator after some interval
            time.sleep(COORDINATOR_CHECK_INTERVAL)
    
    if Coordinator == '':
        Coordinator = me
        return me
    else:
        return Coordinator
        

def bootstrap(startAsCoordinator):
    "Members bootstrapping looking for an overlay and coordinator"
    global Coordinator
    # Start a thread listening for Coordinator Lookup messages
    messageHandler = listener(1, "Listener for JOIN, LEAV, LKUP", LISTEN_PORT, LOGFILE)
    messageHandler.start()
    if startAsCoordinator == False:
        coordinatorLookup() 
    else:
        Coordinator = networking.getHostname()

    print "Coordinator lookup returned " + Coordinator
    do_exit = False
    while do_exit == False:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print "Ctrl-C caught. Terminating gracefully..."
            do_exit = True

    # Stop running threads
    # messageHandler.stop()
    sys.exit(0)

def main(argv):
    startAsCoordinator = False

    try:
        opts, args = getopt.getopt(argv, "sm")
    except getopt.GetoptError:
        print 'member.py -s [-m]'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-s':
            startAsCoordinator = True
            print "INFO: Starting as a COORDINATOR"
        elif opt == '-m':
            print "INFO: Starting as a normal MEMBER"
   
    bootstrap(startAsCoordinator)

if __name__ == "__main__":
    main(sys.argv[1:])
 
