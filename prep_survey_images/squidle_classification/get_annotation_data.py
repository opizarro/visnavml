import requests

from io import BytesIO
from classify_squidle_image_points import *


api_base = 'http://203.101.232.29/api'
#api_base = 'http://LOCALHOST:5000/api'
url_annotation_set = '{api_base}/annotation_set/{annotation_set_id}'
url_media_collection = '{api_base}/media?q={{"filters":[{{"name":"media_collections","op":"any","val":{{"name":"id","op":"eq","val":"{media_collection_id}"}}}}]}}&results_per_page=-1'
url_media_annotations = '{api_base}/media-annotations/{media_id}/{annotation_set_id}'


# Define an annotation set that you would like to work with
# TODO: EDIT THIS
annotation_set_id = 18
#annotation_set_id = 63
# /EDIT THIS

# Get annotation set info from the API (HTTP GET REQUEST)
annotation_set = requests.get(url_annotation_set.format(api_base=api_base, annotation_set_id=annotation_set_id)).json()

# From annotation_set, obtain media_collection id and tag_scheme_id
media_collection_id = annotation_set['media_collection_id']
tag_scheme_id = annotation_set['tag_scheme_id']

# Get list of media items for selected annotation set from the API (HTTP GET REQUEST)
media_list = requests.get(url_media_collection.format(api_base=api_base, media_collection_id=media_collection_id)).json()

# loop through media items and do STUFF
for m in media_list['objects']:

    media_path = m['path_best']    # the url of the image (or media item)
    # Get the annotation label locations from the API (HTTP GET REQUEST)
    media_annotations = requests.get(url_media_annotations.format(api_base=api_base, media_id=m['id'], annotation_set_id=annotation_set_id)).json()
    annotations = media_annotations['annotations']

    # TODO: 'media_path' IS THE PATH OF THE IMAGE TO DOWNLOAD! DOWNLOAD IT AND THEN DO STUFF WITH IT!
    # TODO: 'annotations' IS THE LIST OF DICTS THAT CONTAIN ALL THE INFO ABOUT THE POINTS TO ANNOTATE
    # PRINT STUFF - REMOVE THIS!!! THIS IS JUST FOR DEMO
    print "\nImage URL:", media_path



    print "Annotations:", [{'x': a['x'], 'y':a['y'], 'id': a['id']} for a in annotations]

    classify_patches(media_path, annotations)

    # TODO: ONCE YOU HAVE LABELED THE POINTS, YOU WILL NEED TO EXECUTE ANOTHER API CALL TO SAVE THEM
    # YOU WILL PROBABLY ALSO NEED TO GET THE LIST OF CLASSES
