from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import InceptionV3, preprocess_input
import h5py
import os
import cv2
import argparse
from io import BytesIO
from PIL import Image
import urllib2
import urllib
import time
import sys
import numpy as np


from .classifier import BaseClassifier


def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    print "getting image"
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # return the image
    return image


def prep_image(imagePath):

    if not os.path.isfile(imagePath):
        print('File does not exist %s', imagePath)
        return answer

    url = 'file:///' + imagePath
    fd = urllib2.urlopen(url)
    image_file = BytesIO(fd.read())
    img = Image.open(image_file)

    x = image.img_to_array(img)
    #x = preprocess_input(x)
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


class KerasClassifier(BaseClassifier):
    def __init__(self, name, tag_scheme_list, model_path, labels_path, img_width, img_height, probability_threshold=0.5):
        # NB: possible_codes is an additional argument that is only relevant for this model

        BaseClassifier.__init__(self, name, tag_scheme_list, probability_threshold=probability_threshold)

        self.model = load_model(model_path)
        self.model.compile(loss='categorical_crossentropy',
                optimizer='rmsprop',
                metrics=['accuracy'])
        self.patchsize = [img_width,img_height]
        f = open(labels_path, 'rb')
        lines = f.readlines()
        self.labels = [str(w).replace("\n", "") for w in lines]
        print ("labels used by classifier {}".format(self.labels))


        self.tmp_path = '/Users/opizarro/tmp_squidle_classify'
        maybe_makedir(self.tmp_path)

    def predict(self, media_path, points):
        print(" - Working on: {}".format(media_path))
        # Do something with the media file
        image_location = media_path
        imagename = os.path.basename(image_location)
        start = time.time()
        maybe_makedir(self.tmp_path)
        # for local or web-based images
        image = url_to_image(image_location)
        ## for local use
        #image = cv2.imread(image_location)

        xdim = image.shape[1]
        ydim = image.shape[0]
        halfsize = int((max(self.patchsize) - 1) / 2)
        padsize = halfsize
        # pad with appropriate border before feeding to classifier
        reflect101 = cv2.copyMakeBorder(image,padsize,padsize,padsize,padsize,cv2.BORDER_REFLECT_101)

        labeled_points = []
        for p in points:
            #print p
            if p['x'] is None or p['y'] is None:
                continue
            #classifier_code = "MALC"
            #prob = 0.6
            # find centre points and add padding offset
            x = int(round(p['x'] * xdim) + padsize)
            y = int(round(p['y'] * ydim) + padsize)
            crop_image = reflect101[ y - halfsize : y + halfsize, x - halfsize : x + halfsize ]

            # save cropped image in corresponding directory
            crop_name = imagename + '_' + str(x) + '_' + str(y) + '_' + str(halfsize) + '.jpg'
            fullcrop_name = os.path.join(self.tmp_path, crop_name)
            cv2.imwrite(fullcrop_name, crop_image)
            print fullcrop_name
            print "predicting label"

            imkeras = prep_image(fullcrop_name)
            imkeras = preprocess_input(imkeras)
            predictions = self.model.predict(imkeras,verbose=1)
            predictions = predictions[0]

            #print predictions
            #top_k = predictions.argsort()[-3:][::-1]  # prediction in descending probability
            #top_k = predictions.argsort()[-3:][::-1]
            top_k = predictions.argsort() # in increasing order
            #print top_k

            #classifier_code, prob = self.labels[top_k], [round(j,2) for j in predictions[top_k]]
            #labeled_point = self.get_labeled_point(p, classifier_code, prob)
            for i in top_k:
                classifier_code, prob = self.labels[i], round(predictions[i],2)
                labeled_point = self.get_labeled_point(p, classifier_code, prob)
                if labeled_point is not None:
                    labeled_points.append(labeled_point)

        return labeled_points
