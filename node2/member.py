from networking import listener
import networking
from time import gmtime, strftime
import socket

# Every node starts life as a normal member
COORDINATOR = ''
STARTASCOORDINATOR = False
LOGFILE = "log.txt"
SEEDS = "seeds.txt"
COORDINATOR_CHECK_INTERVAL = 10
LISTEN_PORT = 9797

def coordinatorLookup():
    f = open(SEEDS, 'r')
    me = socket.gethostname()
    for x in range (1,2):
        for node in f:
            if node != me:
                print "Checking out with " + node
                conn = networking.getConnection(node, LISTEN_PORT)
                sendall('LKUP', conn)
                response = perfectReceive(4, conn)
                if response == 'RPLY':
                    nameLen = perfectReceive(NAMELEN, conn)
                    COORDINATOR = perfectReceive(nameLen, conn)
                    networking.closeConnection(conn)
                elif response == 'NONE':
                    networking.closeConnection(conn)
        
        if COORDINATOR != '':
            break
        
        time.sleep(COORDINATOR_CHECK_INTERVAL)
    
    if COORDINATOR == '':
        COORDINATOR = me
        return me
    else:
        return COORDINATOR
        

def bootstrap():
    "Members bootstrapping looking for an overlay and coordinator"
    # Start a thread listening for Coordinator Lookup messages
    messageHandler = listener(1, "Listener for JOIN, LEAV, LKUP", 9798, LOGFILE)
    if STARTASCOORDINATOR == False:
        coordinatorLookup() 
    else:
        COORDINATOR = socket.gethostname()

    print "Coordinator lookup returned " + COORDINATOR

bootstrap()
        

