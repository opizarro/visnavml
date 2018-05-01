from string import Formatter
import requests
import logging
import os

default_url_params = {
    "url": "http://localhost:5000",
    "api_url": "{url}/api",
    "api_token": "47c896b8fa7b5a92bb560f0428a36fdc4bcc0ad982a86a13009a460d",
    "get_user": '{api_url}/users?q={{"filters":[{{"name":"api_token","op":"eq","val":"{api_token}"}}],"single":true}}'
}
#     "platform": "{api_url}/platform",
#     "campaign": "{api_url}/campaign",
#     "get_campaign": '{campaign}?q={{"filters":[{{"name":"key","op":"==","val":"{campaign_key}"}},{{"name":"user_id","op":"==","val":"{user_id}"}}],"single":true}}',
#     "deployment": "{api_url}/deployment",
#     "get_deployment": '{deployment}?q={{"filters":[{{"name":"key","op":"==","val":"{deployment_key}"}},{{"name":"campaign_id","op":"==","val":"{campaign_id}"}}],"single":true}}',
#     "campaign_file": "{api_url}/campaign_file",
#     "get_campaign_file": '{campaign_file}?q={{"filters":[{{"name":"name","op":"==","val":"{name}"}},{{"name":"campaign_id","op":"==","val":"{campaign_id}"}}],"single":true}}',
#     "save_campaign_file": '{campaign_file}/save',
#     "annotation_set": '{api_url}/annotation_set/{annotation_set_id}',
#     "media_collection": '{api_url}/media?q={{"filters":[{{"name":"media_collections","op":"any","val":{{"name":"id","op":"eq","val":"{media_collection_id}"}}}}]}}&results_per_page=20000',
#     "media_annotations": '{api_url}/media-annotations/{media_id}/{annotation_set_id}',
#     "tag_scheme_list": '{api_url}/tag_group?q={{"filters":[{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}]}}',
#     "tag_scheme_hierarchy": '{api_url}/tag_scheme-tree/{tag_scheme_id}',
#     "tag_group_from_info": '{api_url}/tag_group?q={{"filters":[{{"name":"info","op":"any","val":{{"name":"name","op":"eq","val":"{key}"}}}},{{"name":"info","op":"any","val":{{"name":"value","op":"eq","val":"{value}"}}}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}',
#     "tag_group_from_id": '{api_url}/tag_group/{tag_group_id}',
#     "tag_group_from_name": '{api_url}/tag_group?q={{"filters":[{{"name":"name","op":"eq","val":"{tag_group_name}"}},{{"name":"tag_scheme_id","op":"eq","val":{tag_scheme_id}}}],"single":true}}',
#     "user_from_api_key": '{api_url}/users?q={{"filters":[{{"name":"api_token","op":"eq","val":"{api_token}"}}],"single":true}}',
#     "patch_annotations": '{api_url}/annotation-patch-many?q={{"filters":[{{"name":"id","op":"in","val":{annotation_ids}}}]}}',
#     "post_annotation_set": '{api_url}/annotation_set',
#     "post_annotation": '{api_url}/annotation',
# }


class SQAPI(object):
    url_params = {}

    def __init__(self, api_token, url="http://localhost:5000"):
        self.url_params.update(default_url_params)
        self.url_params["api_token"] = api_token
        self.url_params["url"] = url
        self.api_token = api_token

    def get_user(self):
        user = requests.get(self.get_url("get_user")).json()
        return user

    def get_url(self, key, **dictionary):
        dictionary.update(self.url_params)
        return RecursiveFormat(dictionary)[key]

    def is_valid_file(self, fileurl):
        ret = requests.head(fileurl)
        return (ret.status_code == 200)


class RecursiveFormat:
    def __init__(self, dictionary):
        self.formatter = Formatter()
        self.dictionary = dictionary
        self.substituting = set([])

    def __getitem__(self, key):
        if key in self.substituting:
            raise ValueError("Cyclic reference. Key: %s." % key)
        self.substituting.add(key)
        unsubstitutedval = str(self.dictionary[key])
        substitutedval = self.formatter.vformat(unsubstitutedval, [], self)
        self.substituting.remove(key)
        return substitutedval


