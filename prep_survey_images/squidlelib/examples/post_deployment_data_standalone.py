# import httplib2
import pandas as pd
import easygui
from bs4 import BeautifulSoup
import requests
import os
import xmltodict
import json


#url = 'http://squidle.acfr.usyd.edu.au/images/'

# importdata_pattern = 'https://imos-data.s3-ap-southeast-2.amazonaws.com/?delimiter=/&prefix={prefix}'
# csvfile_pattern = 'https://s3-ap-southeast-2.amazonaws.com/imos-data/IMOS/AUV/auv_viewer_data/csv_outputs/{campaign}/DATA_{campaign}_{deployment}.csv'
# img_pattern = 'http://squidle.acfr.usyd.edu.au/images/{campaign}/{deployment}/images/{imgname}.png'
# thm_pattern = 'https://s3-ap-southeast-2.amazonaws.com/imos-data/IMOS/AUV/auv_viewer_data/thumbnails/{campaign}/{deployment}/i2jpg/{imgname}.jpg'
api_url = "http://localhost:5000/api/"
platform_pattern = "{api_url}platform"
user_pattern = "{api_url}users"

def get_datasource_list(datasource_url, datasource_type):
    if datasource_type == "aws":
        url = datasource_url
        page = requests.get(url).text
        data = xmltodict.parse(page)
        return [i['Prefix'] for i in data['ListBucketResult']['CommonPrefixes']]
    elif datasource_type == "http":
        page = requests.get(datasource_url).text
        soup = BeautifulSoup(page, 'html.parser')
        return [datasource_url + node.get('href') for node in soup.find_all('a')]  # if node.get('href').endswith(ext)]

def aws_to_list(urlpattern, prefix):
    url = urlpattern.format(prefix=prefix)
    page = requests.get(url).text
    data = xmltodict.parse(page)
    return [i['Prefix'] for i in data['ListBucketResult']['CommonPrefixes']]

def http_directory_to_list(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + node.get('href') for node in soup.find_all('a')]  # if node.get('href').endswith(ext)]

def select_platform():
    resp = requests.get(platform_pattern.format(api_url=api_url)).json()
    platforms = {i["name"]:i for i in resp['objects']}
    key, baskey = select_list("Choose a PLATFORM:", "Select an option", platforms.keys())
    return platforms[key]

def select_user():
    resp = requests.get(user_pattern.format(api_url=api_url)).json()
    users = {i["email"]:i for i in resp['objects']}
    key, baskey = select_list("Choose a USER:", "Select an option", users.keys())
    return users[key]


def select_list(*args):
    url = easygui.choicebox(*args)
    dirname = os.path.basename(os.path.normpath(url))
    return url, dirname


