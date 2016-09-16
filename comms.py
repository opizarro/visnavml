# 2012/12/26 SS - created

from threading import Thread
from threading import Event
import socket
from Queue import Queue
import sys


class UdpThread(Thread):
    def __init__(self, listening_address, forward_address, myName, udpQueue, ctrlQueue, evtType):
        Thread.__init__(self)
        self.udpQueue = udpQueue
        self.ctrlQueue = ctrlQueue
        self.bind = listening_address
        self.target_add = forward_address
        self.evtType = evtType
        self.name = myName
        self.e = Event()    # This is an event to signal start/stop to the RX thread
        # Open a socket to destination
        if forward_address != None:
            self.target = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if (self.target_add[0] == '<broadcast>'):
                self.target.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        else:
            self.target = None
        # Start the Udp receiving
        self.rx = UdpThreadRx(self.bind, self.udpQueue, self.e, self.evtType)
        self.rx.name = ''.join([self.name,'Rx'])
        self.rx.daemon = True
        self.rx.start()

    def run(self):
        print "Starting, my name is: " + self.name
    	while True:
            #print "Udp queue size is: " + str(self.udpQueue.qsize())
            message=self.udpQueue.get()
#            print message
            if message is None:
                break
            if (message[0] == 'RXD'):
 #               print "Udp thread received: " + message[2]
                self.ctrlQueue.put(('RXD',self.name,message[2])) # send the message received to the control thread
            if (message[0] == 'WAS'):
                if self.target != None:
                    try:
                        self.target.sendto(message[2], self.target_add)
                        print "Sending udp message: " + message[2]
                    except:
                        print "Error sending UDP message"
            # PAUSE = pause receiving thread
            if (message[0] == 'PAUSE'):
                self.e.set()
            # RESUME = resume receiving thread
            if (message[0] == 'RESUME'):
                self.e.clear()
            self.udpQueue.task_done()


class UdpThreadRx(Thread):
    BUFFER_SIZE = 4096
    def __init__(self, listening_address, udpQueue, event, evtType):
        Thread.__init__(self)
        self.bind = listening_address
        self.udpQueue = udpQueue
        self.event =event
        self.evtType = evtType

    def run(self):
        print "Starting, my name is: " + self.name
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	try:
            s.bind(self.bind)
        except socket.error, err:
            print "Couldn't bind server on %r" % (self.bind, )
            sys.exit()
        while True:
            datagram = s.recv(self.BUFFER_SIZE)
            #print datagram
            if (self.evtType == "BLOCKING"):
                if self.event.isSet():
                    datagram = ''
                else:
                    self.udpQueue.put(('RXD',self.name,datagram))
            elif (self.evtType == "NOOP"):
                self.udpQueue.put(('RXD',self.name,datagram))
        s.close()


