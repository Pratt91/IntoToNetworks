"""
A simple link simulator that emulates the transmission of packets from a
senders A & B, through switch C, to receiver D
"""
from collections import deque
import csv

received_packets = []
received_packets_at_c = []
received_packets_at_d = []

class Packet:
    """
    This stores the information associated with a packet
    """
    def __init__(self, num_bits, seq_num, data):
        self.num_bits = num_bits
        self.seq_num = seq_num
        self.data = data
        self.enqueue_time = None
        self.start_transmit_time = None
        self.end_transmit_time = None
        self.receive_time = None

    def __str__(self):
        return str(self.seq_num)


class Node:
    """
    This manages the state of a node and handle the events
    """
    IDLE = 0
    BUSY = 1

    def __init__(self, name):
        self.name = name
        self.incoming_link = None
        self.outgoing_link = None
        self.input_queue = deque()
        self.output_queue = deque()
        self.state = Node.IDLE
        self.seq = 0

    def enqueue(self, sim, owner, data):
        """
        Handles the enqueueing of a packet
        If the queue is empty, then we can start transmitting ASAP
        Else, put the packet in the queue for later
        :param sim:
        :param owner:
        :param data:
        :return:
        """
        p = Packet(1000, self.seq, data)
        p.enqueue_time = sim.now
        self.seq += 1
        if self.state == Node.IDLE:
            sim.schedule_event(self.next_tx, self, p, 0, 'start-tx[%d] %s' % (p.seq_num, self.name))
            self.output_queue.append(p)
            self.state = Node.BUSY
        elif self.state == Node.BUSY:
            self.output_queue.append(p)
        else:
            raise Exception('unknown state')

    def next_tx(self, sim, owner, data):
        """
        Called to transmit the packet that is at the HOQ if such a packet exists
        A start propagation event will be called

        :return:
        """
        
        if len(self.output_queue) > 0:
            self.state = Node.BUSY
            p = self.output_queue.popleft()
            p.start_transmit_time = sim.now
            tx_delay = self.outgoing_link.compute_transmit_delay(p)
            sim.schedule_event(self.outgoing_link.start_propagation,
                               self.outgoing_link, p, tx_delay,
                               'start-prop[%d] %s' % (p.seq_num, self.name)) #Display name
        else:
            self.state = Node.IDLE


    def receive(self, sim, owner, data):
        data.receive_time = sim.now

        #Track data as it routes through C
        if owner.name == 'c':
            received_packets_at_c.append(data)

        #Record data delivered to D
        if owner.name == 'd':
            received_packets_at_d.append(data)
        
        received_packets.append(data)

    def __str__(self):
        return '%s' % self.name


class Link:
    def __init__(self, src, dst, bandwidth, distance):
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth
        self.distance = distance

    def compute_transmit_delay(self, pkt):
        """
        Computes the transmission delay

        :param pkt:
        :return:
        """
        d = pkt.num_bits / self.bandwidth
        return d

    def compute_propagation_delay(self):
        """
        Computes the propagation delay

        :return:
        """
        d = self.distance / 2e8
        return d

    def start_propagation(self, sim, owner, data):
        """
        Called after the packet is transmitted, now we just need for it to propagate
        :param sim:
        :param owner:
        :param data:
        :return:
        """
        propagation_delay = self.compute_propagation_delay()
        data.end_transmit_time = sim.now

        sim.schedule_event(self.dst.receive, self.dst,
                           data, propagation_delay,
                           'receive[%d] %s' % (data.seq_num, self.dst)) ##########

        sim.schedule_event(self.src.next_tx, self.src, data, 0, 'next-tx %s' % self.src) #changed None to data


class Event:
    """
    This class holds all the information associated with the event
    -- fh      -- is the function handler that will be invoked when the event fires

    -- owner   -- is not used in the code, but is intended as a pointer to the object on which fh was called
                  For example, calling a.enqueue would have the fh = a.enqueue and the owner = a

    -- data    -- the information associated with the event

    -- time    -- the absolute time when the event should be executed

    -- tag     -- a user-readable description of the event

    -- seq_num -- the sequence number of the event
    """
    seq_num = 0

    def __init__(self, fh, owner, data, time, tag):
        self.fh = fh
        self.owner = owner
        self.data = data
        self.time = time
        self.tag = tag
        self.seq_num = Event.seq_num
        Event.seq_num += 1

    def __str__(self):
        return 'id=%d @%.1f %s' % (self.seq_num, self.time, self.tag)


