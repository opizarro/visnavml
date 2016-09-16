#!/usr/bin/env python
# takes a sid file from mass spec laptop and generates a DAT-like log with HST 
# once in a DAT file format, it can be read and parsed into kml
# TODO does not deal with non-integer seconds

import csv
import sys
import time
import datetime
import argparse

def convert_sid_to_DAT(sidfile, DATfile):
	with open(sidfile, 'rb') as csvfile:
		# print date	
		magic=csvfile.readline()
		#print magic
		# print log file
		magic=csvfile.readline()
		#print magic
		# read in headers
		# Cycle Number, Step Number, SIM Number, Record Number, Start Date, Start Time, End Date, End Time, Start CTD, End CTD
		input_file = csv.DictReader(csvfile, restkey='peaks', delimiter=',', quotechar='|')	
		output = open(DATfile,'w')
		# skip next two lines
		next(input_file,None)
		next(input_file,None)
		for row in input_file:
			#print row
			s = row[' Start Date'] + ' '+ row[' Start Time'] 
			
			s_dt=datetime.datetime.strptime(s,"%m-%d-%Y %H:%M:%S")
			
			t= time.mktime(s_dt.timetuple())
			str_date_time = s_dt.strftime('%Y/%m/%d %H:%M:%S')
			
			#print t, str_date_time
				#output.write('SPS ' + row['yy/mm/dd'] + ' ' +row['hh:nn:ss'] + ' SPS ' +str(t) + ' ' + row['lat'] + ' ' +row['lon']+ ' '+row['depth'] +' '+  row['lat'] + ' ' +row['lon'] + '1\n')
	
	# desired output format
	# HST 2013/07/16 15:34:28.920740 SMS:1101,R1 SMS:1101,R1143861|005  1317165169.6 6 -289 346 -446.0 3.4 2.688e+01 1.232e+04 6.637e+03 0.00
					
			peak_str = ''
			for elem in row['peaks'][8:13]:
				#print elem
				peak_str = peak_str + ' '+ str(elem)
				
				#print peak_str
			output.write('HST ' + str_date_time + '.00 SMS:1101,R1 SMS:1101,R1233937|005 ' + str(t) + ' 5 0 0 0 0' + peak_str + '\n')
	output.close()

if __name__ == "__main__":
	t1 = time.time()
	print "Parsing command line arguments"
	parser = argparse.ArgumentParser(prog = 'parse_sid.py', description = 'Generate DAT files from mass spec sid file', epilog = 'Tested on OSX 10.8.4')
	#parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', default = False, help = 'arg needed for verbose output, default is False')
	#parser.add_argument('-p', '--progress', dest = 'progress', action = 'store_true', default = False, help = 'arg needed for showing progress status, default is False')
	#parser.add_argument('-i', '--input', dest = 'input', default = 'navtokml.ini', help = 'ini file for %(prog)s, default is navtokml.ini')
	parser.add_argument('-d', '--datafile', dest = 'siddatafile', help = 'path to sid files', required = True)
	parser.add_argument('-l', '--savepath', dest = 'savepath', help = 'path of output DAT file', required = True)
	args = parser.parse_args()
	#print "  Verbose          : %r" % args.verbose
	#print "  Progress         : %r" % args.progress
	#print "  Ini file         : %s" % args.input
	print "  sid data file : %s" % args.siddatafile
	print "  output path DAT  : %s" % args.savepath
	peaks = open('peaks.txt').read().split()
	files_dict={}
	
	convert_sid_to_DAT(siddatapath=args.siddatapath,savepath=args.savepath)
	t2 = time.time()
	print 'Reading took %0.6f s' % (t2-t1)