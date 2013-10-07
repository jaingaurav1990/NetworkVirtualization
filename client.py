import socket

SERVER_PORT = 5656
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER = socket.gethostname()
s.connect((SERVER, SERVER_PORT))
msg = "Hello, server"
msglen = len(msg)
totalSent = 0

while totalSent < msglen:
	sent = s.send(msg[totalSent:])
	if sent == 0:
		raise RuntimeError("Socket connection broken at server end")
	else:
		totalSent += sent

totalReceived = 0
recvdMessage = ''
while len(recvdMessage) < msglen:
	chunk = s.recv(msglen - len(recvdMessage))
	if len(chunk) == 0:
			raise RuntimeError("Socket connection broken at server end")
	else:
		recvdMessage += chunk

print "MESSAGE RECEIVED: " + recvdMessage


