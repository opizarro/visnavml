# take an image and a set of coordinates and
# get image
# extract patch around each coordinate
# run classifier on patch
# uses keras 20171110

from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import InceptionV3, preprocess_input
import h5py
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
modelFullPath = '/Users/opizarro/trained_classifier/output_graph.pb'
labelsFullPath = '/Users/opizarro/trained_classifier/output_labels.txt'
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

    model = load_model('/Users/opizarro/inceptionv3-3class_all_params_9820.model')
    #model = load_model('/Users/opizarro/Downloads/inceptionv3-MALC_9888.model')
    model.compile(loss='categorical_crossentropy',
                optimizer='rmsprop',
                metrics=['accuracy'])


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
    image = url_to_image(image_location)
    ## for local use
    #image = cv2.imread(image_location)

    #
      # pad image with reflected data

    xdim = image.shape[1]
    ydim = image.shape[0]
    patchsize = 299
    halfsize = int((patchsize - 1) / 2)
    padsize = halfsize

    reflect101 = cv2.copyMakeBorder(image,padsize,padsize,padsize,padsize,cv2.BORDER_REFLECT_101)

    # find centre points
    print "finding patches"
    for point in annotations:
        # find centre points and add padding offset
        x = int(round(point['x'] * xdim) + padsize)
        y = int(round(point['y'] * ydim) + padsize)
        hs = halfsize
        #print('halfsize %i') % hs
    #    x = int(round(row[1].x*xdim + padsize))
    #    y = int(round(row[1].y*ydim + padsize))

        # crop around centre point
         # check dimensions correpond
        #if xdim != image.shape[1] or ydim !=image.shape[0]:
    #        print('WARNING: actual image size and size in database not consistent')

    # at least 81 pixels across to have some context
        if hs == halfsize:
            crop_image = reflect101[y - hs:y + hs, x - hs:x + hs]

            # save cropped image in corresponding directory
            crop_name = imagename + '_' + str(x) + '_' + str(y) + '_' + str(halfsize) + '.jpg'
            fullcrop_name = os.path.join(training_path, crop_name)
            cv2.imwrite(fullcrop_name, crop_image)
            print fullcrop_name
            print "predicting label"
            imkeras = prep_image(fullcrop_name)
            imkeras = preprocess_input(imkeras)
            predictions = model.predict(imkeras,verbose=1)
            predictions = predictions[0]
            print predictions

            top_k = predictions.argsort()[-3:][::-1]  # Getting top 5 predictions
            print top_k
            f = open(labelsFullPath, 'rb')
            lines = f.readlines()
            labels = [str(w).replace("\n", "") for w in lines]
            print labels
            #for node_id in top_k:
            #    human_string = labels[node_id]
            #    score = predictions[node_id]
                #print('%s (score = %.5f)' % (human_string, score))

            answer = labels[top_k[0]], predictions[top_k[0]]

            print answer[0]
            #print class_val
            #class_label = class_val
            if answer[0] == 'MALC':
                boxcolor = (0,255,0)
                labelled_annotations.append(point)
                print('classified MALC')
                #probabilities.append(prob_class)
            elif answer[0] == 'Substrate':
                boxcolor = (0,0,255)
                labelled_annotations.append(point)
                print('classified Substrate')
            else:
                boxcolor = (255,0,0)
                print('classified Other')

            cv2.rectangle(reflect101, (int(x - hs), int(y - hs)), (int(x + hs), int(y + hs)), boxcolor, 1)
            cv2.circle(reflect101, (x, y), 5, boxcolor,2)
            cv2.imshow("full", cv2.resize(reflect101, (0, 0), fx=0.5, fy=0.5))
            cv2.imshow("patch", crop_image)
            cv2.waitKey(1)

    end = time.time()
    print(end - start)
    return labelled_annotations

if __name__ == "__main__":

    image_location = '/Users/opizarro/data/benthoz_examples/PR_20081008_015947_568_LC16.png'

    samplesize = 50
    coords = np.random.uniform(0,1,(samplesize,2))

    points = [{'x':p[0],'y':p[1]} for p in coords]

    classify_patches(image_location, points)
    input("press key to exit")
