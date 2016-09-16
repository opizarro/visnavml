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
import tensorflow as tf

import time


# import the necessary packages
#import numpy as np
import urllib
#import cv2


# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urllib.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # return the image
    return image


modelFullPath = '/Users/opizarro/trained_classifier/output_graph.pb'
labelsFullPath = '/Users/opizarro/trained_classifier/output_labels.txt'
training_path = '/Users/opizarro/tmp_squidle_classify'

def create_graph():
    """Creates a graph from saved GraphDef file and returns a saver."""
    # Creates graph from saved graph_def.pb.
    with tf.gfile.FastGFile(modelFullPath, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def run_inference_on_image(imagePath,sess):
    answer = None

    if not tf.gfile.Exists(imagePath):
        tf.logging.fatal('File does not exist %s', imagePath)
        return answer

    image_data = tf.gfile.FastGFile(imagePath, 'rb').read()

    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
    predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
    predictions = np.squeeze(predictions)

    top_k = predictions.argsort()[-5:][::-1]  # Getting top 5 predictions
    f = open(labelsFullPath, 'rb')
    lines = f.readlines()
    labels = [str(w).replace("\n", "") for w in lines]
    for node_id in top_k:
        human_string = labels[node_id]
        score = predictions[node_id]
        print('%s (score = %.5f)' % (human_string, score))

    answer = labels[top_k[0]]
    return answer




def maybe_makedir(dirname, force=False):
  if os.path.isdir(dirname) and not force:
    # You may override by setting force=True.
    print('%s already present - Skipping making dir' % (dirname))
  else:
    print('Making dir %s.' % dirname)
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



def classify_patches(image_location,points):
    # type: (object, object) -> object


    imagename = os.path.basename(image_location)


    start = time.time()

    maybe_makedir(training_path)

    # Creates graph from saved GraphDef.
    create_graph()

    sess = tf.Session()


    cv2.namedWindow( "full" );

    # extract patches

    image = url_to_image(image_location)
    #image = cv2.imread(image_location)

    xdim = image.shape[1]
    ydim = image.shape[0]
    halfsize = (99 - 1) / 2
    # find centre points
    for point in points:
        x = int(point[1] * xdim)
        y = int(point[0] * ydim)

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

            answer = run_inference_on_image(fullcrop_name,sess)
            if answer == 'malc':
                boxcolor = (0,255,0)
            else:
                boxcolor = (255,0,0)

            cv2.rectangle(image, (int(x - hs), int(y - hs)), (int(x + hs), int(y + hs)), boxcolor, 2)
            cv2.circle(image, (x, y), 1, boxcolor)
            cv2.imshow("full", cv2.resize(image, (0, 0), fx=0.5, fy=0.5))
            cv2.imshow("patch", crop_image)
            cv2.waitKey(1)



    sess.close()
    end = time.time()
    print(end - start)


if __name__ == "__main__":

    image_location = '/Users/opizarro/data/benthoz_examples/PR_20081008_015947_568_LC16.png'

    samplesize = 50
    points = np.random.uniform(0,1,(samplesize,2))
    classify_patches(image_location, points)