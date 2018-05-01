import os
import sys
import traceback
import logging

# import squidlib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from squidleapi.datasources import SQAPIDatasources

logfile = "{}.log".format(os.path.realpath(__file__))
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

url = sys.argv[1]
api_token = sys.argv[2]
sqapi = SQAPIDatasources(api_token=api_token, url=url)

if len(sys.argv) > 3:
    platform = sys.argv[3]  # get url from cmd line argument
else:
    platform = sqapi.select_platform()

campaign_list = sqapi.get_datasource_list(platform['data'])
user = sqapi.get_user()
for c in campaign_list:
    campaign_name = os.path.basename(os.path.normpath(c))
    deployment_list = sqapi.get_datasource_list(platform['data'], urlkey=c)
    for d in deployment_list:
        deployment_name = os.path.basename(os.path.normpath(d))
        try:
            sqapi.import_deployment(platform, user, campaign_name, deployment_name)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            traceback.print_exc()
            print "ERROR DEPLOYMENT:", d
            logging.error(e, exc_info=True)
