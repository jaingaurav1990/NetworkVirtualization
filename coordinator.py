import os
import time
import socket
import threading
import subprocess

MEMBERS_FILE = "members.txt"
SERVER_PORT = 5656
MEMBER_PORT = 6767
PORT = 5656
PROBE_INTERVAL = 10
TYPE_LEN = 4
coordinator = True
NAMELEN_HDR = 2

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

def sendfile(filename, node, port):
	"Send file filename to node"
	f = open(filename, 'r')
	conn = socket.socket((node, port)) 

	# Send header indicating file transfer
	perfectSend("FILETRANSFER", conn)
	# Send actual file contents
	while 1:
			chunk = f.read(65536) # Read maximum 65536 bytes at a time
			if len(chunk) == 0:
					break  		  # EOF 
			else:
					perfectSend(msg, conn)	


def listMembers():
	"List all members in the overlay network as known to the coordinator"
	members = []
	f = open(MEMBERS_FILE, 'r')
	for line in f:
			members.append(line)
	f.close()
	return members


def addMember(nodeId):
	"Add nodeId to the list of active members in the overlay"
	# Update the list of active members
	f = open(MEMBERS_FILE, 'a')
	f.write(nodeId + '\n')
	f.close()
	# Maintain a global data structure of all members ??

	# Send updated list to all active members
	members = listMembers()	
	for node in members:
		sendfile(MEMBERS_FILE, node, PORT)


def removeMembers(nodeIdList):
	"Remove nodeId from the list of active members in the overlay"
	# Update the list of active members
	members = listMembers()
	
	f = open(MEMBERS_FILE, 'w')
	for node in members:
			if node not in nodeIdList:
					f.write(node)
	f.close()
	# Send updated list to all active members
	members = listMembers()
	for node in members:
			sendfile(MEMBERS_FILE, node, PORT)

def ping(nodeId):
    "Check whether nodeId is alive (as seen by this host)"
    response = subprocess.call("ping -c 1 %s" % nodeId, shell = True, stdout = open('/dev/null', 'w'), stderr = subprocess.STDOUT)
    print "Returning response from ping"
    return response		# 0 indicates connected. Disconnected otherwise
			

def checkConnectivityToAll():
	"Check if active members listed in members.txt file are still connected"
	members = listMembers()
	disconnectedMembers = []
	for node in members:
            print "INFO: Pinging " + node
            res = ping(node)
            if res != 0: # Probe lost
				disconnected = True
				# Try 3 more probes at max
				for x in range (1, 3):
						response = ping(node)
						if response == 0:
								disconnected = False
								break
						
				if disconnected == True:
					disconnectedMembers.append(node)

	return disconnectedMembers

class serveRequest(threading.Thread):
    def __init__(self, (clientSocket, address)):
		threading.Thread.__init__(self)
		self.clientSocket = clientSocket
		self.address = address

    def run(self):
        msg = perfectReceive(TYPE_LEN, self.clientSocket)
		# msgType is either JOIN OR LEAV
		# Following two characters denote length of nodename
        if msg == 'JOIN' or msgType == 'LEAV':
            name_len = str(perfectReceive(NAMELEN_HDR, self.clientSocket))  # NAMELEN_HDR is 2 characters. Example: 25
            nodeName = perfectReceive(name_len, self.clientSocket)
            if msg == 'JOIN':
				addMember(nodeName)
            else:
                removeMembers(nodeName)
			


class checkConnectivity(threading.Thread):
		def __init__(self, threadId, name, coordinator):
				threading.Thread.__init__(self)
				self.threadId = threadId
				self.name = name
				self.coordinator = coordinator # Boolean value indicating whether this thread is coordinator or not

		def run(self):
				while 1:
					if coordinator == False:
							break
					else:
						disconnMembers = checkConnectivityToAll()
						if disconnMembers:
							removeMembers(disconnMembers)

					time.sleep(PROBE_INTERVAL)

class listeningServer(threading.Thread):
    def __init__(self, threadId, name, coordinator, port):
			threading.Thread.__init__(self)
			self.threadId = threadId
			self.name = name
			self.coordinator = coordinator
			self.port = port

    def run(self):
            try:
		    	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		    	serverSocket.bind(('', SERVER_PORT))
		    	serverSocket.listen(5)
            except:
                print "ERROR: Coordinator Server thread not listening on socket\n"

            while 1:
                (clientSocket, address) = serverSocket.accept()
                print "INFO: Got new connection req from a member\n"
                servingThread = serveRequest((clientSocket, addr))
                servingThread.start()

def main():
    "Main thread executes this function"
    server = listeningServer(1, 'Server', True, SERVER_PORT)
    checkConnect = checkConnectivity(2, 'Check Connection', True)
    server.start()
    checkConnect.start()
    print "Main thread will remain alive...As good as dead though"

# Run main
main()
