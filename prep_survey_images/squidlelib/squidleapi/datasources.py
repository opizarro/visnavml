# import httplib2
import timeit
from datetime import datetime

#import pandas as pd
#import easygui
import sys

import re
from bs4 import BeautifulSoup
import requests
import os
import xmltodict
import json
import logging
import glob

#from api import get_url, get_user
from api import SQAPI
from ui import UIComponents

#url = 'http://squidle.acfr.usyd.edu.au/images/'

# importdata_pattern = 'https://imos-data.s3-ap-southeast-2.amazonaws.com/?delimiter=/&prefix={prefix}'
# csvfile_pattern = 'https://s3-ap-southeast-2.amazonaws.com/imos-data/IMOS/AUV/auv_viewer_data/csv_outputs/{campaign}/DATA_{campaign}_{deployment}.csv'
# img_pattern = 'http://squidle.acfr.usyd.edu.au/images/{campaign}/{deployment}/images/{imgname}.png'
# thm_pattern = 'https://s3-ap-southeast-2.amazonaws.com/imos-data/IMOS/AUV/auv_viewer_data/thumbnails/{campaign}/{deployment}/i2jpg/{imgname}.jpg'


class SQAPIDatasources(SQAPI):
    url_params = {
        "platform": "{api_url}/platform",
        "campaign": "{api_url}/campaign",
        "get_campaign": '{campaign}?q={{"filters":[{{"name":"key","op":"==","val":"{campaign_key}"}},{{"name":"user_id","op":"==","val":"{user_id}"}}],"single":true}}',
        "deployment": "{api_url}/deployment",
        "get_deployment": '{deployment}?q={{"filters":[{{"name":"key","op":"==","val":"{deployment_key}"}},{{"name":"campaign_id","op":"==","val":"{campaign_id}"}}],"single":true}}',
        "campaign_file": "{api_url}/campaign_file",
        "get_campaign_file": '{campaign_file}?q={{"filters":[{{"name":"name","op":"==","val":"{name}"}},{{"name":"campaign_id","op":"==","val":"{campaign_id}"}}],"single":true}}',
        "save_campaign_file": '{campaign_file}/save',
        "platform_single": "{api_url}/platform/{platform_id}"
    }

    def get_datasource_list(self, platform_data, urlkey=None):
        datasource_type = platform_data['datasource_type']
        if datasource_type == "aws":
            prefix = urlkey if urlkey is not None else platform_data['datasource_prefix']
            url = platform_data['datasource_pattern'].format(prefix=prefix)
            page = requests.get(url).text
            data = xmltodict.parse(page)
            try:
                return [i['Prefix'] for i in data['ListBucketResult']['CommonPrefixes']]
            except Exception:
                return []
        elif datasource_type == "http":
            url = urlkey if urlkey is not None else platform_data['datasource_pattern']
            page = requests.get(url).text
            soup = BeautifulSoup(page, 'html.parser')
            return [url + node.get('href') for node in soup.find_all('a')]  # if node.get('href').endswith(ext)]

        elif datasource_type == "local":
            path = urlkey+"/*" if urlkey is not None else platform_data['datasource_pattern']
            return glob.glob(path)

    def select_platform(self):
        new_opt = "+ NEW PLATFORM"
        edit_opt = "# EDIT PLATFORM"
        del_opt = "x DELETE PLATFORM"
        resp = requests.get(self.get_url("platform")).json()
        platforms = {i["name"]:i for i in resp['objects']}
        key, baskey = self.select_list_gui("Choose a PLATFORM:", platforms.keys() + [new_opt, edit_opt, del_opt])
        if key == new_opt:
            return self.new_platform_gui()
        elif key == edit_opt:
            key, baskey = self.select_list_gui("Choose a PLATFORM to EDIT:", platforms.keys())
            return self.edit_platform_data(platforms[key])
        elif key == del_opt:
            key, baskey = self.select_list_gui("Choose a PLATFORM to DELETE:", platforms.keys())
            self.delete_platform(platforms[key])
            return self.select_platform()
        else:
            return platforms[key]

    def select_list_gui(self, title, optionlist, multi_select=False, min_selection_count=1):
        option = UIComponents.select_list(title, optionlist, multi_select=multi_select, min_selection_count=min_selection_count)
        dirname = os.path.basename(os.path.normpath(option))
        return option, dirname

    def get_create_campaign(self, campaign_key, user_id, platform):
        try:  # try get existing based on name
            url = self.get_url("get_campaign", user_id=str(user_id), campaign_key=campaign_key)
            campaign = requests.get(url).json()
            print "    Found campaign: {}".format(campaign["name"])  # this also checks it was a success
            created = False
        except Exception:  # otherwise, make a new one
            if platform['data']['campaign_name_regex']:
                name_search = re.search(platform['data']['campaign_name_regex'], campaign_key)
                short_name = name_search.group(1) if name_search else campaign_key
            else:
                short_name = campaign_key
            data = {
                'name': short_name,
                'key': campaign_key,
                'user_id': user_id,
                'platform_id': platform['id'],
                'media_path_pattern': platform['data']['media_path_pattern'].format(campaign="{campaign.key}", deployment="{deployment.key}", imgname="{media.key}"),
                'thm_path_pattern': platform['data']['thm_path_pattern'].format(campaign="{campaign.key}", deployment="{deployment.key}", imgname="{media.key}", imgid="{media.id}")
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            campaign = requests.post(self.get_url("campaign"), data=json.dumps(data), headers=headers).json()
            print "    Campaign not found. Created a new one: {}".format(campaign["name"])
            created = True

        return campaign, created

    def get_create_deployment(self, deployment_key, user_id, campaign_id, platform):
        try:  # try get existing based on name
            url = self.get_url("get_deployment", campaign_id=str(campaign_id), deployment_key=deployment_key)
            deployment = requests.get(url).json()
            print "    Found deployment: {}".format(deployment["name"])  # this also checks it was a success
            created = False
        except Exception as e:  # otherwise, make a new one
            if platform['data']['deployment_name_regex']:
                name_search = re.search(platform['data']['deployment_name_regex'], deployment_key)
                short_name = name_search.group(1) if name_search else deployment_key
            else:
                short_name = deployment_key
            #timestamp = "{}".format(datetime.strptime(deployment_key[1:16], "%Y%m%d_%H%M%S"))
            data = {
                'name': short_name,
                'key': deployment_key,
                #'timestamp': timestamp,
                'user_id': user_id,
                'campaign_id': campaign_id
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            deployment = requests.post(self.get_url("deployment"), data=json.dumps(data), headers=headers).json()
            print "    Deployment not found. Created a new one: {}".format(deployment["name"])  # this also checks it was a success
            created = True

        return deployment, created

    def get_create_campaign_file(self, fileurl, user_id, campaign_id):
        data = {
            "fileurl": fileurl,
            "description": "Auto uploaded using '{}' from: {}".format(os.path.basename(__file__), fileurl),
            "user_id": user_id,
            "campaign_id": campaign_id,
            "name": os.path.basename(fileurl)
        }
        try:
            campaign_file = requests.get(self.get_url("get_campaign_file", campaign_id=str(campaign_id), name=data['name'])).json()
            print "    Found campaign_file: {}".format(campaign_file["name"])  # this also checks it was a success
            created = False
        except Exception:
            print "    Uploading datafile: {}".format(fileurl)
            campaign_file = requests.post(self.get_url("save_campaign_file"), data=data).json()
            created = True
        return campaign_file, created

    def run_file_operations(self, platform, campaign_file, deployment):
        print ("    Running file operations")
        file_query = platform['data']['datafile_operations']
        for op in file_query:
            if "operation" in op and op["operation"] == "df_to_dict":
                op["columns"]["deployment_id"] = {"ref": "literal", "value": deployment["id"]}
        query_url = campaign_file["fileurl"] + "?format=text&queryparams=" + json.dumps(file_query)
        return requests.get(self.get_url('url') + query_url).json()

    def import_deployment(self, platform, user, campaign_key, deployment_key):
        status = 0
        print ("Checking deployment: {} > {}".format(campaign_key, deployment_key))

        fileurl = platform["data"]['datafile_pattern'].format(campaign=campaign_key, deployment=deployment_key)
        if self.is_valid_file(fileurl):
            user_id = user['id']  # this also check the above was a success

            # Get campaign
            campaign, new_campaign = self.get_create_campaign(campaign_key, user_id, platform)

            # Upload campaign file
            start_time = timeit.default_timer()
            campaign_file, new_campaign_file = self.get_create_campaign_file(fileurl, user_id, campaign['id'])
            if new_campaign_file:
                logging.info("INFO: Uploaded : {} in {}s".format(fileurl, timeit.default_timer() - start_time))

            deployment, new_deployment = self.get_create_deployment(deployment_key, user_id, campaign['id'], platform)

            if not new_deployment:
                if new_campaign_file:
                    print("    TODO: UPDATE EXISTING DEPLOYMENT WITH NEW FILE")
                else:
                    print("    Deployment and CampaignFile already exists. No work done.")
            else:
                # generate filequery
                start_time = timeit.default_timer()
                resp = self.run_file_operations(platform, campaign_file, deployment)
                logging.info("INFO: Completed fileops on {} in {}s: added (response: {})".format(campaign_file["fileurl"], timeit.default_timer()-start_time, resp))
                print("    Done in {}s: (response: {})".format(timeit.default_timer()-start_time, resp))
                status = 1  # set to 1 to show new deployment was created
        else:
            logging.error("ERROR: File not found: {}".format(fileurl))
            status = -1     # return -1 for error

        return status

    def new_platform(self, name, description, user_id, data):
        payload = {
            "name": name,
            "description": description,
            "user_id": user_id,
            "data": data
        }
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        platform = requests.post(self.get_url("platform"), data=json.dumps(payload), headers=headers).json()
        print ("    Created a new platform: {}".format(platform["name"]))
        sys.stdout.flush()
        return platform

    def edit_platform_data(self, platform):
        # Patch platform
        data = {"data": UIComponents.input_multi("Enter platform data", platform['data'])}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        platform = requests.patch(self.get_url("platform_single", platform_id=platform['id']), data=json.dumps(data), headers=headers).json()
        return platform

    def delete_platform(self, platform):
        # Delete platform
        if raw_input("\n\nAre you 100% certain that you want to delete the {} platform?\nAll deployments and campaigns will also be deleted. \nThis is not reversible. \nIf so, type 'YES'.\n".format(platform['name'])) == "YES":
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.delete(self.get_url("platform_single", platform_id=platform['id']), headers=headers)

    def new_platform_data_gui(self, fieldnames):
        fieldvalues = UIComponents.input_multi("Enter platform data", fieldnames)
        return fieldvalues

    def new_platform_gui(self):
        user = self.get_user()

        datasource_type = UIComponents.select_list("Choose a DATASOURCE TYPE for the PLATFORM:", ["aws", "http", "local"])
        if datasource_type == "aws":
            platform_data = self.new_platform_data_gui(['name', 'description', 'datafile_pattern', 'media_path_pattern', 'thm_path_pattern', 'datasource_pattern', 'datasource_prefix', 'deployment_name_regex', 'campaign_name_regex'])
        elif datasource_type == "http":
            platform_data = self.new_platform_data_gui(['name', 'description', 'datafile_pattern', 'media_path_pattern', 'thm_path_pattern', 'datasource_pattern', 'deployment_name_regex', 'campaign_name_regex'])
        elif datasource_type == "local":
            platform_data = self.new_platform_data_gui(['name', 'description', 'datafile_pattern', 'media_path_pattern', 'thm_path_pattern', 'datasource_pattern', 'deployment_name_regex', 'campaign_name_regex'])

        print platform_data

        platform_data['datafile_operations'] = UIComponents.input_json("File operations (as json)")
        platform_data['datasource_type'] = datasource_type

        name = platform_data.pop('name')
        description = platform_data.pop('description')

        return self.new_platform(name, description, user['id'], platform_data)


if __name__ == "__main__":
    print ("Opening GUI to select dataset...")

    logfile = "{}.log".format(os.path.realpath(__file__))
    logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    url = sys.argv[1]  # get url from cmd line argument
    api_token = sys.argv[2]  # get api_token from cmd line argument

    sqapi = SQAPIDatasources(api_token=api_token, url=url)

    user = sqapi.get_user()
    platform = sqapi.select_platform()

    campaigndir, campaign_key = sqapi.select_list_gui("Choose a CAMPAIGN:", sqapi.get_datasource_list(platform['data']))
    deploymentdir, deployment_key = sqapi.select_list_gui("Choose a DEPLOYMENT:", sqapi.get_datasource_list(platform['data'], urlkey=campaigndir))

    sqapi.import_deployment(platform, user, campaign_key, deployment_key)