class Simulator:
    """
    Simulator maintains a queue of events that are sorted by time (and seq_num)
    The event at the HOQ will be executed by calling the function handler that is associated with it.
    New events may be added using the schedule_event function.

    The simulator also help connect together the nodes via links.
    """
    def __init__(self):
        self.queue = []
        self.links = []
        self.now = 0

    def connect(self, src, dst, bandwidth, distance):
        link = Link(src, dst, bandwidth, distance)
        src.outgoing_link = link
        dst.incoming_link = link
        self.links.append(link)

        print('connected node %s to node %s' % (src, dst)) # validate connection

    def schedule_event(self, fh, owner, data, delay, tag):
        event = Event(fh, owner, data, self.now + delay, tag)
        self.queue.append(event)

    def run(self, duration):
        print('%10s %8s %16s %16s' % ('\n\nnow', 'seq_num', 'data', 'tag'))
        while self.now < duration:
            self.queue.sort(key=lambda e: (e.time, e.seq_num))

            if len(self.queue) == 0: break
            hoq = self.queue.pop(0)
            self.now = hoq.time
            print('%10.1f %8d %16s %16s' % (self.now, hoq.seq_num, str(hoq.data), hoq.tag))
            hoq.fh(self, hoq.owner, hoq.data)


if __name__ == "__main__":
    """
    Setup a simple topology a --> b
    """
    node_a = Node('a')
    node_b = Node('b')
    node_c = Node('c')  # node to represent our switch
    node_d = Node('d')  # final destination node


 


    sim = Simulator()
    sim.connect(node_a, node_c, 100, 2e8)     # connect node A to Switch
    sim.connect(node_b, node_c, 100, 2e8)     # connect node B to switch
    sim.connect(node_c, node_d, 100, 2e8)     # connect switch to D

    packets = [] #make iterable source of packets
    seq_num = 0


    
    # packets f
    for time in range(0, 10000, 1000):
        for seq in range(10):
            pkt = Packet(1000, seq_num, 'a')
            packets.append(pkt)
            sim.schedule_event(node_a.enqueue, node_a, pkt, time, 'queue a')
            seq_num += 1
            seq += 1
            

    # packets from node b
    for time in range(0, 10000, 500):
        for seq in range(2):
            pkt = Packet(1000, seq_num, 'b')
            packets.append(pkt)
            sim.schedule_event(node_b.enqueue, node_b, pkt, time, 'queue b')
            seq_num += 1
            seq += 1

    for time in range(10000):
        sim.schedule_event(node_c.enqueue, node_c, pkt, time, 'queue c')
    
    sim.run(1000)

##############################################################
  
    print("seq num")
    for info in received_packets_at_d:
        print(info.seq_num)
    print("\npackets received")
    for info in received_packets:
        print(info.data)
    print("\npacket src")
    for info in packets:
        print(info.data)
    print("\ntime packets received at c")
    for info in received_packets_at_c:
        print(info.receive_time)
    print("\ntime packets transmitted from c")
    for info in received_packets_at_c:
        print(info.start_transmit_time - info.enqueue_time)           
    print("\ntime packets received at d")
    for info in received_packets_at_d:
        print(info.receive_time)
###############################################################

    print('\n\nSimulation Results:')
    print('enqueue time, tx time, receive time, end-to-end delay, queue delay')
    for packet in received_packets:
        queue_delay = packet.start_transmit_time - packet.enqueue_time
        e2e_delay = packet.receive_time - packet.enqueue_time
        print('receive', packet.enqueue_time, packet.end_transmit_time, packet.receive_time, e2e_delay, queue_delay)

 
    #c = csv.writer(open("networkshw1.csv", "w"))
    #c.writerow(["Seq num","Source","Queue @src","Receive @C","Transmit @C","Receive @D"])
    