def create_deployment(platform, campaign_name, deployment_name):
    # TODO: UPLOAD CSV FILE TO CAMPAIGN AND EXECUTE AS FILEMUNGE OPERATION
    try:  # try get existing based on name
        query = 'q={"filters":[{"name":"key","op":"==","val":"'+deployment_name+'"}],"single":true}'
        url = api_url+'deployment?'+query
        deployment = requests.get(url).json()
        print "Not changing existing deployment: {}".format(deployment["name"])  # this also checks it was a success
    except Exception:
        print "Loading CSV file for", platform['data']['datafile_pattern'].format(campaign=campaign_name, deployment=deployment_name), "..."
        df = pd.read_csv(platform['data']['datafile_pattern'].format(campaign=campaign_name, deployment=deployment_name), skiprows=2)
        media_list = []
        for index, row in df.iterrows():
            media_list.append({
                'key': row['image_filename'],
                'media_type': 'image',
                # 'path': img_pattern.format(campaign=campaign_name, deployment=deployment_name, imgname=row['image_filename']),
                # 'path_thm': thm_pattern.format(campaign=campaign_name, deployment=deployment_name, imgname=row['image_filename']),
                'poses': [{
                    'lat': row['latitude'],
                    'lon': row['longitude'],
                    'alt': row['altitude_sensor'],
                    'dep': row['depth_sensor'],
                    'timestamp': row['time'],
                    'data': [
                        {'name': 'sea_water_temperature', 'value': row['sea_water_temperature']},
                        {'name': 'sea_water_salinity', 'value': row['sea_water_salinity']},
                        {'name': 'chlorophyll_concentration_in_sea_water', 'value': row['chlorophyll_concentration_in_sea_water']},
                        {'name': 'backscattering_ratio', 'value': row['backscattering_ratio']},
                        {'name': 'cluster_tag', 'value': row['cluster_tag']},
                    ]
                }]
            })

        print "TODO: open GUI to select user, for now use hard coded..."
        #user = User.query.filter_by(email="ariell.friedman@gmail.com").first()
        #user = requests.get(api_url+'users?q={"filters":[{"name":"email","op":"==","val":"ariell@greybits.com.au"}],"single":true}').json()
        user = select_user()
        user_id = user['id']  # this also check the above was a success

        print "Saving to Database..."

        # CAMPAIGN
        #   name, path, description, user_id, user, created_at, platform_id, platform
        try:  # try get existing based on name
            query = 'q={"filters":[{"name":"key","op":"==","val":"'+campaign_name+'"}],"single":true}'
            url = api_url+'campaign?'+query
            campaign = requests.get(url).json()
            print "Loaded existing campaign: {}".format(campaign["name"])  # this also checks it was a success
        except Exception:  # otherwise, make a new one
            url = api_url+'campaign'
            data = {
                'name': campaign_name,
                'key': campaign_name,
                'user_id': user_id,
                'platform_id': platform['id'],
                'media_path_pattern': platform['data']['media_path_pattern'].format(campaign="{campaign.key}", deployment="{deployment.key}", imgname="{media.key}"),
                'thm_path_pattern': platform['data']['thm_path_pattern'].format(campaign="{campaign.key}", deployment="{deployment.key}", imgname="{media.key}")
            }
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            campaign = requests.post(url, data=json.dumps(data), headers=headers).json()
            print "Created new campaign:", campaign["name"]

        # DEPLOYMENT
        #   name, path, lat, lon, campaign_id, campaign, user_id, user, timestamp
        print "Attempting upload deployment: ", deployment_name
        url = api_url+'deployment/upload'
        short_name = deployment_name[17:]
        timestamp = deployment_name[1:16]
        data = {'name': short_name, 'key': deployment_name, 'timestamp': timestamp, 'user_id': user_id, 'campaign_id': campaign['id'], 'media': media_list}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        #print media_list[:10], deployment_name, deployment_name, user_id, campaign['id']
        deployment = requests.post(url, data=json.dumps(data), headers=headers).json()
        print "Created new deployment: {} (id: {}) and saved {} media and pose entries".format(deployment["name"], deployment['id'], deployment['media_count'])


if __name__ == "__main__":
    print "Opening GUI to select dataset..."
    platform = select_platform()

    campaigndir, campaign_name = select_list("Choose a CAMPAIGN:", "Select a dataset",
        get_datasource_list(platform['data']['datasource_pattern'].format("IMOS/AUV/"), platform['data']['datasource_type']))
    deploymentdir, deployment_name = select_list("Choose a DEPLOYMENT:", "Select a dataset",
        get_datasource_list(platform['data']['datasource_pattern'].format(campaigndir),platform['data']['datasource_type']))

    # campaigndir, campaign_name = select_list("Choose a CAMPAIGN:", "Select a dataset", aws_to_list(platform['data']['datasource_pattern'], "IMOS/AUV/"))
    # deploymentdir, deployment_name = select_list("Choose a DEPLOYMENT:", "Select a dataset", aws_to_list(platform['data']['datasource_pattern'], campaigndir))
    # campaigndir, campaign_name = select_list("Choose a CAMPAIGN:", "Select a dataset", aws_to_list(importdata_pattern, "IMOS/AUV/"))
    # deploymentdir, deployment_name = select_list("Choose a DEPLOYMENT:", "Select a dataset", aws_to_list(importdata_pattern, campaigndir))
    # campaigndir, campaign = select_directory("Choose a CAMPAIGN:", "Select a dataset", http_directory_to_list(url))
    # deploymentdir, deployment = select_directory("Choose a DEPLOYMENT:", "Select a dataset", http_directory_to_list(campaigndir))

    create_deployment(platform, campaign_name, deployment_name)

