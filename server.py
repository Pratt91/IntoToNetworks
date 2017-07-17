#SERVER
import socket
import select
import sys
import Queue
import struct

   
    
##### Encode and Decode provided by Dr. Chipvara ######
def encode_message(seqnum, UID, DID, msg, version=150):
    header_buf = bytearray(36)
    UID = UID + ' ' * (16 - len(UID))
    DID = DID + ' '* (16 - len(DID))

    header_buf = struct.pack('!HH16s16s', version, seqnum, UID.encode('utf-8'), DID.encode('utf-8'))
    header_buf = header_buf + msg.encode('utf-8')

    return header_buf


def decode_message(msg_buf):
    tuple = struct.unpack('!HH16s16s', msg_buf[:36])
    (version, seqnum, UID, DID) = tuple
    UID = UID.decode('utf-8')
    DID = DID.decode('utf-8')
    msg = msg_buf[36:].decode('utf-8')
    return (seqnum, UID, DID, msg)


#msg = encode_message(3, 'abc', 'cdef', 'hello')
#msg1 = decode_message(msg)[-1]
#print(msg)
###########################################################



#### First open up a TCP connection to the server (server.py)
try:
    #AF_INET, STREAM socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("TCP socket opened at server")
except socket.error as e:
    print("ERR: Server socket not created " + str(e))
    
#Server address
host = 'localhost'
port = 54321
IP = socket.gethostbyname(host)
print('Server HOST: ' + socket.gethostbyname(host))
print('Server PORT: ' + str(port))
print('Server IP: ' + str(IP))


#bind to server address
try:
    s.bind((host, port))   #used to take connections at port
    print("socket binded")
    
    s.listen(5) #accepted number of connections
    print("listening on port: " + str(port))
    conn, addr = s.accept() ## accept the connection
    print("Waiting for connection...")
    print("Connected to: " , addr)

    while True:
        data = conn.recv(1024)      #accept 1024 bytes from conn
        decodeData = data.decode('utf-8')
        print("MSG: ", repr(data))    #store message at data
        reply = input("Reply: ")  #prompt reply
        response = reply.encode('utf-8')
        conn.sendall(response)           #send reply

except socket.error as e:
    print("ERR: cannot bind socket "+str(e))








'''
#wait for connection

s.listen(5) #accepted number of connections
print("listening on port: " + str(port))
conn, addr = s.accept() ## accept the connection
print("Connected to: " , addr)

while True:
    print("Waiting for connection...")
    data = conn.recv(1024)      #accept 1024 bytes from conn
    decodeData = data.decode('utf-8')
    print("MSG: ", repr(data))    #store message at data
    reply = input("Reply: ")  #prompt reply
    response = reply.encode('utf-8')
    conn.sendall(response)           #send reply

conn.close()
    '''


