import requests
import json
from api import SQAPI


class SQAPIMediaData(SQAPI):
    url_params = {
        "annotation_set": '{api_url}/annotation_set/{annotation_set_id}',
        "media_collection": '{api_url}/media?q={{"filters":[{{"name":"media_collections","op":"any","val":{{"name":"id","op":"eq","val":"{media_collection_id}"}}}}],"order_by":[{{"field":"timestamp_start","direction":"asc"}}]}}&results_per_page=20000',
        "media_annotations": '{api_url}/media-annotations/{media_id}/{annotation_set_id}',
        "tag_scheme_list": '{api_url}/tag_group?q={{"filters":[{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}]}}&results_per_page=5000',
        "tag_scheme_hierarchy": '{api_url}/tag_scheme-tree/{tag_scheme_id}',
        "tag_group_from_info": '{api_url}/tag_group?q={{"filters":[{{"name":"info","op":"any","val":{{"name":"name","op":"eq","val":"{key}"}}}},{{"name":"info","op":"any","val":{{"name":"value","op":"eq","val":"{value}"}}}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}',
        "tag_group_from_id": '{api_url}/tag_group/{tag_group_id}',
        "tag_group_from_name": '{api_url}/tag_group?q={{"filters":[{{"name":"name","op":"eq","val":"{tag_group_name}"}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}',
        "user_from_api_key": '{api_url}/users?q={{"filters":[{{"name":"api_token","op":"eq","val":"{api_token}"}}],"single":true}}',
        "patch_annotations": '{api_url}/annotation-patch-many?q={{"filters":[{{"name":"id","op":"in","val":{annotation_ids}}}]}}',
        "post_annotation_set": '{api_url}/annotation_set',
        "post_annotation": '{api_url}/annotation'
    }

    def get_annotation_set(self, annotation_set_id):
        print "Getting:", self.get_url("annotation_set", annotation_set_id=annotation_set_id)
        return requests.get(self.get_url("annotation_set", annotation_set_id=annotation_set_id)).json()

    def new_annotation_set(self, media_collection_id, annotation_set_name, tag_scheme_id, user_id, parent_annotation_set_id=None, description="", params={}, allow_add=False):
        return requests.post(
            self.get_url("post_annotation_set"),
            json.dumps({
                'data': {'allow_add': allow_add, 'params': params},
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
        print "GET:", self.get_url("media_collection", media_collection_id=media_collection_id)
        media_list = requests.get(self.get_url("media_collection", media_collection_id=media_collection_id)).json()
        print "Retrieved {} media objects...".format(len(media_list['objects']))
        return media_list

    def get_tag_scheme_list(self, tag_scheme_id):
        # Get full list of annotation labels for the selected tag_scheme from API (HTTP GET REQUEST). This may be useful for
        # training a classifier, or for manually reconciling classifier labels with labels contained in the system.
        return requests.get(self.get_url("tag_scheme_list", tag_scheme_id=tag_scheme_id)).json()

    def get_tag_scheme_hierarchy(self, tag_scheme_id):
        # Below is similar but is a hierarchical representation of the list of classes, with a bit less info
        return requests.get(self.get_url("tag_scheme_hierarchy", tag_scheme_id=tag_scheme_id)).json()

    def get_tag_group(self, tag_group_id=None, tag_group_info=None, tag_scheme_id=None, tag_group_name=None):
        if tag_group_id is not None:
            # Get specific class label (tag_group) info using known tag_group_id from API (HTTP GET REQUEST). This may be useful if
            # you use the options above and have specific IDs for classes contained in the API
            return requests.get(self.get_url("tag_group_from_id", tag_group_id=tag_group_id)).json()
        elif tag_group_info is not None and tag_scheme_id is not None:
            # Get specific class label (tag_group) info using info properties from API (HTTP GET REQUEST)
            return requests.get(self.get_url("tag_group_from_info", tag_scheme_id=tag_scheme_id, **tag_group_info)).json()
        elif tag_group_name is not None and tag_scheme_id is not None:
            return requests.get(self.get_url("tag_group_from_name", tag_scheme_id=tag_scheme_id, tag_group_name=tag_group_name)).json()
        else:
            print "TODO: throw proper error! Improper arguments for tag_group_lookup"

    def get_media_annotations(self, media_id, annotation_set_id):
        return requests.get(self.get_url("media_annotations", media_id=media_id, annotation_set_id=annotation_set_id)).json()

    def new_annotation(self, annotation):
        return requests.post(
            self.get_url("post_annotation"),
            json.dumps(annotation),
            headers={'content-type': 'application/json', 'auth-token': self.api_token}
        ).json()

    def new_annotation_retry(self, annotation, retries=5):
        retry_count = 0
        while retry_count < retries:
            try:
                retry_count = retry_count+1
                result = self.new_annotation(annotation)
                break
            except Exception as e:
                print "*** ERROR: Could not create annotation. RETRYING: {}/{}".format(retry_count, retries)
                result = {"status": "error"}
        return result
