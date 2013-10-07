import socket
import threading

MSGTYPE_LEN = 4

def getConnection(node, port):
    s = socket.socket()
    s.connect((node, port))
    return s

def closeConnection(s):
    s.close()

def perfectSend(msg, connection):
        totalSent = 0
        while totalSent < len(msg):
                sent = connection.send(msg[totalSent:])
                if sent == 0:
                        raise RuntimeError("Socket connection broken at other end")
                else:
                        totalSent = totalSent + sent

def perfectReceive(msgLen, connection):
    msg = ''    
    while len(msg) < msgLen:
            chunk = connection.recv(msgLen - len(msg))
            if len(chunk) == 0:
                    raise RuntimeError("Socket connection broken at other end")
            else:
                    msg = msg + chunk
    return msg

class handleMessage(threading.Thread):
    def __init__(self, (clientSocket, address), logfile):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.address = address
        self.logfile = logfile

    def run(self):
        msg = perfectReceive(MSGTYPE_LEN, self.clientSocket)
        # msgType is either JOIN, LEAV OR LOOK (Coordinator Lookup)
        # Following two characters denote length of nodename
        if msg == 'JOIN' or msgType == 'LEAV':
            name_len = str(perfectReceive(NAMELEN_HDR, self.clientSocket))  # NAMELEN_HDR is 2 characters. Example: 25
            nodeName = perfectReceive(name_len, self.clientSocket)
            if msg == 'JOIN':
                addMember(nodeName)
                logEvent('JOIN', nodeName, self.logfile)
            else:
                removeMembers(nodeName)
                logEvent('JOIN', nodeName, self.logfile)
        elif msg == 'LKUP':
            if COORDINATOR != '':
                perfectSend('RPLY', self.clientSocket)
                perfectSend(COORDINATOR, self.clientSocket)
            else:
                perfectSend('NONE', self.clientSocket)


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


