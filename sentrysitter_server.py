#!/usr/bin/env python

# DESCRIPTION: a program that acts as a dual-link proxy server between
# the SentrySitter GUIs and Sentry.  Connection can be switched between
# ethernet and SAIL.
#
# INSTALLATION: no installation required. Modify the serial port device
# to the device connected to the APS magnetometer and the ports
#
# USAGE: launch the program with ./sentrysitter_server.py
#
# AUTHOR: Stefano Suman, ssuman@whoi.edu
#
# MODIFICATION HISTORY
# 2011-12-10 SS - created


import socket
from threading import Thread
from threading import Event
from Queue import Queue
import serial
import time
import ConfigParser
import datetime

from timers import *
from comms import *
from sshworker import *
import sail

DEVICE = '/dev/ttyUSB0'
BAUDRATE = 9600

SENTRY_POWER_INI_PATH = "../sentry_cmds/sentry_power.ini"
MAX_TIME_NO_POLL_SAIL = 65

class Controller(Thread):
    """ used to manage data paths
    """
    def __init__(self, myname, ctrlQueue, udpQueue, serialQueue, udGuiQueue):
        Thread.__init__(self)
        self.name = myname
        self.ctrlQueue = ctrlQueue
        self.udpQueue = udpQueue
        self.serialQueue = serialQueue
        self.udpGuiQueue = udpGuiQueue
        self.sailBus = sail.Bus()
        self.sailBus.lock()

    def hex2bin(self,string):
        bin = [' 0 0 0 0',' 0 0 0 1',' 0 0 1 0',' 0 0 1 1',
               ' 0 1 0 0',' 0 1 0 1',' 0 1 1 0',' 0 1 1 1',
               ' 1 0 0 0',' 1 0 0 1',' 1 0 1 0',' 1 0 1 1',
               ' 1 1 0 0',' 1 1 0 1',' 1 1 1 0',' 1 1 1 1']
        aa = ''
        for i in range(len(string)):
            aa += bin[int(string[i],base=16)]
        return aa

    def unwrap_power_status(self,hexstr_pwr): # hexstr_pwr is the string with the 8 double-hex-digits power status
        hexsplit = hexstr_pwr.split(' ')
        binary = ''
        for byte in hexsplit: # loop over all the bytes
            binary += self.hex2bin(byte)
        return binary

    def run(self):
        print "Starting, my name is: " + self.name

        self.activeSendQueue = self.serialQueue
        udpQueue.put(('PAUSE',self.name,' '))

        self.serGrdPoll = customTimer(2.0, self.ctrlQueue, "GrdPollTimer", '#GRD/PWR?P') # Set and start the GRD poll timer, with a 5 seconds interval
        self.serGrdPoll.start()
        self.serGrdPoll.pause()

        self.rovSafeTmr = customTimer(10.0, self.udpQueue, "SafeRovTimer", 'NSC CMD_GENERIC_PWR #GRD/PWR!ICFFX') # Set rov CMD_GENERIC_PWR to a safe FF every 10 seconds
        self.rovSafeTmr.start()
        self.rovSafeTmr.pause()

        self.sailUnlockTmr = customTimer(5.0, self.ctrlQueue, "SailUnlockTimer", 'SAIL UNLOCK CHECK') # Set and start the GRD poll timer, with a 5 seconds interval
        self.sailUnlockTmr.start()

        while True:
            print "Ctrl queue size is: " + str(self.ctrlQueue.qsize())
            message=self.ctrlQueue.get()
            msgType = message[0]
            msgSender = message[1]
            msgData = message[2]

            if (msgType == 'RXD'): # got a message from Sentry's NIO or SIO
                print "Controller got this: " + msgData
                print "Length:              " + str(len(msgData))

                if ((not('#GRD/PWR?P' in msgData)) and not('PWR!IS' in msgData) and not('PWR!IC' in msgData) and (msgSender is 'SerialThread')):
                    self.sailBus.lock()
                    print "locked the sail bus!"

                if ((len(msgData) == 69) and ('#GRD/PWR?P' in msgData)): # This is our received power status from ROV
                    try:
                        split = msgData.split(' ',3)
                        power_status = split[3][10:33]
                        print "Power status: " + power_status
                        binary = self.unwrap_power_status(power_status) # Here I transform the power status from hex to bin
                        if(self.activeSendQueue == self.serialQueue):
                            self.ctrlQueue.put(('WAS','UdpGuiThread','SWITCH ETH')) # automatically switch to ETH when I receive the first PWS from ROV
                        self.udpGuiQueue.put(('WAS',self.name,'PWRST ' + binary))
                        self.udpGuiQueue.put(('WAS',self.name,'SOURCE 0')) # Tell the GUI that this message came from SAIL
                    except:
                        pass

                elif ((self.activeSendQueue == self.serialQueue) and (len(msgData) == 41) and ('#GRD/PWR?P' in msgData)): # This is serial power status from SAIL
                    try:
                        power_status = msgData[10:33]
                        print "Power status: " + power_status
                        binary = self.unwrap_power_status(power_status) # Here I transform the power status from hex to bin
                        self.udpGuiQueue.put(('WAS',self.name,'PWRST ' + binary))
                        self.udpGuiQueue.put(('WAS',self.name,'SOURCE 1')) # Tell the GUI that this message came from SAIL
                    except:
                        pass

                elif ((('GAS' in msgData) or ('DVZ' in msgData) or ('GVX' in msgData) or ('AUV' in msgData) or ('RSVPASCII' in msgData)) and (msgSender == 'UdpThread')):
                    self.udpGuiQueue.put(('WAS',self.name,msgData))

                elif (('HTP' in msgData) and (msgSender == 'UdpThread')): # forward the HTP messages to the GUI (strip the GRD and timestamp)
                    splitmsg = msgData.split(' ',3)
                    self.udpGuiQueue.put(('WAS',self.name,splitmsg[3]))

            if (msgSender == 'UdpGuiThread'): # received a message from a GUI thread name

                if '!IS' in msgData: # this is a "turn on" command
                    if (self.activeSendQueue == self.serialQueue):
                        print msgData
                        self.serialQueue.put(('WAS', self.name, msgData))
                    elif (self.activeSendQueue == self.udpQueue):
                        self.udpQueue.put(('WAS', self.name, 'NSC CMD_GENERIC_PWR ' + msgData))                    

                elif '!IC' in msgData: # this is a "turn off" command
                    if (self.activeSendQueue == self.serialQueue):
                        self.serialQueue.put(('WAS', self.name, msgData))
                    elif (self.activeSendQueue == self.udpQueue):
                        self.udpQueue.put(('WAS', self.name, 'NSC CMD_GENERIC_PWR ' + msgData))

                elif 'SWITCH ETH' in msgData: # this is a GUI-initiated "switch connection" command, to use NIO
                    if (self.activeSendQueue == self.serialQueue): # Switch from serial to udp
                        self.activeSendQueue = self.udpQueue
                        serialQueue.put(('PAUSE',self.name,' '))
                        udpQueue.put(('RESUME',self.name,' '))
                        self.serGrdPoll.pause()
                        self.rovSafeTmr.resume()
                        self.udpGuiQueue.put(('WAS',self.name,'SOURCE 0')) # Tell the GUI that we switched to ETH
                        print "Switching to udp link"

                elif 'SWITCH SAIL' in msgData: # this is a GUI-initiated "switch connection" command, to use SIO
                    if (self.activeSendQueue == self.udpQueue): # Switch from udp to serial
                        self.activeSendQueue = self.serialQueue
                        udpQueue.put(('PAUSE',self.name,' '))
                        serialQueue.put(('RESUME',self.name,' '))
                        self.serGrdPoll.resume()
                        self.rovSafeTmr.pause()
                        self.udpGuiQueue.put(('WAS',self.name,'SOURCE 1')) # Tell the GUI that we switched to SAIL
                        print "Switching to SAIL link"

                elif 'BOOTSTRAP VEHICLE' in msgData: # this is a GUI-initiated vehicle bootstrap command, use SIO
                    if (self.activeSendQueue == self.serialQueue):
                        bootstrapMsg = '##GRD!S'
                        self.serialQueue.put(('WAS', self.name, bootstrapMsg))
                        time.sleep(1) # Just sleep for 1 second before sending the bootstrap confirmation
                        bootstrapConfirmMsg = 'S'
                        self.serialQueue.put(('WAS', self.name, bootstrapConfirmMsg))
                        time.sleep(1)
                        self.serGrdPoll.resume()

                elif 'START SAIL PWR TIMER' in msgData:
                    self.serGrdPoll.resume()

                elif 'UNLOCK SAIL' in msgData:
                    self.sailBus.unlock()

                elif 'LOCK SAIL' in msgData:
                    self.sailBus.lock()

                elif 'STOP SAIL PWR TIMER' in msgData:
                    self.serGrdPoll.pause()

                elif 'SSH COMMAND' in msgData:
                    try:
                        if not self.sailBus.is_locked():
                            self.sailBus.lock()
                            command = msgData.split(' ')[2]
                            if (command in cmdDict): # Execute the ssh command only if it is in the list of permitted commands
                                t = threading.Thread(target=executeSshCommand, args=(host, user, password, command, self.ctrlQueue,))
                                t.start()
                    except:
                        print "Error while executing SSH command"

                else: # These are commands from the terminal lineEdit, be careful!!!
                    if (self.activeSendQueue == self.serialQueue):
                        self.serialQueue.put(('WAS', self.name, msgData))
                    elif (self.activeSendQueue == self.udpQueue):
                        self.udpQueue.put(('WAS', self.name, 'NSC CMD_GENERIC_PWR ' + msgData))

            elif (msgSender == 'GrdPollTimer'):
                if not self.sailBus.is_locked():
                    self.serialQueue.put(('WAS', self.name, msgData))
                else:
                    print "Received sail poll timer but sail bus is locked"

            elif (msgSender == 'SailUnlockTimer'):
                if (self.sailBus.is_locked()):
                    locktime = self.sailBus.lock_time()
                    currentTime = datetime.datetime.utcnow()
                    timeDifference = (currentTime - locktime).seconds
                    print "Sail lock was %s seconds ago" % repr(timeDifference)
                    if (timeDifference > MAX_TIME_NO_POLL_SAIL):
                        self.sailBus.unlock()

            if (msgType == 'SSH'): # received an output after a SSH command
                if (msgSender in cmdDict): # Check if the command response is in the list of registered commands
                    self.sailBus.unlock()
                    self.udpGuiQueue.put(('WAS',self.name,' '.join(['msgSender',msgData]))) # Tell the GUI that we switched to ETH

            self.ctrlQueue.task_done()



