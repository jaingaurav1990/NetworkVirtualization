import socket
def getConnection(node, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node, port))
    return s

conn = None
try:
    conn = getConnection("planetlab1.inf.ethz.ch", 6444)
except socket.timeout:
    print msg

    
