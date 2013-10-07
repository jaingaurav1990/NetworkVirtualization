from networking import listener
from time import gmtime, strftime

# Every node starts life as a normal member
COORDINATOR = ''
STARTASCOORDINATOR = True
LOGFILE = "log.txt"
LISTEN_PORT = 9797
SEEDS = "seeds.txt"
COORDINATOR_CHECK_INTERVAL = 10

def coordinatorLookup():
    f = open(SEEDS, 'r')
    me = socket.gethostname()
    for x in range (1,2):
        for node in f:
            if node != me:
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
    messageHandler = listener(1, "Listener for JOIN, LEAV, LKUP", LISTEN_PORT, LOGFILE)
    messageHandler.start()
    if STARTASCOORDINATOR == False:
        coordinatorLookup() 
    else:
        #COORDINATOR = socket.gethostname()
        COORDINATOR = "planetlab1.node"

    print "Coordinator lookup returned " + COORDINATOR

bootstrap()
        

