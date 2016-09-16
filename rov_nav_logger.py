#!/usr/bin/env python

# listens to UDP traffic and creates a DAT file that will then periodically be made into kmls by navtokml
# to use when both Sentry and Herc are in the water

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

# TODO
# define beacon of interest
# for AUV, log SMS messages
# Example call
# python rov_nav_logger.py -f ~/data/visdives/Sentry189 -r ~/data/visdives/Hercules/Herc1279

import socket
from threading import Thread
from threading import Event
from Queue import Queue
import time
import ConfigParser
import datetime
import signal
import argparse
import utm
import calendar
import os

from timers import *
from comms import *
from datetime import date
global logfile
def signal_handler(signal, frame):
	print 'You pressed Ctrl+C!'
	logfile.close()
	rov_logfile.close()
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
		#print message
		msgType = message[0]
		msgSender = message[1]
		msgData = message[2]
		# expected format
		#$PSONALL,Name,Offset,HHMMSS.ss,EEEEEEEE.ee,NNNNNNNN.nn.yy, DDDD.dd,HHH.hh,CCC.cc,T,PP.PP,RR.RR,VVV.vv,AAA.AA,BBB.BB*hhCRLF
		# example
		# $PSONALL,1201,Offset,042044.333,102.89,103.13,512.60,0.00,0.00,G,0.00,0.00,0.00,0.533,0.533*32\r\n'
		#print msgData
		parsed=msgData.split(',',8)
		if len(parsed) > 1:
			hdr=parsed[0]
			dmsec=datetime.datetime.now()
			dmsec_str = str(dmsec)
			nofrag, frag = dmsec_str.split('.')			
			d=time.gmtime()
			# UTC from gmtime does not keep track of sub seconds
			dstr=time.strftime("%Y/%m/%d %H:%M:%S",d) + '.' + frag
			print 'hdr ', hdr

			if hdr[0:3] == 'SMS':  
				tsdata='HST '+dstr+ ' '+ msgData
				logfile.write(tsdata)
				logfile.flush()
				print 'logging HST data', tsdata
			elif hdr[0:3] == 'SPS':
				tsdata='SPS '+dstr+ ' '+ msgData
				logfile.write(tsdata)
				logfile.flush()
				print 'logging SPS data', tsdata
			elif hdr=='$PSONALL':
				print 'parsing PSONALL msg ' + msgData 
			# wish to output format SPS 2011/09/27 22:54:59.546 SPS 1317164099.546 34.229027 -120.384252 421.560 34.216667 -120.433333 1
# conversion needed from UTM to lat lon
				beacon=parsed[1]
				Easting=float(parsed[4])
				Northing=float(parsed[5])
				Depth=parsed[6]
				# ROV beacon 1301
				# Zone 15 R for Galveston
				
				# FIXME unix time shoud be based on Ranger output. It's only HHMMSS.ss
				
								
				
				(lat,lon) = utm.to_latlon(Easting, Northing, 15, 'R')
				tsdata = 'SPS ' + dstr + ' ' + 'SPS ' + str(calendar.timegm(d))+'.'+frag  + ' ' + str(lat) + ' ' +  str(lon) + ' ' + str(Depth) + ' ' + str(lat) + ' ' +  str(lon) + ' 1\n'
				# for Sentry beacon is 1301
				if beacon=='SENTRY':
					logfile.write(tsdata)
					logfile.flush()
					print 'AUV beacon ' + beacon + ' logging SPS data from Ranger PSONALL ', tsdata
				elif beacon=='HURC':
					rov_logfile.write(tsdata)
					rov_logfile.flush()
					print 'ROV beacon ' + beacon + ' logging SPS data from Ranger PSONALL ', tsdata
					
				
					
				

		self.ctrlQueue.task_done()



if __name__ == "__main__":
	print "Parsing command line arguments"

	parser = argparse.ArgumentParser(prog = 'udp_nav_logger.py', description = 'Listens to UDP and generates DAT file', epilog = 'Tested on OSX 10.8.4')
	parser.add_argument('-f', '--logfile', dest = 'logfile_name', default = 'navudp.DAT', help = 'DAT output file name. Do not include extension. Default is navmass.DAT')
	parser.add_argument('-r', '--rov_logfile', dest = 'rov_logfile_name', help = 'DAT output file for ROV on Sonardyne', required = False)
	args = parser.parse_args()
	print "  Log file         : %r" % args.logfile_name
	print "  ROV log file	  : %r" % args.rov_logfile_name

	FROM_SENTRY_UDP_PORT = 56333
	FROM_GUI_UDP_PORT = 52465 
	#logfile = open(sys.argv[1],'w')    
	tstamp = datetime.datetime.now()
	tstamp_str = tstamp.strftime('%Y%m%d_%H%M%S')
	logpath,logfilename = os.path.split(args.logfile_name + '_' + tstamp_str + '.DAT')
	if not os.path.exists(logpath):
		os.makedirs(logpath)
	logfile = open(os.path.join(logpath,logfilename),'w')

	rov_logpath, rov_logfilename = os.path.split(args.rov_logfile_name + '_' + tstamp_str + '.DAT')
	if not os.path.exists(rov_logpath):	
		os.makedirs(rov_logpath)
	rov_logfile = open(os.path.join(rov_logpath,rov_logfilename),'w')
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
