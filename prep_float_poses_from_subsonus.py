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
import shutil, sys, argparse
import pandas as pd
import pymap3d
import numpy as np
from scipy.optimize import least_squares
from scipy import linalg
import matplotlib.pyplot as plt
#import utm


#read in advanced nav csv of time, lat, lon, depth , uncertainty
# read in camera time and depth

# model as constant vx and vy that minimise a robust measure of errors to USBL robust
# calculate positions for camera instants
# export for GIS and metashape use

# min depth, export uncertainties should be optional input args

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



def drift_model(x,t):
	xini = x[0:2]
	v = x[2:4]
	return np.outer(v,t) + np.outer(xini,np.ones(np.shape(t)))

def error_fun(x,t,n,e):
	return np.ravel(drift_model(x,t)-[n,e])


def generate_poses_from_adnav(args):

	# read nav csv
	#renavout = open(args.cam_poses_file,'w')

	# navcsv_file = '/Users/opizarro/SIO_sfm/DEFAULT_lokiOut_TM1.txt'
	# SIO_impath = '/Users/opizarro/SIO_sfm/camB/'
	#SIO_impath = '/media/opizarro/Samsung_T3/chuckFK160407/falkor2016_leg1/survey_20160410_120620_R1922/ABE2P/'
	#navcsv_file = '/media/opizarro/Samsung_T3/chuckFK160407/ROPOS/R1922/Loki/DEFAULT_lokiOut.txt'
	#renavout = open('/media/opizarro/Samsung_T3/chuckFK160407/falkor2016_leg1/survey_20160410_120620_R1922/photoscan/ABE2P_camera_poses.csv','w')


	#
	# nav = collections.OrderedDict()
	#
	# with open(args.navcsv_file) as csvfile:
	# 	nav_fieldnames = ['Unix Time','Microseconds','Remote Address','Remote Latitude', 'Remote Longitude','Remote Down']
	# 	#navfile = csv.DictReader((line.replace('\0','') for line in csvfile), fieldnames = nav_fieldnames)
	# 	navfile = csv.Dictreader
	# 	for row in navfile:
	# 		# timestamp of form YYYY-mm-dd HH:MM:SS.uuu
	# 		#print row['timestamp']
	# 		timestamp_nomsec,msec = string.split(row['timestamp'],'.',2)
	# 		#print timestamp_nomsec
	# 		ttup = time.strptime(timestamp_nomsec, '%Y-%m-%d %H:%M:%S')
	# 		utime = str(calendar.timegm(ttup)) + '.' + msec
	# 		#print utime
	# 		t = utime
	# 		nav[t] = {'lat': row['lat'], 'lon': row['lon'], 'depth': row['depth'], 'hdg': row['hdg'],'pitch': row['pitch'],'roll': row['roll'],'alt': row['alt']}
	# 		#print str(nav[t]) + '\n'

	usbl_df = pd.read_csv(args.navcsv_file)
	print(usbl_df)

	# only consider depths greater than min_depth to estimate velocity
	min_depth = 40

	valid_fixes = usbl_df[(usbl_df['Remote Geodetic Position Valid'] == 1) & (usbl_df['Remote Down'] > min_depth)]
	print(valid_fixes)

	# define local origin as average of valid fixes
	lat = valid_fixes['Remote Latitude'].to_numpy()
	lon  = valid_fixes['Remote Longitude'].to_numpy()
	tabs = valid_fixes['Unix Time'].to_numpy()+valid_fixes['Microseconds'].to_numpy()/1e6
	# first valid fix sets the time base
	t = tabs - tabs[0]
	lat0 = np.average(lat)
	lon0 = np.average(lon)

	# convert to NED
	n,e,d = pymap3d.geodetic2ned(lat, lon, 0, lat0, lon0, 0)
	print("n shape", np.shape(n))
	# initial guess for parameter vector
	x0 = np.array([n[0],e[0],(n[-1]-n[0])/t[-1],(e[-1]-e[0])/t[-1]])

	print(np.shape([n,e]))
	# solve as least squares
	res = least_squares(error_fun, x0, loss='cauchy' , f_scale=10, args = (t, n, e), verbose=2 )

	# estimate uncertainties
	cov = linalg.inv(res.jac.T @ res.jac)
	perr = np.sqrt(np.diag(cov))
	print(perr)

	nfit, efit = drift_model(res.x,t)

	# visualise results
	plt.plot(e,n,'o')
	plt.plot(efit,nfit,'x')
	plt.xlabel('$e$')
	plt.ylabel('$n$')
	plt.show(block=False)


	# read in camera depths and time stamps
	camdepth_df = pd.read_csv(args.camdepthcsv_file)



	zcam = -camdepth_df['depth'].to_numpy()
	tcam = camdepth_df['t'].to_numpy()
	print("tcam ",tcam[0])

	# get estimated float positions for the image timestamps
	ncam, ecam = drift_model(res.x,tcam-tabs[0])


	# convert back to lat lon
	latcam,loncam,hcam = pymap3d.ned2geodetic(ncam,ecam,np.zeros(np.shape(ncam)),lat0,lon0,0)

	# assemble dataframe for export
	zsig=0.05
	xysig=0.5
	zsigvec = zsig*np.ones(np.shape(latcam))
	xysigvec = xysig*np.ones(np.shape(latcam))

	outd = {'t': camdepth_df['t'], 'filename' : camdepth_df['filename'], 'lat': latcam, 'lon': loncam, 'z': zcam, 'xysig': xysigvec, 'zsig': zsigvec }
	camnav_df = pd.DataFrame(outd)

	camnav_df.to_csv(args.outcsv_file)


def main():
# Parse arguments

	parser = argparse.ArgumentParser(description="Script to generate AdNav USBL poses for images from timestamps", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("navcsv_file", help="The full path to the csv nav file for the AdNav Subsonus log.")
	#parser.add_argument("SOI_impath", help="The directory containing images that need poses.")
	parser.add_argument("camdepthcsv_file", help="full path to input csv file with depth and timestamp for each image")
	parser.add_argument("outcsv_file", help="full path to out csv file with lat,lon, depth and timestamp for each image" )
	args = parser.parse_args()

	generate_poses_from_adnav(args)

	# create table with time image name, lat, lon, depth, alt


if __name__== "__main__":
	sys.exit(main())
