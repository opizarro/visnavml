import random
import requests
from classify_squidle_image_points import *

api_base = 'http://203.101.232.29/api'
# api_base = 'http://LOCALHOST:5000/api'   # testing
url_annotation_set = '{api_base}/annotation_set/{annotation_set_id}'
url_media_collection = '{api_base}/media?q={{"filters":[{{"name":"media_collections","op":"any","val":{{"name":"id","op":"eq","val":"{media_collection_id}"}}}}]}}&results_per_page=20000'
url_media_annotations = '{api_base}/media-annotations/{media_id}/{annotation_set_id}'
# get all tag_groups (labels) for given annotation scheme
url_tag_scheme_list = '{api_base}/tag_group?q={{"filters":[{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}]}}'
# get hierarchical list of classes
url_tag_scheme_hierarchy = '{api_base}/tag_scheme-tree/{tag_scheme_id}'
# lookup tag_group (label) using info property (eg: code, code_short, id or other properties from scheme source...)
url_tag_group_from_info = '{api_base}/tag_group?q={{"filters":[{{"name":"info","op":"any","val":{{"name":"name","op":"eq","val":"{tag_group_info_key}"}}}},{{"name":"info","op":"any","val":{{"name":"value","op":"eq","val":"{tag_group_info_value}"}}}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}'
# get specific tag_group from ID
url_tag_group_from_id = '{api_base}/tag_group/{tag_group_id}'
# lookup label using class name
# eg: tag_group_name='Macroalgae: Large canopy-forming: Brown'
url_tag_group_from_name = '{api_base}/tag_group?q={{"filters":[{{"name":"name","op":"eq","val":"{tag_group_name}"}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}'

# URL for patching the annotations to save labels
url_patch_annotations = '{api_base}/annotation-patch-many?q={{"filters":[{{"name":"id","op":"in","val":{media_annotation_ids}}}]}}'

# Define an annotation set that you would like to work with
# TODO: EDIT THIS
#annotation_set_id = 18 # Ari's test
annotation_set_id = 28
# annotation_set_id = 64   #localhost
# /EDIT THIS

# Get annotation set info from the API (HTTP GET REQUEST)
annotation_set = requests.get(url_annotation_set.format(api_base=api_base, annotation_set_id=annotation_set_id)).json()

# From annotation_set, obtain media_collection id and tag_scheme_id
media_collection_id = annotation_set['media_collection_id']
tag_scheme_id = annotation_set['tag_scheme_id']   # this is the ID of the classification scheme for the annotation set

# Get full list of annotation labels for the selected tag_scheme from API (HTTP GET REQUEST). This may be useful for
# training a classifier, or for manually reconciling classifier labels with labels contained in the system.
#tag_scheme_list = requests.get(url_tag_scheme_list.format(api_base=api_base, tag_scheme_id=tag_scheme_id)).json()

# Below is similar but is a hierarchical representation of the list of classes, with a bit less info
#tag_scheme_hierarchy = requests.get(url_tag_scheme_hierarchy.format(api_base=api_base, tag_scheme_id=tag_scheme_id)).json()

# Get specific class label (tag_group) info using known label ID from API (HTTP GET REQUEST). This may be useful if you
# use the options above and have specific IDs for classes contained in the API
#tag_group = requests.get(url_tag_group_from_id.format(api_base=api_base, tag_group_id=tag_group_id)).json()

# Get specific class label (tag_group) info using info properties from API (HTTP GET REQUEST)
# tg = {'tag_group_info_key': 'code', 'tag_group_info_value': '80300902'}  # CAAB code example
tg = {'tag_group_info_key': 'code_short', 'tag_group_info_value': 'MALCB'}  # short code example
tag_group = requests.get(url_tag_group_from_info.format(api_base=api_base, tag_scheme_id=tag_scheme_id, **tg)).json()
print tag_group

# Get list of media items for selected annotation set from the API (HTTP GET REQUEST)
print "GET:", url_media_collection.format(api_base=api_base, media_collection_id=media_collection_id)
media_list = requests.get(url_media_collection.format(api_base=api_base, media_collection_id=media_collection_id)).json()
print "Retrieved {} media objects...".format(len(media_list['objects']))

# loop through media items and do STUFF
k = 1
for m in media_list['objects']:
    media_path = m['path_best']    # the url of the image (or media item)
    print "Working on image:", media_path, " iteration: ", k

    # Get the annotation label locations from the API (HTTP GET REQUEST)
    media_annotations = requests.get(url_media_annotations.format(api_base=api_base, media_id=m['id'], annotation_set_id=annotation_set_id)).json()
    annotations = media_annotations['annotations']

    #print "Annotations:", [{'x': a['x'], 'y': a['y'], 'id': a['id']} for a in annotations]
    #print annotations


    # TODO: INSERT CLASSIFIER CODE HERE!

    annotations_to_label, probabilities =classify_patches(media_path, annotations)

    # Get list of annotation ids to label
    # TODO: get these ids from the output of classifier
    # this just gets a random selection of half of the annotations to label.
    #annotations_to_label = random.sample(annotations, int(len(annotations)/2))
    #print annotations_to_label


    media_annotation_ids = [a['id'] for a in annotations_to_label]  # list of IDs to label




    # Set the labels using the API
    payload = '{{"tag_group_id":"{}"}}'.format(tag_group['id'])     # create JSON payload with label id
    #payload = '{"tag_group_id":null}'                              # this deletes/resets labels (if needed)
    requests.patch(                                                 # patch labels
        url_patch_annotations.format(api_base=api_base, media_annotation_ids=media_annotation_ids),
        payload,
        headers={'content-type': 'application/json'}
    )
    k = k+1
print "DONE!!! Checkout the labels online!"