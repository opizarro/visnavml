#!/usr/bin/env python
# takes a sid file from mass spec laptop and generates a DAT-like log with HST 
# once in a DAT file format, it can be read and parsed into kml
# TODO does not deal with non-integer seconds

import csv
import sys
import time
import datetime
import argparse

def convert_flr_to_csv(flrdatafile, savefile):
	with open(flrdatafile, 'rb') as flrfile:
		# print date	
		magic=flrfile.readline()
		#print magic
		# print log file
		magic=flrfile.readline()
		#print magic
		# read in headers
		# Cycle Number, Step Number, SIM Number, Record Number, Start Date, Start Time, End Date, End Time, Start CTD, End CTD
		input_file = csv.DictReader(flrfile, restkey='peaks', delimiter=',', quotechar='|')	
		output = open(savefile,'w')
		# skip next two lines
		next(input_file,None)
		next(input_file,None)
		for row in input_file:
			#print row 4-5-2011,20:47:57,4-5-2011,20:48:39
			start = row[' Start Date'] + ' '+ row[' Start Time'] 

			stime = datetime.datetime.strptime(start,"%m-%d-%Y %H:%M:%S")
					
			#start_unixtime_string = calendar.timegm(stime.timetuple()) 
			stime_string = stime.strftime('%Y,%m,%d,%H,%M,%S')
			
			
			end = row[' End Date'] + ' '+ row[' End Time'] 

			etime = datetime.datetime.strptime(end,"%m-%d-%Y %H:%M:%S")
			etime_string = etime.strftime('%Y,%m,%d,%H,%M,%S')
			#start_unixtime_string = calendar.timegm(etime.timetuple()) 			
			
		
	
	#0000001,05,01,000000001,3-29-2011,18:24:09,3-29-2011,18:24:42,,,0000005751.981,0000355790.656,0000416273.062,0000179229.047,0000059842.465,0000043170.125
			peak_str = ''
			for elem in row['peaks'][8:13]:
				#print elem
				peak_str = peak_str + ','+ str(elem)
				
				#print peak_str
				
				
				
			output.write(stime_string + ',' + etime_string + ',' + peak_str + '\n')
	output.close()

if __name__ == "__main__":
	t1 = time.time()
	print "Parsing command line arguments"
	parser = argparse.ArgumentParser(prog = 'parse_fluor_to_csv.py', description = 'Generate DAT files from fluorometer file', epilog = 'Tested on OSX 10.8.4')
	#parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', default = False, help = 'arg needed for verbose output, default is False')
	#parser.add_argument('-p', '--progress', dest = 'progress', action = 'store_true', default = False, help = 'arg needed for showing progress status, default is False')
	#parser.add_argument('-i', '--input', dest = 'input', default = 'navtokml.ini', help = 'ini file for %(prog)s, default is navtokml.ini')
	parser.add_argument('-d', '--datafile', dest = 'flrdatafile', help = 'path to flr files', required = True)
	parser.add_argument('-l', '--savefile', dest = 'savefile', help = 'output csv file', required = True)
	args = parser.parse_args()
	#print "  Verbose          : %r" % args.verbose
	#print "  Progress         : %r" % args.progress
	#print "  Ini file         : %s" % args.input
	print "  flr data file : %s" % args.flrdatafile
	print "  output file csv  : %s" % args.savefile
	
	convert_flr_to_csv(flrdatafile=args.flrdatafile,savefile=args.savefile)
	t2 = time.time()
	print 'Reading took %0.6f s' % (t2-t1)