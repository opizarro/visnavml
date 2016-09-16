#!/usr/bin/env python
#
# Generate KML file from navigation and sensor data
# interpolates position to the sensor reading
# color-codes readings based on range of sensor values
#
# 2011-09-20 SS - created and written
# 2013-07 OP and MJR modified for Sentry mass spec and fluorometer use

import sys
import os
import glob
import ConfigParser
import argparse
import time
import collections
import bisect
import simplekml
from pynmea import nmea
from datetime import datetime
from decimal import Decimal
from itertools import izip
from parseSMS import parseSMS
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
def jet(value):
	fourValue = 4 * value;
	red   = clamp(min(fourValue - 1.5, -fourValue + 4.5),0.0,1.0);
	green = clamp(min(fourValue - 0.5, -fourValue + 3.5),0.0,1.0);
	blue  = clamp(min(fourValue + 0.5, -fourValue + 2.5),0.0,1.0);
 
	return int(255*red), int(255*green), int(255*blue)

def pairs(lst):
    i = iter(lst)
    first = prev = item = i.next()
    for item in i:
        yield prev, item
        prev = item
    yield item, first
def pairwise(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)

def flr_conc(flr_voltage):
	# from Chelsea Technologies Group cerficate of calibration UV aquatracka S/N 04-4671-001
	return 0.001205*10**float(flr_voltage)-0.043360

class VehicleFix:
	def __init__(self, lat, lon, depth):
		#self.lat, self.lon, self.depth = lat+Decimal(0.000202), lon-Decimal(0.000705), depth
		self.lat, self.lon, self.depth = lat, lon, depth
	def println(self):
		print "(lat: %lf, lon: %lf, depth: %lf)" % (self.lat, self.lon, self.depth)
	def kmlcoords(self):
		return (self.lon, self.lat, -self.depth)
		 


gpgga = nmea.GPGGA()

USBL = collections.OrderedDict()
GPS  = collections.OrderedDict()
FLUR  = collections.OrderedDict()
MASS  = collections.OrderedDict()

#ind = bisect.bisect_left(a.keys(), 45.3)


global pathtokml
#pathtokml = 'http://www-personal.acfr.usyd.edu.au/opizarro/tioga002'
#pathtokml = os.getcwd()
pathtokml = 'contents/'
	

def string_HST(data, verbose, t):
	split_data = data.split(',',1)
	if (split_data[0] == '$GPGGA'):
		gpgga.parse(data)
		lat = Decimal(gpgga.latitude)
		long = Decimal(gpgga.longitude)
		lat = ((lat-(lat%100))/100)+(lat%100)/60
		long = ((long-(long%100))/100)+(long%100)/60
		if gpgga.lon_direction == 'W':
			long*=-1;
		if gpgga.lat_direction == 'S':
			lat*=-1
		GPS[t] = VehicleFix(float(lat),float(long), 0.0)
	elif split_data[0][0:3] == 'SMS':
		rest,queue=parseSMS(data)
		if rest != None:
			if queue == '005':		
				#print 'strip msg ' + str(rest.strip('\r\n').split(' ')	)									
				l=map(float,rest.strip('\r\n').split(' '))
# TODO assign keys from names of peaks
				try:												#
					MASS[t]={'time': l[0], 'unk': l[1], 'x':l[2], 'y':l[3],'depth':l[4], 'alt':l[5], 'peak15':l[6],'peak17':l[7],'peak27':l[8],'peak43':l[9],'peak78':l[10]}
				except:
					print "problem with line", rest
			elif queue == '045':
				if len(rest.strip('\r\n').split(' '))>6:
					FLUR[t]=dict(e.split(':') for e in rest.strip('\r\n').split(' ')[4:6])
				else:
					print 'Not proper length for ' + rest 
				#print 'FLUR[t] ' + str(FLUR[t])
			else: 
				print 'Not using queue ', queue
	


def string_SPS(data, verbose, t):
	if verbose:
		print "Processing SPS log"
	SPSsplittedString = data.split(' ')
	USBL[t] = VehicleFix(Decimal(SPSsplittedString[2]), Decimal(SPSsplittedString[3]), Decimal(SPSsplittedString[4]))

