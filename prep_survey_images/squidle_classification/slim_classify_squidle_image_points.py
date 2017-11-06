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
import sys
sys.path.append('/Users/opizarro/git/workspace/models/slim')
from nets import inception
from preprocessing import inception_preprocessing


# import the necessary packages
#import numpy as np
import urllib2
import urllib
#import cv2
slim = tf.contrib.slim

batch_size = 1
image_size = inception.inception_v1.default_image_size

checkpoints_dir='/Users/opizarro/kelp-models/inception_v1/all'

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
    with tf.Graph().as_default():
        url = 'file:///' + imagePath
        image_string = urllib2.urlopen(url).read()
        image = tf.image.decode_jpeg(image_string, channels=3)
        processed_image = inception_preprocessing.preprocess_image(image, image_size, image_size, is_training=False)
        processed_images  = tf.expand_dims(processed_image, 0)

        # Create the model, use the default arg scope to configure the batch norm parameters.
        with slim.arg_scope(inception.inception_v1_arg_scope()):
            logits, _ = inception.inception_v1(processed_images, num_classes=2, is_training=False)
            probabilities = tf.nn.softmax(logits)

            init_fn = slim.assign_from_checkpoint_fn(
            os.path.join(checkpoints_dir, 'model.ckpt-100000'),
            slim.get_model_variables('InceptionV1'))

        with tf.Session() as sess:
            init_fn(sess)
            np_image, probabilities = sess.run([image, probabilities])
            probabilities = probabilities[0, 0:]
            sorted_inds = [i[0] for i in sorted(enumerate(-probabilities), key=lambda x:x[1])]

        
        predictions = np.squeeze(probabilities)

        top_k = predictions.argsort()[-5:][::-1]  # Getting top 5 predictions
        f = open(labelsFullPath, 'rb')
        lines = f.readlines()
        labels = [str(w).replace("\n", "") for w in lines]
        for node_id in top_k:
            human_string = labels[node_id]
            score = predictions[node_id]
        #print('%s (score = %.5f)' % (human_string, score))

        answer = labels[top_k[0]], predictions[top_k[0]]

        return answer

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
    labelled_annotations = []
    probabilities = []
    # type: (object, object) -> object

    imagename = os.path.basename(image_location)
    start = time.time()
    maybe_makedir(training_path)

    # Creates graph from saved GraphDef.
    grapht1 = time.time()
    create_graph()
    grapht2 = time.time()
    print('graph creation time {}'.format(grapht2-grapht1))

    sesst1 = time.time()
    sess = tf.Session()
    sesst2 = time.time()
    print('session activation time {}'.format(sesst2-sesst1))
    # close the graph to any further change (will throw an exception if something is adding nodes)
    # tf.get_default_graph().finalize()
    cv2.namedWindow( "full" );

    # extract patches

    image = url_to_image(image_location)
    #image = cv2.imread(image_location)

    xdim = image.shape[1]
    ydim = image.shape[0]
    halfsize = (99 - 1) / 2

    # find centre points
    print "finding patches"
    for point in annotations:
        x = int(point['x'] * xdim)
        y = int(point['y'] * ydim)

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

            print "predicting label"
            class_label, prob_class = run_inference_on_image(fullcrop_name,sess)

            if class_label == 'malc':
                boxcolor = (0,255,0)
                labelled_annotations.append(point)
                probabilities.append(prob_class)
            else:
                boxcolor = (255,0,0)

            cv2.rectangle(image, (int(x - hs), int(y - hs)), (int(x + hs), int(y + hs)), boxcolor, 2)
            cv2.circle(image, (x, y), 1, boxcolor)
            cv2.imshow("full", cv2.resize(image, (0, 0), fx=0.5, fy=0.5))
            cv2.imshow("patch", crop_image)
            cv2.waitKey(1)
    tf.reset_default_graph() # IMPORTANT: this keeps the graph from growing
    sess.close()
    end = time.time()
    print(end - start)
    return labelled_annotations, probabilities

if __name__ == "__main__":

    image_location = '/Users/opizarro/data/benthoz_examples/PR_20081008_015947_568_LC16.png'

    samplesize = 50
    points = np.random.uniform(0,1,(samplesize,2))
    classify_patches(image_location, points)
