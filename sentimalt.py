# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 19:37:11 2013

generates an ACFR style stereo_pose_est.data file for imagery collected with sentry 201307

@author: opizarro
"""
import csv
import collections
import os
import glob
import string
import time
import calendar
import bisect
import shutil
import utm

def interp1d(t,x1,x2,y1,y2,z1,z2,a1,a2,t1,t2):
	if t2 != t1:	
		u=(t-t1)/(t2-t1)
	else:
		u=0
	x=x1+u*(x2-x1)
	y=y1+u*(y2-y1)
	z=z1+u*(z2-z1)
	a=a1+u*(a2-a1)
	return (x,y,z,a)



# create table with time image name, lat, lon, depth, alt

# read nav csv


#navcsv_file = '/Users/opizarro/data/sentry201307/git/sentry190_20130801_2136_camint.csv'
#sentry_impath = '/Volumes/SAMSUNG/sentry190raw/IM000/color/'
#ACFR_impath = '/Volumes/SAMSUNG/sentry190raw/ACFR/'
navcsv_file = '/media/data/sentry201307/git/sentry190_20130801_2136_camint.csv'
sentry_impath = '/media/SAMSUNG/sentry190raw/IM000/color/'
ACFR_impath = '/media/SAMSUNG/sentry190raw/ACFR/'
nav = collections.OrderedDict()

with open(navcsv_file) as csvfile:
	nav_fieldnames = ['utime','lat','lon','depth','alt']
	navfile = csv.DictReader((line.replace('\0','') for line in csvfile), fieldnames = nav_fieldnames)
	for row in navfile:
		
		#nav[row['utime']]=[row(['lat']), row('lon'), row('depth'), row('alt') ]
		#print row['lat'], row['lon'], row['depth'], row['alt'] 
		t = row['utime']
		nav[t] = {'lat': row['lat'], 'lon': row['lon'], 'depth': row['depth'], 'alt': row['alt']}
		#print str(nav[t]) + '\n'
	
		

print 'searching ' + os.path.join(sentry_impath,"*.tif")
#os.listdir(sentry_impath)

if not os.path.exists(ACFR_impath):
	os.mkdir(ACFR_impath)
	
recordn = 1
renavout = open('stereo_pose_est.data','w')

for fullimfile in glob.glob(os.path.join(sentry_impath,"*.tif")):
	# generate timestamp from name e.g. sentry.20130731.161028703455.4.tif
	# sentry.YYYYmmDD.HHMMSS.f.N.tif
	impath,imfile = os.path.split(fullimfile)
	#print imfile
	#print string.split(imfile,'.',4)
	veh,imdate,imtime,inum,extension = string.split(imfile,'.',4)
	#print 'vehicle ' + veh + ', date ' + imdate + ', time ' + imtime
	imtime_int = imtime[0:6]
	imtime_msec = imtime[6:]
	ttup = time.strptime(imdate+imtime_int,'%Y%m%d%H%M%S')
	utime = str(calendar.timegm(ttup)) + '.'+ imtime_msec
	
	# find altitude for image
	navkeys = nav.keys()
	ind = bisect.bisect_left(navkeys,utime)
	print 'nearest nav timestamp ' + str(ind)
	print 'nav record ' + str(navkeys[ind])
	# create record for camera with altitude, unixtime, position and ACFR style name
	# of form PR_YYYYmmdd_HHMMSS_sss_RC16.tif
	ACFRname = time.strftime('PR_%Y%m%d_%H%M%S',ttup)
	ACFRname = ACFRname + '_' + imtime_msec[0:3] + '_RC16.tif'
	camline = imfile + ' ' + str(nav[navkeys[ind]] )+ ACFRname + '\n'
	print camline 
	 
	# create a symlink to sentry image using ACFR naming scheme (to test standard tools)
	# for images less than 8m high, create symlink
	
	if float(nav[navkeys[ind]]['alt']) < 8:
		#os.symlink(fullimfile,os.path.join(ACFR_impath,ACFRname))
		#print 'Linking ' + fullimfile + ' to ' + os.path.join(ACFR_impath,ACFRname)
        	#shutil.copyfile(fullimfile,os.path.join(ACFR_impath,ACFRname))
		print 'copying ' + fullimfile + ' to ' + os.path.join(ACFR_impath,ACFRname)
		
		# write out a stereo_nav_file est
	# 	(lat,lon) = utm.to_latlon(Easting, Northing, 15, 'R')
#	utm.from_latlon(51.2, 7.5)
# (395201.3103811303, 5673135.241182375, 32, 'U')
#			renav['record'].append(int(row[0].strip()))
#            renav['timestamp'].append(float(row[1].strip()))
#            renav['latitude'].append(float(row[2].strip()))
#            renav['longitude'].append(float(row[3].strip()))
#            renav['Xpos'].append(float(row[4].strip()))
#            renav['Ypos'].append(float(row[5].strip()))
#            renav['Zpos'].append(float(row[6].strip()))
#            renav['Xang'].append(float(row[7].strip()))
#            renav['Yang'].append(float(row[8].strip()))
#            renav['Zang'].append(float(row[9].strip()))
#
#            if ftype is 'vehicle':
#                renav['altitude'].append(float(row[10].strip()))
#            else:
#                renav['leftim'].append(row[10].strip())
#                renav['rightim'].append(row[11].strip())
#                renav['altitude'].append(float(row[12].strip()))
#                renav['boundrad'].append(float(row[13].strip()))
#                renav['crosspoint'].append(bool(row[14].strip()))
		lat = float(nav[navkeys[ind]]['lat'])
		lon = float(nav[navkeys[ind]]['lon'])
		print 'lat ' + str(lat) + ' lon ' + str(lon)
		Xpos,Ypos,zone,code = utm.from_latlon(lat,lon)
		Zpos = str(-float(nav[navkeys[ind]]['depth']))
		Xang = '0'
		Yang = '0'
		Zang = '0'
		leftimbase,tifext = os.path.splitext(ACFRname)
		leftim = leftimbase + '.png'
		rightim = leftim
		altitude = nav[navkeys[ind]]['alt']
		boundrad = '0'
		crosspoint = '0'
		
		renavline = str(recordn) + ' ' + utime + ' ' + str(lat) + ' ' + str(lon) + ' ' + str(Xpos) + ' ' + str(Ypos) + ' ' + Zpos + ' 0 0 0 ' + leftim + ' ' + rightim + ' ' + altitude + ' 0 0\n'
		renavout.write(renavline)	
		recordn = recordn + 1
			
			
# read images in folder

	# convert name to timestamp

	# find nearest time stamp in nav / interp

	# write out new file

