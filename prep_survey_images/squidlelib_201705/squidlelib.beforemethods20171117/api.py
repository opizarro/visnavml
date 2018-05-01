import requests
import json

# Default number of retries on request.
# The requests library doesn't really make this configurable, nor does it intend to.
# Currently (requests 1.1), the retries count is set to 0. If you really want to set it to a higher value,
# you have to set this globally:
requests.adapters.DEFAULT_RETRIES = 5

class SquidleAPI():
    url_annotation_set = '{api_base}/annotation_set/{annotation_set_id}'
    url_media_collection = '{api_base}/media?q={{"filters":[{{"name":"media_collections","op":"any","val":{{"name":"id","op":"eq","val":"{media_collection_id}"}}}}]}}&results_per_page=20000'
    url_media_annotations = '{api_base}/media-annotations/{media_id}/{annotation_set_id}'
    # get all tag_groups (labels) for given annotation scheme
    url_tag_scheme_list = '{api_base}/tag_group?q={{"filters":[{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}]}}'
    # get hierarchical list of classes
    url_tag_scheme_hierarchy = '{api_base}/tag_scheme-tree/{tag_scheme_id}'
    # lookup tag_group (label) using info property (eg: code, code_short, id or other properties from scheme source...)
    url_tag_group_from_info = '{api_base}/tag_group?q={{"filters":[{{"name":"info","op":"any","val":{{"name":"name","op":"eq","val":"{key}"}}}},{{"name":"info","op":"any","val":{{"name":"value","op":"eq","val":"{value}"}}}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}'
    # get specific tag_group from ID
    url_tag_group_from_id = '{api_base}/tag_group/{tag_group_id}'
    # lookup label using class name
    # eg: tag_group_name='Macroalgae: Large canopy-forming: Brown'
    url_tag_group_from_name = '{api_base}/tag_group?q={{"filters":[{{"name":"name","op":"eq","val":"{tag_group_name}"}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}'
    url_user_from_api_key = '{api_base}/users?q={{"filters":[{{"name":"api_token","op":"eq","val":"{api_token}"}}],"single":true}}'
    # URL for patching the annotations to save labels
    url_patch_annotations = '{api_base}/annotation-patch-many?q={{"filters":[{{"name":"id","op":"in","val":{annotation_ids}}}]}}'

    # create new annotation set
    url_post_annotation_set = '{api_base}/annotation_set'
    # create new annotation
    url_post_annotation = '{api_base}/annotation'

    def __init__(self, api_token, api_base='http://203.101.232.29/api' ):
        self.api_token = api_token
        self.api_base = api_base

    def get_user(self):
        return requests.get(self.url_user_from_api_key.format(api_base=self.api_base, api_token=self.api_token)).json()

    def get_annotation_set(self, annotation_set_id):
        return requests.get(self.url_annotation_set.format(api_base=self.api_base, annotation_set_id=annotation_set_id)).json()

    def new_annotation_set(self, media_collection_id, annotation_set_name, tag_scheme_id, user_id, parent_annotation_set_id=None, description="", params={}, allow_add=False):
        return requests.post(
            self.url_post_annotation_set.format(api_base=self.api_base),
            json.dumps({
                'data': {'allow-add': allow_add, 'params': params},
                'description': description,
                'media_collection_id': media_collection_id,
                'name': annotation_set_name,
                'tag_scheme_id': tag_scheme_id,
                'parent_annotation_set_id': parent_annotation_set_id,
                'user_id': user_id
            }),
            headers={'content-type': 'application/json', 'auth-token': self.api_token}
        ).json()

    def get_media_list(self, media_collection_id):
        # Get list of media items for selected annotation set from the API (HTTP GET REQUEST)
        print "GET:", self.url_media_collection.format(api_base=self.api_base, media_collection_id=media_collection_id)
        media_list = requests.get(self.url_media_collection.format(api_base=self.api_base, media_collection_id=media_collection_id)).json()
        print "Retrieved {} media objects...".format(len(media_list['objects']))
        return media_list

    def get_tag_scheme_list(self, tag_scheme_id):
        # Get full list of annotation labels for the selected tag_scheme from API (HTTP GET REQUEST). This may be useful for
        # training a classifier, or for manually reconciling classifier labels with labels contained in the system.
        return requests.get(self.url_tag_scheme_list.format(api_base=self.api_base, tag_scheme_id=tag_scheme_id)).json()

    def get_tag_scheme_hierarchy(self, tag_scheme_id):
        # Below is similar but is a hierarchical representation of the list of classes, with a bit less info
        return requests.get(self.url_tag_scheme_hierarchy.format(api_base=self.api_base, tag_scheme_id=tag_scheme_id)).json()

    def get_tag_group(self, tag_group_id=None, tag_group_info=None, tag_scheme_id=None, tag_group_name=None):
        if tag_group_id is not None:
            # Get specific class label (tag_group) info using known tag_group_id from API (HTTP GET REQUEST). This may be useful if
            # you use the options above and have specific IDs for classes contained in the API
            return requests.get(self.url_tag_group_from_id.format(api_base=self.api_base, tag_group_id=tag_group_id)).json()
        elif tag_group_info is not None and tag_scheme_id is not None:
            # Get specific class label (tag_group) info using info properties from API (HTTP GET REQUEST)
            return requests.get(self.url_tag_group_from_info.format(api_base=self.api_base, tag_scheme_id=tag_scheme_id, **tag_group_info)).json()
        elif tag_group_name is not None and tag_scheme_id is not None:
            return requests.get(self.url_tag_group_from_name.format(api_base=self.api_base, tag_scheme_id=tag_scheme_id, tag_group_name=tag_group_name)).json()
        else:
            print "TODO: throw proper error! Improper arguments for tag_group_lookup"

    def get_media_annotations(self, media_id, annotation_set_id):
        return requests.get(self.url_media_annotations.format(api_base=self.api_base, media_id=media_id, annotation_set_id=annotation_set_id)).json()

    def new_annotation(self, annotation):
        return requests.post(
            self.url_post_annotation.format(api_base=self.api_base),
            json.dumps(annotation),
            headers={'content-type': 'application/json', 'auth-token': self.api_token}
        ).json()

    def new_annotation_retry(self, annotation, retries):
        retry_count = 0
        while retry_count < retries:
            try:
                retry_count = retry_count+1
                result = requests.post(
                    self.url_post_annotation.format(api_base=self.api_base),
                    json.dumps(annotation),
                    headers={'content-type': 'application/json', 'auth-token': self.api_token}
                ).json()

                break
            except Exception as e:
                print "*** ERROR: Could not create annotation. RETRYING: {}/{}".format(retry_count, retries)
                result = {"status": "error"}
        return result