def interp1d(t,x1,x2,y1,y2,z1,z2,t1,t2):
	if t2 != t1:	
		u=(t-t1)/(t2-t1)
	else:
		u=0
	x=x1+u*(x2-x1)
	y=y1+u*(y2-y1)
	z=z1+u*(z2-z1)
	return (x,y,z)
				
def getClosePos(vehiclefix_col,t,keys):
	#keys = sorted(vehiclefix_col.keys())
	index = bisect.bisect(keys, t)
	if index >= 1:
		k1=(index - 1)									
	else:
		k1=index
		#print 'not interp using single point at start' 

	if index >= len(keys):
		k2=len(keys)-1
		#print 'not interp using single point at end'
	else:
		k2=index	 
	#print t, 'k1 ', k1, 'k2 ', k2, 'index ', index, 'len keys ',len(keys),  'length vehiclefix_col ', len(vehiclefix_col)
	x1=float(vehiclefix_col[keys[k1]].kmlcoords()[0])
	y1=float(vehiclefix_col[keys[k1]].kmlcoords()[1])
	z1=float(vehiclefix_col[keys[k1]].kmlcoords()[2])
	#print k2, len(keys)
	x2=float(vehiclefix_col[keys[k2]].kmlcoords()[0])
	y2=float(vehiclefix_col[keys[k2]].kmlcoords()[1])
	z2=float(vehiclefix_col[keys[k2]].kmlcoords()[2])
	x,y,z=interp1d(float(t),x1,x2,y1,y2,z1,z2,float(keys[k1]),float(keys[k2]))
	return (x,y,z)

# Main program
def convert_to_kml(verbose,progress,ini_file,dvlnavdatapath,savepath,files_dict):
	# Define dictionary of string types and callback functions
	stringType = {
	'HST'    : string_HST,
	'SPS'    : string_SPS,
	}	
	
	csvoutput = open(os.path.join(savepath,'stacked_mass.csv'),'w')
	# Set the timestamp format of input logs
	dsl_time_format = "%Y/%m/%d %H:%M:%S.%f"
	

	# Manage command line arguments
	# Parse ini file
	print "Parsing ini file"
	config = ConfigParser.ConfigParser()
	config.readfp(open(ini_file))

	#os.chdir(dvlnavdatapath)
	for dvlnavfile in glob.glob(dvlnavdatapath+"*.DAT"):
		print "Reading DVLNAV file %s..." % dvlnavfile
		data_fd = open(dvlnavfile)
		content = "Start"
		while (content != "" ):
			content = data_fd.readline()
			split_string = content.split(None, 3)
			if len(split_string) == 4: #Process only the lines that have header,date,time,string (4 items in list)
				if verbose:
					print "Parsed string         : %s" % content
				try:
					mytime = datetime.strptime(split_string[1] + " " + split_string[2], dsl_time_format)
