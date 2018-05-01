#! /usr/bin/env python

# read csv file with poses and labels
# filter by class and depth
# randomly select a subset

import csv
import pandas as pd

#renavfile = '/home/opizarro/Downloads/SS07_tables_with_cluster_id/gbr07_viper_label.csv'
renavfile = '/home/opizarro/Downloads/SS07_tables_with_cluster_id/gbr09_hydro_label.csv'
#r20071011_043724_gbr_10_hydrographers_grid_leg
#r20071012_042111_gbr_11_hydrographers_shoal_sandwaves
#gbr09_hydro_label.csv
#gbr10_hydro_label.csv
#gbr11_hydro_label.csv


# read file
# Open label file, get information
df = pd.read_csv(renavfile, skiprows=25,names=['record','easting','northing','Zpos','altitude','label','leftim','rightim',
                                    'identno','timestamp','Xpos','Ypos','Xang','Yang','Zang','boundrad','crosspoint'])


# select relevant clusters
relevant_set = set((6,7,8,14,17,19,23,27,29,32,33,37,39))

reef = df[df['label'] in relevant_set]

# separate in depth bands
depth_bands = [10,20,30,40,50,60,70,80,90,100,110,120,130,140]

for depth in depth_bands
    reefd[depth] = reef[(reef['Zpos'] < depth) and (reef['Zpos'] >= depth-10) ]
