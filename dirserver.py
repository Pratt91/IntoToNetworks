#SERVER
import socket
import select
import sys
import queue
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
address = (host, port)

print('Chat clients can connect to host ',socket.gethostbyname(host),':',port)
#Create TCP socket
try:
    #AF_INET, STREAM socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(address)
    server.listen(2) #listen for two chat clients
    print("TCP socket opened on port: ", port)
except socket.error as e:
    print("ERR: Client socket not created " + str(e))
    server.close()

###Three arguments for select: read, write, err######
read = [server]     #need to read from clients
write = []          #as clients connect we will want to write to them
message_queues = {} #need to store messages if client buffer is full


while read:
    print('Waiting for event', file = sys.stderr)
    readable, writable, exceptional = select.select(read, write, read)
    #handle readable argument
    for s in readable:
        #case where client is connecting
        if s is server:
            conn, client_addr = s.accept()
            print('Incomming connection from ', client_addr, file = sys.stderr)
            conn.setblocking(0)
            read.append(conn) #add readable client to input list
            message_queues[conn] = queue.Queue()
        #Case where client is sending a message
        else:
            data = s.recv(1024) #buffer
            if data:
                print('Received ', data, ' from ', s.getpeername(), file = sys.stderr)
                message_queues[s].put(data)
                #add client into chat connection
                #send data to other client
                if s not in write:
                    write.append(s)
                for each in write:
                    s.send(message)
            else:
                print('closing ', client_addr, file = sys.stderr)
                #stop listening for input on the connection
                if s in write:  #changed outputs to write
                    write.remove(s) #changed outputs to write
                read.remove(s) #changed inputs to read
                s.close()
                #clean out message queue
                del message_queues[s]
    #Handle writable argument
    for s in writable:
        #If there is a message in the queue get it and send it
        #If there is no message the queue is empty
        try:
            message = message_queues[s].get_nowait()
            s.send(message)
        except queue.Empty:
            print('  ',s.getpeername(), 'queue empty', file = sys.stderr)
            write.remove(s)
        else:
            #for each in read:
            print('sending ', message, 'to ', s.getpeername(), file = sys.stderr)
            #s.send(message)
    #Finally hand exception argument
    for s in exceptional:
        print('connection err')
        read.remove(s)
        if s in write:
            write.remove(s)
        s.close()
        del message_queues[s]



















    
