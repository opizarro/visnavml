# setup folder with images to process based on inputs
# image superset location directory
# dive name (for output folder)
# start and stop times (to copy relevant images)

# assumes
# tif images
# image names of the form : cIMG-20160410-151519-190120-804.tif

import os
import glob
import shutil
import time
import datetime
import argparse, sys

# test inputs and outputs
#image_location = '/media/opizarro/Samsung_T3/chuckFK160407/falkor2016_leg1/survey_20160410_150946_R1922/camB'
#dive_location = '/media/opizarro/Samsung_T3/chuckFK160407/processedACFR/ABE1/camB'
#start_time_str = '20160410-160819'
#stop_time_str = '20160410-164038'

# Parse arguments
def main():
    parser = argparse.ArgumentParser(description="Script to copy working images for 3D reconstruction.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("image_location", help="The path to images from which a subset is going to be copied.")
    parser.add_argument("dive_location", help="The output path where images are copied")
    parser.add_argument("start_time_str", help="start time string in YYYYmmdd-HHMMSS format")
    parser.add_argument("stop_time_str", help="end time string in YYYYmmdd-HHMMSS format")
    args = parser.parse_args()

    start_utime = time.mktime(datetime.datetime.strptime(args.start_time_str, "%Y%m%d-%H%M%S").timetuple())
    stop_utime = time.mktime(datetime.datetime.strptime(args.stop_time_str, "%Y%m%d-%H%M%S").timetuple())
    # for each image check that time is between limits
    # if it is, copy image to dive_location

    if not os.path.exists(args.dive_location):
        os.makedirs(args.dive_location)
        print("Making output dive folder")

    icounter = 0

    for ipath in glob.glob(os.path.join(args.image_location,'*.tif')):
        cam_time_str = os.path.basename(ipath)[5:20]
        cam_utime = time.mktime(datetime.datetime.strptime(cam_time_str, "%Y%m%d-%H%M%S").timetuple())
        if (cam_utime >= start_utime) and (cam_utime <= stop_utime):
            icounter += 1
            print('copying %s.' % (os.path.basename(ipath)))
    print('copied %d images' % icounter)

if __name__ == "__main__":
    sys.exit(main())