if __name__ == "__main__":
    host = "213.123.1.100"
    user = "sentrysitter"
    password = "dsl!sitt"

    TO_SENTRY_UDP_PORT = 13300
    FROM_SENTRY_UDP_PORT = 12350

    TO_GUI_UDP_PORT = 60103
    FROM_GUI_UDP_PORT = 60102

    TO_SAIL_UDP_PORT = 55677
    FROM_SAIL_UDP_PORT = 55678

    # '' = receive broadcast
    # '<broadcast>' = send broadcast

    LISTEN_IP = ""
    TARGET_IP = "213.123.1.100"
    LISTEN_GUI_IP = ''
    TARGET_GUI_IP = '<broadcast>'
    LISTEN_SAIL_IP = ''
    TARGET_SAIL_IP = "213.123.1.140"
    LISTEN = (LISTEN_IP, FROM_SENTRY_UDP_PORT) # Should listen for the GRD msg on port 12350 on Sentry net
    TARGET = (TARGET_IP, TO_SENTRY_UDP_PORT) # The port in ROV where the NSC commands are received
    LISTEN_GUI = (LISTEN_GUI_IP, FROM_GUI_UDP_PORT) # TBD
    TARGET_GUI = (TARGET_GUI_IP, TO_GUI_UDP_PORT) # TBD
    LISTEN_SAIL = (LISTEN_SAIL_IP, FROM_SAIL_UDP_PORT)
    TARGET_SAIL = (TARGET_SAIL_IP, TO_SAIL_UDP_PORT)

    config = ConfigParser.RawConfigParser()
    config.read(SENTRY_POWER_INI_PATH)

    serialQueue = Queue()   # queue for messages going into SerialThread
    udpQueue = Queue()      # queue for messages going into UdpThread
    udpGuiQueue = Queue()   # queue for messages going into UdpGuiThread
    ctrlQueue = Queue()     # queue for messages going into ControllerThread
    #ser=SerialThread(DEVICE,BAUDRATE,serialQueue, ctrlQueue)
    #ser.name = 'SerialThread'
    #ser.start()
    udpSail=UdpThread(LISTEN_SAIL,TARGET_SAIL, 'SerialThread', serialQueue, ctrlQueue, "BLOCKING")
    udpSail.daemon=True
    udpSail.start()
    udp=UdpThread(LISTEN, TARGET, 'UdpThread', udpQueue, ctrlQueue, "NOOP")
    udp.daemon=True
    udp.start()
    udpGui=UdpThread(LISTEN_GUI, TARGET_GUI, 'UdpGuiThread', udpGuiQueue, ctrlQueue, "NOOP")
    udpGui.daemon=True
    udpGui.start()
    ctrl=Controller('ControllerThread', ctrlQueue, udpQueue, serialQueue, udpGuiQueue)
    ctrl.daemon=True
    ctrl.start()

    while True:
        time.sleep(1)
