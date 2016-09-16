#!/usr/bin/env python
# takes a uvflour.txt file from mass spec laptop and generates a DAT-like log with HST 
# once in a DAT file format, it can be read and parsed into kml

# TODO does not deal with non-integer seconds

# example line from Fluorometer
# 17102752,7-17-2013,22:45:52,00.221

import csv
#import sys
import time
#import datetime
import argparse
import calendar

def convert_flr_to_csv(flrfile , outfile):
	
	#data_initial = open(flrfile, "rU")
	#data = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")	
	
	with open(flrfile,'rb') as csvfile:
		# skip first line	
		magic=csvfile.readline()
		flr_fieldnames= ['reading','date','time','conc']
		input_file = csv.DictReader((line.replace('\0','') for line in csvfile), fieldnames=flr_fieldnames, delimiter=',')	
		output = open(outfile,'w')
		skip = 0
		subsample = 0
		for row in input_file:
			#if row.split(',')==3:
			
			if skip == subsample:
				s = row['date'] + ' '+ row['time'] 
				print s
				s_dt = time.strptime(s,"%m-%d-%Y %H:%M:%S")
				utime = calendar.timegm(s_dt)
				#t= time.mktime(s_dt.timetuple())
				
									
				
				# format requires milliseconds
				#str_date_time = s_dt.strftime('%Y/%m/%d %H:%M:%S')+'.00'
	
				
	# desired output format
	# flourometer data
	# HST 2013/07/16 15:35:11.908709 SMS:1101,R1 SMS:1101,R1233937|045 0.0000 0.0000 0.0000 0.0000 avg:2.7124 n-1:2.7129 n-2:2.7136 n-3:2.711
				output.write(str(utime) + ' ' + row['conc'] + '\n')		
				skip = 0
			else:
				skip = skip+1
						
			#except:
		#		print 'problem parsing ' + str(row)
			
	output.close()



if __name__ == "__main__":
	t1 = time.time()
	print "Parsing command line arguments"
	parser = argparse.ArgumentParser(prog = 'parse_fluor.py', description = 'Generate csv files from mass spec fluor file', epilog = 'Tested on OSX 10.8.4')
	
	parser.add_argument('-d', '--datafile', dest = 'flrdatafile', help = 'fluor txt file', required = True)
	parser.add_argument('-l', '--csvfile', dest = 'outfile', help = 'path of output csv file', required = True)
	args = parser.parse_args()
	#print "  Verbose          : %r" % args.verbose
	#print "  Progress         : %r" % args.progress
	#print "  Ini file         : %s" % args.input
	print "  flr data file : %s" % args.flrdatafile
	print "  output csvfile  : %s" % args.outfile
	
	
	convert_flr_to_csv(flrfile=args.flrdatafile,outfile=args.outfile)
	t2 = time.time()
	print 'Reading took %0.6f s' % (t2-t1)