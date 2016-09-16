#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 11:19:33 2013

@author: opizarro
"""

# launches UDP listener mass_nav_logger.py
# and periodically runs navtokml.py
## to FIX
##***** UDP ports not closing properly
## initial peak file created without kml extension
# add bathy at the start
# update legend depending on stream
# document 
# remove prints
# read ranges for colour bar from ini file
# deal with NaN on mass spec data

# create directories if they don't exist 

import os
import shutil
import time
import subprocess
import simplekml
import argparse
from navtokml import convert_to_kml
from create_legend import MakeLegend



# create kml that points to expected data sources
global pathtokml
# kmls will be stored in this subdir with the main kml being the only one at
# base level. This is so they can be compressed into a kmz


print "Parsing command line arguments"
parser = argparse.ArgumentParser(prog = 'master_vis_auv.py', description = 'Generate DAT from UDP data', epilog = 'Tested on OSX 10.8.4')	
parser.add_argument('-l', '--savefile', dest = 'savefile', help = 'path log file e.g. sentryNNN (extesion added)', required = True)
args = parser.parse_args()
#	
#	print "  output path s  : %s" % args.savepath
#	peaks = open('peaks.txt').read().split()
#	files_dict={}
#	
#	for filename in peaks:
#		files_dict.setdefault(filename + '.kml', open(filename,'w'))
#	convert_to_kml(verbose=args.verbose,progress=args.progress,ini_file=args.input,dvlnavdatapath=args.dvlnavdatapath,savepath=args.savepath,files_dict=files_dict)
#	


datastore='/Users/opizarro/data/visdives/'
#divename='Sentry194'
#divename='Sentry192'
divename  = args.savefile

localpath = os.path.join(datastore,divename)
pathtokml = 'contents/'
kml_writepath = os.path.join(localpath,pathtokml)
#pathtokml = os.getcwd()
dvlnavdatapath = os.path.join(datastore,divename+'_working/')
if not os.path.exists(dvlnavdatapath):
	os.makedirs(dvlnavdatapath)

#logpath = os.path.split(os.path.join(datastore,))

if not os.path.exists(kml_writepath):
	os.makedirs(kml_writepath)


ml=MakeLegend()
ml.create_legend()
#legendname=localpath+pathtokml+'legend.png';
Legendname = os.path.join(kml_writepath,'Legend.png')
ml.pilImgLegend.save(Legendname)

# allow for postprocess data
# I've been assembling a fake .DAT from scc to DAT and mass_spec_mat to DAT

# **** listen to UDP and write to DAT
# this assumes a playback format that is unlikely to be correct
#subprocess.Popen(["python", "mass_nav_logger.py", "mass_nav.DAT"])

kml = simplekml.Kml()


screen = kml.newscreenoverlay(name='Legend')
screen.icon.href = pathtokml + 'legend.png'
screen.overlayxy = simplekml.OverlayXY(x=0,y=1,xunits=simplekml.Units.fraction,
                                       yunits=simplekml.Units.fraction)
screen.screenxy = simplekml.ScreenXY(x=15,y=15,xunits=simplekml.Units.pixel,
                                     yunits=simplekml.Units.insetpixels)
screen.size.x = -1
screen.size.y = -1
screen.size.xunits = simplekml.Units.fraction
screen.size.yunits = simplekml.Units.fraction

# crude way of getting peaks from a file
peakfiles = open('peaks.txt').read().split()
files_dict={}
for filename in peakfiles:
	print 'filename ', filename
	files_dict.setdefault(filename + '.kml', open(filename,'w'))
# peaks for Sentry GM20130728
# 15 17 27 43 78
# for test data peak_labels = ('peak 15','peak 17','peak 27','peak 32')
# for GM201307
#peak_labels = ('peak 15','peak 17','peak 27','peak 43','peak 78')
#ij=0
for peak in files_dict.keys():		
	#peakl = peak_labels[ij]
	peak = os.path.splitext(peak)[0]	
	#peakl = peak	
	print 'peak from file ', peak
	netlink= kml.newnetworklink(name= peak + " vis link")
	netlink.link.href = pathtokml + peak + ".kml"
	#ij=ij+1
	netlink.link.refreshmode = simplekml.RefreshMode.oninterval
	netlink.link.refreshinterval = 30
	
	print 'peak from file ', peak, '_normalized17'
	netlink= kml.newnetworklink(name= peak + '_norm17 vis link')
	netlink.link.href = pathtokml + peak + '_normalized17.kml'
	netlink.link.refreshmode = simplekml.RefreshMode.oninterval
	netlink.link.refreshinterval = 30	
	
# link for vehicle track
netlink= kml.newnetworklink(name= "Sentry track")
netlink.link.href = pathtokml+"line.kml"
netlink.link.refreshmode = simplekml.RefreshMode.oninterval
netlink.link.refreshinterval = 30


netlink= kml.newnetworklink(name= "Fluorometer track")
netlink.link.href = pathtokml+"flr.kml"
netlink.link.refreshmode = simplekml.RefreshMode.oninterval
netlink.link.refreshinterval = 30

# this is for an geotiff underlay. Given that this would not
# be updated during the dive, it makes sense to have it a separate kml/kmz

#netlink= kml.newnetworklink(name= "Bathymetry overlay")
#netlink.link.href = pathtokml+"/doc.kml"

kml.save(os.path.join(localpath,divename + ".kml"))


PIPE = subprocess.PIPE


#os.system("python navtokml.py -d .") 
print 'convert to kml'
#dvlnavdatapath='/Volumes/dvlnav_raw'
#dvlnavdatapath='/Users/opizarro/data/sentry201307/git/testdata'
dvlnavmounted='/Volumes/dvlnav_raw/'
#dvlnavdatapath='/Users/opizarro/data/sentry201307/git/tioga002final/'

#dvlnavdatapath='/Users/opizarro/data/testdata/'
rsync_from_mounted =False

ref_marker ='/Users/opizarro/data/sentry201307/git/circle.png'
print 'Copying marker ' + ref_marker + ' figure to contents dir'
shutil.copy(ref_marker,kml_writepath)
while True:
	#dvlnavdatapath=os.getcwd(),
	if rsync_from_mounted:
		print 'rsyncing'
		subprocess.call(["rsync", "-va","--progress","--include=2013_07_3*.DAT","--exclude=*",dvlnavmounted,dvlnavdatapath])
	
	convert_to_kml(verbose=False,progress=False,ini_file='navtokml.ini',dvlnavdatapath=dvlnavdatapath,savepath=kml_writepath,files_dict=files_dict)
	
	
	#archive_name = datastore+divename
	archive_name = datastore+divename
	root_dir = datastore+divename
	shutil.make_archive(archive_name, 'zip', root_dir)
	
	
	print 'Moving to kmz'
	#shutil.move(archive_name+'.zip',archive_name+'.kmz')
	os.rename(archive_name+'.zip',archive_name+'.kmz')
	
	publish_path = '/Users/opizarro/Dropbox/visdives/'
	shutil.copy(archive_name+'.kmz',publish_path)
	#shutil.copy(archive_name+'/contents/stacked_mass.csv',publish_path)
	print 'waiting ...'
	time.sleep(60)
	
