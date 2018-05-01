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
#import io
import time
import sys

import numpy as np



class KerasClassifier():

    model = None
    tag_group_lookup = {}
# arguments to pass when instantiating
    model_path = '/Users/opizarro/inceptionv3-3class_all_params_9820.model'
    labels_path = '/Users/opizarro/inceptionv3-3class_labels.txt'
    img_width, img_height = 299, 299 # dimensions expected by InceptionV3

    def __init__(self, tag_scheme_list, model_path, labels_path, img_width, img_height):
        # create a lookup / hash of the different classifier labels and how they map to the tag_group_ids

        # based on path
        self.model = load_model(model_path)


        self.tmp_path = '/Users/opizarro/tmp_squidle_classify'
        maybe_makedir(self.tmp_path)

        f = open(labels_path, 'rb')
        lines = f.readlines()
        self.labels = [str(w).replace("\n", "") for w in lines]
        print self.labels
        #self.img_width = img_width
        #self.img_height = img_height
        self.patchsize = max(img_width,img_height)



        self.model = load_model(model_path)
        #model = load_model('/Users/opizarro/Downloads/inceptionv3-MALC_9888.model')
        self.model.compile(loss='categorical_crossentropy',
                    optimizer='rmsprop',
                    metrics=['accuracy'])


    def url_to_image(self,url):
        # download the image, convert it to a NumPy array, and then read
        # it into OpenCV format
        print "getting image"
        resp = urllib.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        # return the image
        return image

    def prep_image(self,imagePath):


        if not os.path.isfile(imagePath):
            print('File does not exist %s', imagePath)
            return answer

        url = 'file:///' + imagePath
        fd = urllib2.urlopen(url)
        image_file = io.BytesIO(fd.read())
        img = Image.open(image_file)

        x = image.img_to_array(img)
        #x = preprocess_input(x)
        x = np.expand_dims(x, axis=0)
        return x

    def maybe_makedir(self,dirname, force=False):
      if os.path.isdir(dirname) and not force:
        # You may override by setting force=True.
        #print('%s already present - Skipping making dir' % (dirname))
        pass
      else:
       # print('Making dir %s.' % dirname)
        os.makedirs(dirname)
      return


    def predict(self, media_path, annotations):
        print " - Working on:", media_path
        labeled_annotations = []
        self.model
        # lookup tag_group_id from classification scheme
        #tag_group_id = self.tag_group_lookup["MALC"] # hardcoded
        #classifier_codes, prob_classes = classify_patches(media_path, annotations)
        # extract patches
        # for local or web-based images
        image_location = media_path
        imagename = os.path.basename(image_location)
        image = url_to_image(image_location)
        ## for local use
        #image = cv2.imread(image_location)

        xdim = image.shape[1]
        ydim = image.shape[0]

        halfsize = int((self.patchsize - 1) / 2)
        padsize = halfsize
        # pad with appropriate border before feeding to classifier
        reflect101 = cv2.copyMakeBorder(image,padsize,padsize,padsize,padsize,cv2.BORDER_REFLECT_101)

        # find centre points
        print "finding patches"
        for point in annotations:
            # find centre points and add padding offset
            x = int(round(point['x'] * xdim) + padsize)
            y = int(round(point['y'] * ydim) + padsize)
            hs = halfsize

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
                predictions = self.model.predict(imkeras,verbose=1)
                predictions = predictions[0]

                print predictions
                top_k = predictions.argsort()[-3:][::-1]  # prediction in descending probability
                print top_k

                answer = labels[top_k[0]], predictions[top_k[0]]

                print answer





        for i in range(0, len(annotations)):
            if classifier_codes[i] in self.tag_group_lookup:
                # lookup tag_group_id from classification scheme
                tag_group_id = self.tag_group_lookup[classifier_codes[i]]
                prob = prob_classes[i]
                # append to label list of dicts with random probability
                labeled_annotations.append({
                    "tag_group_id": tag_group_id,
                    "prob": prob,
                    "media_annotation_id": annotations[i]['id']
                })
        return labeled_annotations