#FIXME strftime('%s') is not true UTC or sopported by Python					
					tstring = mytime.strftime("%s.%f")
					t = Decimal(tstring)
				except ValueError:
					print 'Problem parsing time to t ' + split_string[1] + " " + split_string[2] + ' with ' + dsl_time_format 
					continue
				
				if progress:	
					print "Processing timestamp  : %s" % t
				if verbose:
					print "Parsed string         : %s" % content
					print "Splitted string       : %s" % split_string
				if split_string[0] in stringType:
					stringType[split_string[0]](split_string[3], verbose, t)


	# Do refreshmode 'onchange' and set 'refreshinterval'
	
	#for timestamp, Fix in USBL.items():
		#print str(timestamp)
		#Fix.println()
	#	kml.newpoint(name="Sentry", coords=[Fix.kmlcoords()])  # lon, lat, optional height
	#kml.save("sentry098.kml")
	print 'Starting list comprehension for mass spec'
	sortkeys = sorted(USBL.keys());
	massptlist = [tuple([getClosePos(USBL,timestamp,sortkeys),dat,timestamp])  for timestamp, dat in MASS.items()]
	print 'End list comprehension for mass spec'    
				
	if len(massptlist) > 0:  
		for fname in files_dict.keys():
			if not files_dict[fname].closed:
				files_dict[fname].close()
			key=os.path.splitext(fname)[0]
			
			kml = simplekml.Kml()
			kml.AltitudeMode = 'absolute'
			print 'processing ', key
			min_val = min(item[1][key] for item in massptlist)
			max_val = max(item[1][key] for item in massptlist)
			
					
			
			#print 'asd',min_val,max_val
			#ls = kml.newlinestring(name='Mass '+ key)
			for Pos,massdata,timestamp in massptlist:
				#print Pos
				pnt=kml.newpoint(name=key, coords=[Pos])
				pnt.altitudemode = 'absolute'
				pnt.style.iconstyle.icon.href='circle.png'
				if max_val > min_val:
					pnt.style.iconstyle.color = simplekml.Color.rgb(*jet((massdata[key]-min_val)/(max_val-min_val)))
				else:
					pnt.style.iconstyle.color = '28000000' # translucent black
				pnt.style.iconstyle.scale = 0.25 
				pnt.style.labelstyle.scale = 0
				# actual value of mass spec peak as description bubble
				pnt.description = str(massdata[key]) + '\n at ' + ('%.2f' % Pos[2]) + ' [m]'	
				
				# hack to write an easy to parse file for Rich's matlab routine
				csvline = key[4:] + ' ' +  str(massdata[key]) + ' '+ '%.2f' % timestamp + ' ' + '%.7f' % Pos[1]  +' ' + '%.7f' % Pos[0] + ' ' + '%.1f' % Pos[2] + '\n'
				#print '*** THIS WOULD BE LOGGED ' + csvline
				csvoutput.write(csvline)
				csvoutput.flush()
				
			print 'Saving ', fname
			kml.save(savepath + fname)
			
			
			try:
				min_val_norm = min(item[1][key]/item[1]['peak17'] for item in massptlist if item[1]['peak17']>0 )
				max_val_norm = max(item[1][key]/item[1]['peak17'] for item in massptlist if item[1]['peak17']>0 )	
			except:
				print 'Problem calculating max min\n'	
				min_val_norm = 0
				max_val_norm = 1	
				
				
			kmln = simplekml.Kml()
			kmln.AltitudeMode = 'absolute'
			for Pos,massdata,timestamp in massptlist:
				pnt=kmln.newpoint(name=key+' normalized', coords=[Pos])
				pnt.altitudemode = 'absolute'
				pnt.style.iconstyle.icon.href='circle.png'
				if (max_val_norm > min_val_norm) & (massdata['peak17'] > 0):
					pnt.style.iconstyle.color = simplekml.Color.rgb(*jet((massdata[key]/massdata['peak17']-min_val_norm)/(max_val_norm-min_val_norm)))
					pnt.description = str(massdata[key]/massdata['peak17']) + ' (normalized to peak17) \n at ' + ('%.2f' % Pos[2]) + ' [m]'
				else:
					pnt.style.iconstyle.color = '28000000' # translucent black
				pnt.style.iconstyle.scale = 0.25 
				pnt.style.labelstyle.scale = 0
				# actual value of mass spec peak as description bubble
									
			print 'Saving ', key + '_normalized17.kml'
			kmln.save(savepath + key + '_normalized17.kml')
			
	print 'Starting list comprehension for Flourometer'
	flurptlist = [tuple([getClosePos(USBL,timestamp,sortkeys),dat])  for timestamp, dat in FLUR.items()]
	print 'End list comprehension for Flourometer'
	#print 'flr dict ', flurptlist
	if len(flurptlist) > 0:
		kml = simplekml.Kml()
		kml.AltitudeMode = 'absolute'
		print 'processing FLR'
		key = 'avg'
		#min_val = min(float(item[1][key]) for item in flurptlist)
		#max_val = max(float(item[1][key]) for item in flurptlist)
		# 20130718 temp hack to plot Tiaoga data 		
		min_val = flr_conc(2.96)
		max_val = flr_conc(3.0)		
		for Pos, flrdata in flurptlist:
			pnt=kml.newpoint(name=key, coords=[Pos])
			pnt.altitudemode = 'absolute'
			pnt.style.iconstyle.icon.href='circle.png'
			if max_val > min_val:
				pnt.style.iconstyle.color = simplekml.Color.rgb(*jet((flr_conc(flrdata[key])-min_val)/(max_val-min_val)))
			else:
				pnt.style.iconstyle.color = '28000000' # translucent black
			pnt.style.iconstyle.scale = 0.25 
			pnt.style.labelstyle.scale = 0
			# actual value of flr as description bubble
			pnt.description = str(flr_conc(flrdata[key])) + '\n at, ' + ('%.2f' % Pos[2]) + ' [m]'			
		print 'Saving flr.kml'
		kml.save(savepath + 'flr.kml')
	else:
		print '===== No FLR data to process! ====== \n'
		
		
