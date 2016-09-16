#!/usr/bin/env python

# listens to UDP traffic and creates a DAT file that will then periodically be made into kmls by navtokml
# tested for Sentry data 
# nmodified from Stefano's below
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
import time
import ConfigParser
import datetime
import signal
import argparse

from timers import *
from comms import *
from datetime import date
global logfile
def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        logfile.close()
        sys.exit(0)

class Controller(Thread):
    """ used to manage data paths
    """
    def __init__(self, myname, ctrlQueue, udpQueue, udGuiQueue,logfile):
        Thread.__init__(self)
        self.name = myname
        self.ctrlQueue = ctrlQueue
        self.udpQueue = udpQueue
        self.udpGuiQueue = udpGuiQueue
        self.logfile = logfile


    def run(self):
        print "Starting, my name is: " + self.name

#        self.activeSendQueue = self.serialQueue
        udpQueue.put(('PAUSE',self.name,' '))


        while True:
#            print "Ctrl queue size is: " + str(self.ctrlQueue.qsize())
		message=self.ctrlQueue.get()
		msgType = message[0]
		msgSender = message[1]
		msgData = message[2]
		parsed=msgData.split(' ',1)
		if len(parsed) > 1:
			hdr=parsed[0]
			d=datetime.datetime.now()
			dstr=d.strftime("%Y/%m/%d %H:%M:%S.%f")
			#print 'hdr ', hdr

			if hdr[0:3] == 'SMS':  
				tsdata='HST '+dstr+ ' '+msgData
				logfile.write(tsdata)
				logfile.flush()
				print 'logging HST data', tsdata
			elif hdr[0:3] == 'SPS':
				tsdata='SPS '+dstr+ ' '+msgData
				logfile.write(tsdata)
				logfile.flush()
				print 'logging SPS data', tsdata

		self.ctrlQueue.task_done()



if __name__ == "__main__":
	print "Parsing command line arguments"

	parser = argparse.ArgumentParser(prog = 'mass_nav_logger.py', description = 'Listens to UDP and generates DAT file', epilog = 'Tested on OSX 10.8.4')
	parser.add_argument('-f', '--logfile', dest = 'logfile_name', default = 'navmass.DAT', help = 'DAT output file name. Include extension. Default is navmass.DAT')
	#parser.add_argument('-d', '--datapath', dest = 'dvlnavdatapath', help = 'path of DVLNAV files', required = True)
	args = parser.parse_args()
	print "  Log file         : %r" % args.logfile_name

	FROM_SENTRY_UDP_PORT = 12350
	FROM_GUI_UDP_PORT = 60103
	#logfile = open(sys.argv[1],'w')    
	logfile = open(args.logfile_name,'w')
	signal.signal(signal.SIGINT, signal_handler)
    # '' = receive broadcast
    # '<broadcast>' = send broadcast

	LISTEN_IP = ""
	TARGET_IP = "127.0.0.1"
#    TARGET = (TARGET_IP, TO_SENTRY_UDP_PORT)
	LISTEN_GUI_IP = ''
	TARGET_GUI_IP = '<broadcast>'

	LISTEN = (LISTEN_IP, FROM_SENTRY_UDP_PORT) # Should listen for the GRD msg on port 12350 on Sentry net
	
	LISTEN_GUI = (LISTEN_GUI_IP, FROM_GUI_UDP_PORT) # TBD

	config = ConfigParser.RawConfigParser()
#    config.read(SENTRY_POWER_INI_PATH)


	udpQueue = Queue()      # queue for messages going into UdpThread
	udpGuiQueue = Queue()   # queue for messages going into UdpGuiThread
	ctrlQueue = Queue()     # queue for messages going into ControllerThread
	#ser=SerialThread(DEVICE,BAUDRATE,serialQueue, ctrlQueue)
	#ser.name = 'SerialThread'
	#ser.start()
	
	udp=UdpThread(LISTEN, None, 'UdpThread', udpQueue, ctrlQueue, "NOOP")
	udp.daemon=True
	udp.start()
	udpGui=UdpThread(LISTEN_GUI, None, 'UdpGuiThread', udpGuiQueue, ctrlQueue, "NOOP")
	udpGui.daemon=True
	udpGui.start()
	ctrl=Controller('ControllerThread', ctrlQueue, udpQueue, udpGuiQueue,logfile)
	ctrl.daemon=True
	ctrl.start()
	
	while True:
		time.sleep(1)
