#!/usr/bin/env python
# takes a scc file from Sentry and generates a DAT-like log with HST and SPS lines for the fluorometer and vehicle fixes
# once in a DAT file format, it can be read and parsed into kml
# tested on Sentry data from Tioga trials 15 and 16JUL2013
import csv
import sys
import time
import datetime
with open(sys.argv[1], 'rb') as csvfile:
	magic=csvfile.readline()
	print magic
	if magic.strip('\r\n') != 'scc':
		print 'not scc'
		sys.exit(-1)   
	input_file = csv.DictReader(csvfile, delimiter=' ', quotechar='|')
	output = open(sys.argv[2],'w')
	for row in input_file:
		s = row['yy/mm/dd'] + ' '+ row['hh:nn:ss'] 
		nofrag, frag = s.split('.')
		print nofrag	
		# 20130718 there's a 60 happening in the seconds that breaks this. I've added a try to deal with it temporarily. Check wih Dana that the scc is generated properly
		try:							
			nofrag_dt=datetime.datetime.strptime(nofrag,"%Y/%m/%d %H:%M:%S")
			dt = nofrag_dt.replace(microsecond=int(frag))
			t= time.mktime(dt.timetuple())
			output.write('SPS ' + row['yy/mm/dd'] + ' ' +row['hh:nn:ss'] + ' SPS ' +str(t) + ' ' + row['lat'] + ' ' +row['lon']+ ' '+row['depth'] +' '+  row['lat'] + ' ' +row['lon'] + '1\n')
# flourometer data
# HST 2013/07/16 15:35:11.908709 SMS:1101,R1 SMS:1101,R1233937|045 0.0000 0.0000 0.0000 0.0000 avg:2.7124 n-1:2.7129 n-2:2.7136 n-3:2.711
			output.write('HST ' + row['yy/mm/dd'] + ' ' +row['hh:nn:ss'] + ' SMS:1101,R1 SMS:1101,R1233937|045 0.00 0.00 0.00 0.00 avg:' + row['aux2'] + ' n-1:0 n-2:0 n-3:0\n')
		except:
			print "problem with line", s
output.close()
