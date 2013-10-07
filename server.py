import socket

PORT = 5656

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
serverSocket.bind((host, PORT))
serverSocket.listen(5)
print "Server is listening"

def receive(clientSocket, msglen):
	totalReceived = 0
	msg = ''
	while totalReceived < msglen:
		chunk = clientSocket.recv(msglen - totalReceived)
		if len(chunk) == 0:
				raise RuntimeError("Connection broken at client end")
		else:
			msg = msg + chunk
			totalReceived = totalReceived + len(chunk)
	
	return msg


while 1:
	(clientSocket, address) = serverSocket.accept()
	print "Got connection request from a client"
	
	msglen = len("Hello, server")
	message = receive(clientSocket, msglen)
	print "MESSAGE FROM CLIENT: " + message
	clientSocket.send("Hello, client")
	clientSocket.close()


