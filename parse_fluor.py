#!/usr/bin/env python
# takes a uvflour.txt file from mass spec laptop and generates a DAT-like log with HST 
# once in a DAT file format, it can be read and parsed into kml

# TODO does not deal with non-integer seconds

# example line from Fluorometer
# 17102752,7-17-2013,22:45:52,00.221

import csv
import sys
import time
import datetime
import argparse

def convert_flr_to_DAT(flrfile , DATfile):
	
	#data_initial = open(flrfile, "rU")
	#data = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")	
	
	with open(flrfile,'rb') as csvfile:
		# skip first line	
		magic=csvfile.readline()
		flr_fieldnames= ['reading','date','time','conc']
		input_file = csv.DictReader((line.replace('\0','') for line in csvfile), fieldnames=flr_fieldnames, delimiter=',')	
		output = open(DATfile,'w')
		skip = 0
		subsample = 10
		for row in input_file:
			#if row.split(',')==3:
			try:
				if skip == subsample:
					s = row['date'] + ' '+ row['time'] 
		
					s_dt=datetime.datetime.strptime(s,"%m-%d-%Y %H:%M:%S")
		
					t= time.mktime(s_dt.timetuple())
					# format requires milliseconds
					str_date_time = s_dt.strftime('%Y/%m/%d %H:%M:%S')+'.00'
		
					
		# desired output format
		# flourometer data
		# HST 2013/07/16 15:35:11.908709 SMS:1101,R1 SMS:1101,R1233937|045 0.0000 0.0000 0.0000 0.0000 avg:2.7124 n-1:2.7129 n-2:2.7136 n-3:2.711
					output.write('HST ' + str_date_time + ' SMS:1101,R1 SMS:1101,R1233937|045 0.00 0.00 0.00 0.00 avg:' + row['conc'] + ' n-1:0 n-2:0 n-3:0\n')		
					skip = 0
				else:
					skip = skip+1
						
			except:
				print 'problem parsing ' + str(row)
			
	output.close()



if __name__ == "__main__":
	t1 = time.time()
	print "Parsing command line arguments"
	parser = argparse.ArgumentParser(prog = 'parse_fluor.py', description = 'Generate DAT files from mass spec fluor file', epilog = 'Tested on OSX 10.8.4')
	
	parser.add_argument('-d', '--datafile', dest = 'flrdatafile', help = 'fluor txt file', required = True)
	parser.add_argument('-l', '--DATfile', dest = 'DATfile', help = 'path of output DAT file', required = True)
	args = parser.parse_args()
	#print "  Verbose          : %r" % args.verbose
	#print "  Progress         : %r" % args.progress
	#print "  Ini file         : %s" % args.input
	print "  flr data file : %s" % args.siddatafile
	print "  output path DAT  : %s" % args.savepath
	
	
	convert_flr_to_DAT(flrdatafile=args.flrdatafile,DATfile=args.DATfile)
	t2 = time.time()
	print 'Reading took %0.6f s' % (t2-t1)