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


import os
import time
import subprocess
import simplekml
from navtokml import convert_to_kml
from create_legend import MakeLegend

# create kml that points to expected data sources
global pathtokml
pathtokml = 'http://www-personal.acfr.usyd.edu.au/opizarro/tioga002'
#pathtokml = os.getcwd()

ml=MakeLegend()
ml.create_legend()
legendname=os.getcwd()+'/legend.png';
ml.pilImgLegend.save(legendname)

# allow for postprocess data
# I've been assembling a fake .DAT from scc to DAT and mass_spec_mat to DAT

# **** listen to UDP and write to DAT
# this assumes a playback format that is unlikely to be correct
#subprocess.Popen(["python", "mass_nav_logger.py", "mass_nav.DAT"])

kml = simplekml.Kml()


screen = kml.newscreenoverlay(name='Legend')
screen.icon.href = legendname
screen.overlayxy = simplekml.OverlayXY(x=0,y=1,xunits=simplekml.Units.fraction,
                                       yunits=simplekml.Units.fraction)
screen.screenxy = simplekml.ScreenXY(x=15,y=15,xunits=simplekml.Units.pixel,
                                     yunits=simplekml.Units.insetpixels)
screen.size.x = -1
screen.size.y = -1
screen.size.xunits = simplekml.Units.fraction
screen.size.yunits = simplekml.Units.fraction


peakfiles = open('peaks.txt').read().split()
files_dict={}
for filename in peakfiles:
	print 'filename ', filename
	files_dict.setdefault(filename + '.kml', open(filename,'w'))

peak_labels = ('peak15','peak 17','peak 27','peak 32')
ij=0
for peak in files_dict.keys():		
	peakl = peak_labels[ij]
	peak = os.path.splitext(peak)[0]	
	print 'peak from file ', peak
	netlink= kml.newnetworklink(name= peakl + " vis link")
	netlink.link.href = pathtokml +"/"+ peak + ".kml"
	ij=ij+1
	#netlink.link.refreshmode = simplekml.RefreshMode.oninterval
	#netlink.link.refreshinterval = 5
# link for vehicle track
netlink= kml.newnetworklink(name= "Sentry track")
netlink.link.href = pathtokml+"/line.kml"
#netlink.link.refreshmode = simplekml.RefreshMode.oninterval
#netlink.link.refreshinterval = 5


netlink= kml.newnetworklink(name= "Fluorometer track")
netlink.link.href = pathtokml+"/flr.kml"
#netlink.link.refreshmode = simplekml.RefreshMode.oninterval
#netlink.link.refreshinterval = 5

netlink= kml.newnetworklink(name= "Bathymetry overlay")
netlink.link.href = pathtokml+"/l/doc.kml"


kml.save("vislink.kml")



#while True:
	#os.system("python navtokml.py -d .") 
print 'convert to kml'
convert_to_kml(verbose=False,progress=False,ini_file='navtokml.ini',dvlnavdatapath=os.getcwd(),files_dict=files_dict)
time.sleep(2)
	
