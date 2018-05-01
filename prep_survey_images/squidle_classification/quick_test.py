# take an image and a set of coordinates and
# get image
# extract patch around each coordinate
# run classifier on patch
# uses keras 20171110


import os
import cv2
import argparse
#import requests
from io import BytesIO
from PIL import Image
import urllib2
import urllib
import io
import time
import sys

import numpy as np


# import the necessary packages
#import numpy as np

#import cv2

batch_size = 1

# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    print "getting image"
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # return the image
    return image

#modelFullPath = '/Users/opizarro/kelp-models/inception_v1/all/output_graph.pb'
#modelFullPath = '/Users/opizarro/trained_classifier/output_graph.pb'
#labelsFullPath = '/Users/opizarro/trained_classifier/output_labels.txt'
training_path = '/Users/opizarro/tmp_squidle_classify'


def prep_image(imagePath):


    if not os.path.isfile(imagePath):
        print('File does not exist %s', imagePath)
        return answer

    url = 'file:///' + imagePath
    fd = urllib2.urlopen(url)
    image_file = io.BytesIO(fd.read())
    img = Image.open(image_file)

    x = image.img_to_array(img)

    x = np.expand_dims(x, axis=0)
    return x


def maybe_makedir(dirname, force=False):
  if os.path.isdir(dirname) and not force:
    # You may override by setting force=True.
    #print('%s already present - Skipping making dir' % (dirname))
    pass
  else:
   # print('Making dir %s.' % dirname)
    os.makedirs(dirname)
  return

# get image from http addess
# TODO : check how to get image from http

#response = requests.get(url)
#img = Image.open(BytesIO(response.content))


# get coordinates from list
    # for each point
        # extract patch
        # run the classifier



def classify_patches(image_location,annotations):

    # dimensions expected by InceptionV3
    img_width, img_height = 299, 299


    labelsFullPath = '/Users/opizarro/inceptionv3-3class_labels.txt'
    labelled_annotations = []
    probabilities = []
    # type: (object, object) -> object

    imagename = os.path.basename(image_location)
    start = time.time()
    maybe_makedir(training_path)

    # Creates graph from saved GraphDef.
    #grapht1 = time.time()
    #create_graph()
    #grapht2 = time.time()
    #print('graph creation time {}'.format(grapht2-grapht1))

    #sesst1 = time.time()
    #sess = tf.Session()
    #sesst2 = time.time()
    #print('session activation time {}'.format(sesst2-sesst1))
    # close the graph to any further change (will throw an exception if something is adding nodes)
    # tf.get_default_graph().finalize()


    # extract patches
    # for local or web-based images
    #image = url_to_image(image_location)
    ## for local use
    image = cv2.imread(image_location)
    cv2.imshow("original", image)
    cv2.waitKey(1)
    #
    end = time.time()
    print(end - start)
    return labelled_annotations

if __name__ == "__main__":

    image_location = '/Users/opizarro/data/benthoz_examples/PR_20081008_015947_568_LC16.png'

    samplesize = 25
    coords = np.random.uniform(0,1,(samplesize,2))

    points = [{'x':p[0],'y':p[1]} for p in coords]

    classify_patches(image_location, points)
    #input("press key to exit")
