# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 19:37:11 2013

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
#import utm

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


# navcsv_file = '/Users/opizarro/SIO_sfm/DEFAULT_lokiOut_TM1.txt'
# SIO_impath = '/Users/opizarro/SIO_sfm/camB/'
SIO_impath = '/media/opizarro/Samsung_T3/chuckFK160407/falkor2016_leg1/survey_20160410_120620_R1922/ABE2P/'
navcsv_file = '/media/opizarro/Samsung_T3/chuckFK160407/ROPOS/R1922/Loki/DEFAULT_lokiOut.txt'
renavout = open('/media/opizarro/Samsung_T3/chuckFK160407/falkor2016_leg1/survey_20160410_120620_R1922/photoscan/ABE2P_camera_poses.csv','w')


nav = collections.OrderedDict()

with open(navcsv_file) as csvfile:
	nav_fieldnames = ['idtag','timestamp','lat','lon','depth','hdg','pitch','roll','forvel','stbvel','dwnvel','alt']
	navfile = csv.DictReader((line.replace('\0','') for line in csvfile), fieldnames = nav_fieldnames)
	for row in navfile:
		# timestamp of form YYYY-mm-dd HH:MM:SS.uuu
		#print row['timestamp']
		timestamp_nomsec,msec = string.split(row['timestamp'],'.',2)
		#print timestamp_nomsec
		ttup = time.strptime(timestamp_nomsec, '%Y-%m-%d %H:%M:%S')
		utime = str(calendar.timegm(ttup)) + '.' + msec
		#print utime
		t = utime
		nav[t] = {'lat': row['lat'], 'lon': row['lon'], 'depth': row['depth'], 'hdg': row['hdg'],'pitch': row['pitch'],'roll': row['roll'],'alt': row['alt']}
		#print str(nav[t]) + '\n'



print 'searching ' + os.path.join(SIO_impath,"*.tif")
#os.listdir(sentry_impath)

recordn = 1
#renavout = open('/Users/opizarro/SIO_sfm/SIO_test_camera_positions.csv','w')


for fullimfile in glob.glob(os.path.join(SIO_impath,"*.tif")):
	# generate timestamp from name e.g. 	cIMG-20160413-065344-783853-153.tif
	# sentry.YYYYmmDD.HHMMSS.f.N.tif
	impath,imfile = os.path.split(fullimfile)
	print imfile
	#print string.split(imfile,'.',4)

	camtype,imdate,imtime,imutime,inum_ext = string.split(imfile,'-',5)
	#print 'vehicle ' + veh + ', date ' + imdate + ', time ' + imtime

	ttup = time.strptime(imdate+imtime,'%Y%m%d%H%M%S')
	utime = str(calendar.timegm(ttup)) + '.'+ imutime

	# find altitude for image
	navkeys = nav.keys()
	ind = bisect.bisect_left(navkeys,utime)
	print 'utime ' + str(utime)
	print 'nearest nav timestamp ' + str(ind)
	print 'nav record ' + str(navkeys[ind])
	# create record for camera with altitude, unixtime, position and ACFR style name
	# of form PR_YYYYmmdd_HHMMSS_sss_RC16.tif
	lat = float(nav[navkeys[ind]]['lat'])
	lon = float(nav[navkeys[ind]]['lon'])
	print 'lat ' + str(lat) + ' lon ' + str(lon)
	#Xpos,Ypos,zone,code = utm.from_latlon(lat,lon)
	Zpos = str(-float(nav[navkeys[ind]]['depth']))
	altitude = nav[navkeys[ind]]['alt']
	hdg = nav[navkeys[ind]]['hdg']
	pitch = nav[navkeys[ind]]['pitch']
	roll = nav[navkeys[ind]]['roll']
	renavline = imfile + ',' + utime + ',' + str(lat) + ',' + str(lon) + ',' + Zpos + ',' + altitude + ',' + hdg + ',' + pitch + ',' + roll + '\n'
	renavout.write(renavline)
	recordn = recordn + 1


# read images in folder

	# convert name to timestamp

	# find nearest time stamp in nav / interp

	# write out new file
