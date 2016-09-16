# take an image and a set of coordinates and
# get image
# extract patch around each coordinate
# run classifier on patch


import os
import cv2
import argparse
#import requests
from io import BytesIO
import numpy as np

#response = requests.get(url)
#img = Image.open(BytesIO(response.content))

training_path = '/Users/opizarro/tmp_squidle_classify'

def maybe_makedir(dirname, force=False):
  if os.path.isdir(dirname) and not force:
    # You may override by setting force=True.
    print('%s already present - Skipping making dir' % (dirname))
  else:
    print('Making dir %s.' % dirname)
    os.makedirs(dirname)
  return

maybe_makedir(training_path)

# get image from http addess
# TODO : check how to get image from http
web_location = '/Users/opizarro/data/benthoz_examples/PR_20081008_015947_568_LC16.png'

# get coordinates from list
    # for each point
        # extract patch
        # run the classifier


imagename = os.path.basename(web_location)

samplesize = 100
points = np.random.uniform(0,1,(samplesize,2))

# extract patches
if os.path.isfile(web_location):


    image = cv2.imread(web_location)

    # cv2.imshow("original",image)
    # plt.figure(1)
    # plt.imshow(image)
    # read label
    # print('row label %s') % row[1].code
    # imlabels = string.split(row[1].name,':')
    # imlabel = imlabels[0]

    # print ('entry %s has label %s') % (imagename, imlabel)

    xdim = image.shape[1]
    ydim = image.shape[0]
    halfsize = (99 - 1) / 2
    # find centre points
    for point in points:


        x = round(point[1] * xdim)
        y = round(point[0] * ydim)


        # draw circle
        # cv2.circle(image,(x,y),11,(0,255,0),-1)

        # crop around centre point
        dx = min(min(x, halfsize), min(halfsize, xdim - x))
        dy = min(min(y, halfsize), min(halfsize, ydim - y))
        hs = min(dx, dy)
        # at least 81 pixels across to have some context
        if hs > 40:
            crop_image = image[y - hs:y + hs, x - hs:x + hs]

            # save cropped image in corresponding directory
            crop_name = imagename + '_' + str(x) + '_' + str(y) + '_' + str(halfsize) + '.jpg'
            fullcrop_name = os.path.join(training_path, crop_name)
            cv2.imwrite(fullcrop_name, crop_image)
            cmd="/Users/opizarro/git/tensorflow/bazel-bin/tensorflow/examples/label_image/label_image "
            label_flag = " --labels=/Users/opizarro/trained_classifier/output_labels.txt "
            graph_flag = " --graph=/Users/opizarro/trained_classifier/output_graph.pb "
            output_flag = " --output_layer=final_result "
            image_arg = " --image=" + fullcrop_name
            os.system(cmd + label_flag + graph_flag + output_flag + image_arg )


else:

    print('**** WARNING: could not find image %s') % imagename

# --image=/Users/opizarro/data/benthoz_examples/PR_20081008_015947_568_LC16.png

# classify patches
