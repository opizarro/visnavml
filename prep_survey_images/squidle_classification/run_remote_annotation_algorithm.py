import sys
sys.path.append('/Users/opizarro/git/visnav/prep_survey_images/squidlelib/squidlelib')
from api import SquidleAPI
from classifiers import KelpClassifier
import sys

# Usage:
# Run from base directory so modules can be located
#    python examples/run_remote_annotation_algorithm.py <str:api_token> <int:annotation_set_id>


#api_base = 'http://203.101.232.29/api'
api_base = 'http://192.168.0.111:5000/api'   # testing

#api_token = sys.argv[1]  # get api_token from cmd line argument
#original_annotation_set_id = sys.argv[2]  # get annotation_set_id from cmd line argument

api_token = "245ac56ca914e029a4a85e20ff1a5b70fdaa7a13d7ec0de17ad3dfdf" # ari on his machine
#api_token = "1fb5bac7e8f7f8b189bba22c9c681a0d5f652e9aa4b0b6ad7d7350ef" # opizarro for web version
#api_token = "e3eb9237e12fe3533473d2a28b12bf6d01b24e41099f036ea2bcdd11" # kelpbot online
original_annotation_set_id =  123 #"48" # second set from WA # ""28"first set from WA


annotation_algorithm_name = "KELPBOT"


# Initialise module
sq = SquidleAPI(api_token, api_base=api_base)

# Get user information from API key
user = sq.get_user()


# Get annotation set info from the API (HTTP GET REQUEST)
original_annotation_set = sq.get_annotation_set(original_annotation_set_id)

# Set some useful variables
media_collection_id = original_annotation_set['media_collection_id']
tag_scheme_id = original_annotation_set['tag_scheme_id']   # this is the ID of the classification scheme for the annotation set
new_annotation_set_name = '['+annotation_algorithm_name+']> '+original_annotation_set['name']  # name for new annotationset
user_id = user['id']

# Create a new annotation set to store classifier suggestions (HTTP POST REQUEST)
# This new annotation set is derived on the previous one. It will be presented as suggestions and is not a 
# standalone annotation set
new_annotation_set = sq.new_annotation_set(
    media_collection_id, 
    new_annotation_set_name, 
    tag_scheme_id, 
    user_id,
    description="Suggested annotations by '"+annotation_algorithm_name+"' for the '"+original_annotation_set['name']+"' annotation set. This is not a standalone annotation set."
)


# Get full list of annotation labels for the selected tag_scheme. This may be useful for
# training a classifier, or for manually reconciling classifier labels with labels contained in the system.
tag_scheme_list = sq.get_tag_scheme_list(tag_scheme_id)

# Below is similar but is a hierarchical representation of the list of classes, with a bit less info
#tag_scheme_hierarchy = sq.get_tag_scheme_hierarchy(tag_scheme_id)

# Get specific class label (tag_group) info using known tag_group_id. This may be useful if
# you use the options above and have specific IDs for classes contained in the API
#tag_group = sq.get_tag_group(tag_group_id=tag_group_id)

# Get specific class label (tag_group) info using info properties
#tag_group_info = {'key': 'code', 'value': '80300902'}  # code example (Catami scheme)
#tag_group_info = {'key': 'code_short', 'value': 'MALCB'}  # short code example (Squidle Scheme)
#tag_group_info = {'key': 'code_short', 'value': ' MALCB '}  # short code example (Catami Scheme - has annoying space!)
#tag_group = sq.get_tag_group(tag_group_info=tag_group_info, tag_scheme_id=tag_scheme_id)


# initialise classifier
# TODO: make a real classifier. Replace this class with a new one in classifier.py module that is an actual real classifier.
cl = KelpClassifier(tag_scheme_list['objects'])

# Get list of media items for selected annotation set
media_list = sq.get_media_list(media_collection_id)

# loop through media items and do STUFF
n = len(media_list['objects'])
i = 0
for m in media_list['objects']:
    i += 1
    print "Item {}/{}".format(i, n)

    media_path = m['path_best']    # the url of the image (or media item)

    # Get the annotation label locations from the API (HTTP GET REQUEST)
    media_annotations = sq.get_media_annotations(m['id'], original_annotation_set_id)
    annotations = media_annotations['annotations']

    # Get labeled annotations from classifier
    labeled_annotations = cl.predict(media_path, annotations)

    j = 0
    for ma in labeled_annotations:
        # Create new annotation label
        if ma['prob'] > 0.6:    # if prob is greater than 0.5 make a new annotation label
            j += 1              # counter number of point labeled
            sq.new_annotation({
                "annotation_set_id": new_annotation_set['id'],
                "tag_group_id": ma['tag_group_id'],   # the tag_group to use for this label
                "data": {"probability": ma['prob']},
                "media_annotation_id": ma['media_annotation_id'],
                "user_id": user_id
            })
    print " - Labelled {}/{} points".format(j, len(annotations))
print "DONE!!! Checkout the labels online!"