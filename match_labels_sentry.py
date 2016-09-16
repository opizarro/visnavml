#! /usr/bin/env python

# Helper script for matching cluster labels to a renav solution.  
#
# Author:   Daniel Steinberg
#           Australian Centre for Field Robotics
# Date:     25/07/2013

import sys, csv, argparse
import renavutils as rutil


def main():
    """ Helper function for matching cluster labels to a renav solution. """

    # Parse arguments
    parser = argparse.ArgumentParser(description="Script for matching cluster \
                labels to renav poses.",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("renavfile", help="The stereo_pose_est.data file for \
            the renav to match the clustering solution to.")
    parser.add_argument("labelfile", help="The orignal cluster labels file.")
    parser.add_argument("matchfile", help="The file to store the aligned "
                        "labels and poses.")
    args = parser.parse_args()

    # Open label file, get information
    labels, ftype = rutil.read_labels(args.labelfile)

    if ftype is 'matched':
        print('This file is already a matched file!')
        return 1

    # Open label file, get information
    renav, _, _, ftype = rutil.read_renav(args.renavfile)

    if ftype is not 'stereo':
        print('Require a stereo+pose_est.data file!')
        return 1

    # Write the header for the output file
    write_header(args.matchfile)

    with open(args.matchfile, 'ab') as f:
        csvwrite = csv.writer(f, delimiter=' ')
        match = 0
        unmatch = 0

        # Make cluster labels into a dictionary for fast indexing
        imlab = dict(zip(labels['grayimage'], labels['label']))

        for i, im in enumerate(renav['rightim']):
            try:
                mlabel = imlab[im]
                csvwrite.writerow((renav['timestamp'][i], renav['rightim'][i], renav['latitude'][i], renav['longitude'][i],renav['Xpos'][i],renav['Ypos'][i],renav['Zpos'][i], mlabel))
                match += 1
            except:
                unmatch += 1

    print("Done! {0} matched and {1} unmatched poses.".format(match, unmatch))
    return 0


def write_header(filepath):
    """ Write header into csv file for field information. """

    headstr = \
"""% IMAGE_LABEL_FILE VERSION 1
%
% Each line of this file lists a single string label for the
% corresponding image, generated for instance by an image clustering
% algorithm.
%
% On each line of the file are 5 items:
%
% 1) Record identifier                - integer value
% 2) Timestamp                        - in seconds
% 3) Left image name                  - string
% 4) Right image name                 - string
% 5) Image label                      - integer value\n"""

    with open(filepath, 'w+') as f:
        f.write(headstr)


if __name__ == "__main__":
    sys.exit(main())
