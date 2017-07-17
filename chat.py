#CLIENT
import socket
import sys
import select
import argparse
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


 
#server address
host = 'localhost'
port = 54321


seqnum = 0
UID = str(input('Enter User Name '))
IP_Port = str(port)
DID = str(socket.gethostbyname(host))
dirService_IP_Port = None
####Open TCP connection####
try:
    #AF_INET, STREAM socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("TCP socket opened at client")
except socket.error as e:
    print("ERR: Client socket not created " + str(e))


print('Client HOST: ' + socket.gethostbyname(host))

#connect client to port
try:
    s.connect((host, port))
    print('Client is connected to port: ' + str(port))
    connected = True
except socket.error as e:
    print("ERR: cannot connect to socket " + str(e))
    connected = False

while connected is True:
    message = input("Your message: ")
    #encodedMSG = message.encode('utf-8')
    encodedMSG = encode_message(seqnum, UID, DID, message)
    s.send(encodedMSG)
    print("Waiting for reply")
    reply = s.recv(1024)
    #response = reply.decode('utf-8')
    response = decode_message(reply)
    print("Received ", repr(response))



 