#        print massptlist
 #       print flurptlist
	ptlist = [Fix.kmlcoords() for timestamp, Fix in USBL.items()]
	if len(ptlist) > 0:
		print 'processing FLR'
		kml = simplekml.Kml()
		kml.AltitudeMode = 'absolute'
		
		
		ls = kml.newlinestring(name='Vehicle')
		ls.coords = ptlist
		#ls.extrude = 1
		ls.style.linestyle.width = 3
		ls.style.linestyle.color = simplekml.Color.forestgreen
		ls.altitudemode = simplekml.AltitudeMode.relativetoground
		ls.style.linestyle.color = simplekml.Color.changealphaint(120, simplekml.Color.green)
		
		kml.save(savepath + "line.kml")
	else:
		print  '===== No NAV data to process! ====== \n'
	
#	kml = simplekml.Kml()
#	maxitems=float(len(USBL.items()))
#	i=float(0)
#	for p1,p2 in pairs(USBL.items()):
#		seg=[p1[1].kmlcoords(),p2[1].kmlcoords()]
#		ls = kml.newlinestring(name='Seg')
#		ls.coords = seg
#	#ls.extrude = 1
#		ls.style.linestyle.width = 5
#		ls.style.linestyle.color = simplekml.Color.rgb(*jet(i/maxitems))
#		ls.altitudemode = simplekml.AltitudeMode.absolute
#		i=i+1.0
#	kml.save("seg.kml")
#        for p1,p2 in pairs(GPS.items()):
#                seg=[p1[1].kmlcoords(),p2[1].kmlcoords()]
#                ls = kml.newlinestring(name='GPS')
#                ls.coords = seg
#                #ls.extrude = 1                                                         
#                ls.style.linestyle.width = 5
#                ls.style.linestyle.color = simplekml.Color.red
#                ls.altitudemode = simplekml.AltitudeMode.relativetoground
#
#
##	for timestamp, Fix in GPS.items():
#		#print str(timestamp)
#	#	kml.newpoint(name="Ship", coords=[Fix.kmlcoords()])  # lon, lat, optional height
#	kml.save("gps.kml")

	# Finished
	print "Done"

if __name__ == "__main__":
	t1 = time.time()
	print "Parsing command line arguments"
	parser = argparse.ArgumentParser(prog = 'navtokml.py', description = 'Generate KML files from NAV data', epilog = 'Tested on Ubuntu Linux 12.04 64bit')
	parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', default = False, help = 'arg needed for verbose output, default is False')
	parser.add_argument('-p', '--progress', dest = 'progress', action = 'store_true', default = False, help = 'arg needed for showing progress status, default is False')
	parser.add_argument('-i', '--input', dest = 'input', default = 'navtokml.ini', help = 'ini file for %(prog)s, default is navtokml.ini')
	parser.add_argument('-d', '--datapath', dest = 'dvlnavdatapath', help = 'path of DVLNAV files', required = True)
	parser.add_argument('-l', '--savepath', dest = 'savepath', help = 'path of output KML files', required = True)
	
	args = parser.parse_args()
	print "  Verbose          : %r" % args.verbose
	print "  Progress         : %r" % args.progress
	print "  Ini file         : %s" % args.input
	print "  DVLNAV data path : %s" % args.dvlnavdatapath
	print "  output path KMLs  : %s" % args.savepath
	peaks = open('peaks.txt').read().split()
	files_dict={}
	
	for filename in peaks:
		files_dict.setdefault(filename + '.kml', open(filename,'w'))
	convert_to_kml(verbose=args.verbose,progress=args.progress,ini_file=args.input,dvlnavdatapath=args.dvlnavdatapath,savepath=args.savepath,files_dict=files_dict)
	t2 = time.time()
	print 'Reading took %0.6f s' % (t2-t1)
