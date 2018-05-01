import argparse
import sys
import os
import importlib

# import squidlib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from squidleapi.mediadata import SQAPIMediaData
#from classifiers.random_demo import RandomSampleClassifier
from classifiers.keras_classifier import KerasClassifier

# Usage:
# Run from base directory so modules can be located
#    python examples/demo_annotation_algorithm.py --api_key <str:api_token> --asid <int:annotation_set_id> --url http://203.101.232.29/



parser = argparse.ArgumentParser()
parser.add_argument("--api_key", type=str, help="The API key of the user to act as", required=True)
parser.add_argument("--url", type=str, help="The base URL of the server (including http://)", default="http://localhost:5000")
parser.add_argument("--asid", type=str, help="Annotation Set ID")
args = parser.parse_args()



#url = 'http://203.101.232.29'
url = args.url   # testing

api_token = args.api_key  # get api_token from cmd line argument
original_annotation_set_id = args.asid  # get annotation_set_id from cmd line argument
annotation_algorithm_name = "RANDCLASS"

# Initialise module
sqapi = SQAPIMediaData(api_token, url=url)

# Get user information from API key
user = sqapi.get_user()

# Get annotation set info from the API (HTTP GET REQUEST)
original_annotation_set = sqapi.get_annotation_set(original_annotation_set_id)

#print original_annotation_set

# Set some useful variables
media_collection_id = original_annotation_set['media_collection_id']
tag_scheme_id = original_annotation_set['tag_scheme_id']   # this is the ID of the classification scheme for the annotation set

# Get full list of annotation labels for the selected tag_scheme. This may be useful for
# training a classifier, or for manually reconciling classifier labels with labels contained in the system.
tag_scheme_list = sqapi.get_tag_scheme_list(tag_scheme_id)

# Below is similar but is a hierarchical representation of the list of classes, with a bit less info
#tag_scheme_hierarchy = sq.get_tag_scheme_hierarchy(tag_scheme_id)

# Get specific class label (tag_group) info using known tag_group_id. This may be useful if
# you use the options above and have specific IDs for classes contained in the API
#tag_group = sq.get_tag_group(tag_group_id=tag_group_id)


# initialise classifier
# TODO: make a real classifier. Replace this class with a new one in classifier.py module that is an actual real classifier.

#classifier = RandomSampleClassifier("RANDBOT", tag_scheme_list['objects'])
model_path = '/Users/opizarro/inceptionv3-3class_all_params_9820.model'
labels_path = '/Users/opizarro/inceptionv3-3class_labels.txt'
img_width, img_height = 299, 299
prob_th=0.0
classifier = KerasClassifier('Triplebot', tag_scheme_list['objects'], model_path, labels_path, img_width, img_height, probability_threshold=prob_th)
# Create a new annotation set to store classifier suggestions (HTTP POST REQUEST)
# This new annotation set is derived on the previous one. It will be presented as suggestions and is not a
# standalone annotation set
new_annotation_set_name = '['+classifier.name+']> '+original_annotation_set['name']  # name for new annotationset
new_annotation_set = sqapi.new_annotation_set(
    media_collection_id,
    new_annotation_set_name,
    tag_scheme_id,
    user['id'],
    parent_annotation_set_id=original_annotation_set["id"],
    description="Suggested annotations by '"+annotation_algorithm_name+"' for the '"+original_annotation_set['name']+"' annotation set. This is not a standalone annotation set."
)


# Get list of media items for selected annotation set
media_list = sqapi.get_media_list(media_collection_id)

# loop through media items and do STUFF
n = len(media_list['objects'])
i = 0
for m in media_list['objects']:
    i += 1
    print("Item {}/{}".format(i, n))

    # Get the annotation label locations from the API (HTTP GET REQUEST)
    media_annotations = sqapi.get_media_annotations(m['id'], original_annotation_set_id)
    points = media_annotations['annotations']

    # Get labeled annotations from classifier
    labeled_points = classifier.predict(m['path_best'], points)
    print labeled_points
    # Create a new annotation set
    classifier.submit_predictions(labeled_points, new_annotation_set["id"], user['id'], sqapi)

print("DONE!!! Checkout the labels online!")
