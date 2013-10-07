import socket
import threading
import logging
import subprocess
import os

MSGTYPE_LEN = 4
PING_PORT = 37896
PONG_PORT = 45240
PING_TIMEOUT = 10
PONG_TIMEOUT = 10

def getHostname():
    return socket.gethostname()

# Enclose every single call to getConnection() in
# a try: except: block
def getConnection(node, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node, port))
    return s

def closeConnection(s):
    s.close()

def perfectSend(msg, connection):
        totalSent = 0
        while totalSent < len(msg):
            try:
                sent = connection.send(msg[totalSent:])
                if sent == 0:
                    logging.warning("perfectSend(): send() returned 0. Socket connection broken at other end")
                    closeConnection(connection)
                else:
                        totalSent = totalSent + sent
            except socket.error:
                logging.warning(msg)

def perfectReceive(msgLen, connection):
    msg = ''    
    while len(msg) < msgLen:
        numBytes = msgLen - len(msg)
        chunk = connection.recv(numBytes)
        if len(chunk) == 0:
            raise socket.error
        msg = msg + chunk
    return msg

def sysPing(nodeId):
    "Check whether nodeId is alive (as seen by this host)"
    response = os.system("ping -c 1 " + nodeId)
    return response     # 0 indicates connected. Disconnected otherwise

def ping(node, retry):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(PING_TIMEOUT)
    s.bind(('', PING_PORT))
    try:
        s.sendto('PING', (node, PONG_PORT))
        data, address = s.recvfrom(4)
        if data != 'PONG':
            logging.warning(data + " received instead of a PONG. Not right!")
        s.close()
        return 0
    except socket.timeout:
        s.close()
        if retry != 0:
            return ping(node, retry - 1)
        else:
            return 1
    except socket.error, msg:
        logging.warning(msg)
        s.close()
        return 2

def pong(retry):
    """Sends a reply to PING"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', PONG_PORT))
    s.settimeout(PONG_TIMEOUT)
    try:
        data, address = s.recvfrom(4)
        if data != 'PING':
            logging.warning(data + " received instead of a PING. Not right!")

        s.sendto('PONG', address) 
        s.close()
    except socket.timeout:
        s.close()
        if retry != 0:
            pong(retry - 1)
        else:
            logging.info("pong() detected Coordinator Failure (Timeout)")
            raise # Let application take action
    except socket.error, msg:
        logging.warning(msg)
        s.close()
        raise

