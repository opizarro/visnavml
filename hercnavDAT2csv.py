#!/usr/bin/env python
#
# Generate csv file from DAT navigation for Hercules
#
# 2011-09-20 SS - created and written
# 2013-07 OP and MJR modified for Sentry mass spec and fluorometer use

import sys
import os
import glob
import argparse
import time
import calendar
from pynmea import nmea
from datetime import datetime
from decimal import Decimal





# Main program

# Set the timestamp format of input logs
dsl_time_format = "%Y/%m/%d %H:%M:%S.%f"

# Manage command line arguments
# Parse ini file
#print "Parsing ini file"
#config = ConfigParser.ConfigParser()
#config.readfp(open(ini_file))

#os.chdir(dvlnavdatapath)


t1 = time.time()
print "Parsing command line arguments"
parser = argparse.ArgumentParser(prog = 'hercnavDAT2csv.py', description = 'Generate csv files from herc NAV data', epilog = 'Tested on OSX 10.8.4')

parser.add_argument('-d', '--datapath', dest = 'dvlnavdatapath', help = 'path of DVLNAV files', required = True)
parser.add_argument('-l', '--savefile', dest = 'savefile', help = 'file (and path) of output csv file. Include extension', required = True)
args = parser.parse_args()

print "  DVLNAV data path : %s" % args.dvlnavdatapath
print "  output path KMLs  : %s" % args.savefile

outfile = open(args.savefile,'w')

	
	
for dvlnavfile in glob.glob(args.dvlnavdatapath+"*.DAT"):
	print "Reading DVLNAV file %s..." % dvlnavfile
	data_fd = open(dvlnavfile)
	content = "Start"
	while (content != "" ):
		content = data_fd.readline()
		# HST 2013/08/02 15:00:01.899 JDS 2013/08/02 15:00:00.573 HERC 27.05529133 -94.93776581 -770.468 586.278 0.650 -0.800 295.930 1267.714 0.000 57747.5 0.5 
		split_string = content.split(' ')
		if len(split_string) > 6:
			
			if (split_string[0] == 'HST') & (split_string[3] == 'JDS') & (split_string[6] == 'HERC'):
				try:
					mytime = datetime.strptime(split_string[4] + " " + split_string[5], dsl_time_format)
					tstring2 = mytime.strftime('%Y,%m,%d,%H,%M,%S.%f')
					tstring = calendar.timegm(mytime.timetuple()) 
					t = Decimal(tstring)
					lat = split_string[7]
					lon = split_string[8]
					x = split_string[9]
					y = split_string[10]
					depth = split_string[14]
					alt = split_string[15]
					unixtime_str =  str(tstring) + '.' + split_string[5].split('.')[1]
					# time output as unix time at start and Y m d H M S 
					tsdata= unixtime_str + ',' + lat + ',' + lon + ',' + x + ',' + y + ',' + depth + ','+ alt + ',' + tstring2 +  '\n'
					#print 'writing ' + tsdata
					outfile.write(tsdata)
				except:
					print 'problem with ' + split_string[4] + " " + split_string[5]
					
						
				
			
				
				
				
# Finished
print "Done"