import timeit

import schedule
import time
import os
import sys
import traceback
import logging
import argparse

# import squidlib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from squidleapi.datasources import SQAPIDatasources

# setup logfile
logfile = "{}.log".format(os.path.realpath(__file__))
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--api_key", type=str, help="The API key of the user to act as", required=True)
parser.add_argument("--url", type=str, help="The base URL of the server (including http://)", default="http://localhost")
parser.add_argument("--platform", type=str, help="The platform name to use")
parser.add_argument("--verbosity", help="Set the level of verbosity (0,1,2)", action="count", default=1)
parser.add_argument("--runonce", help="No schedule, just run once", action='store_true')
args = parser.parse_args()

# setup api
sqapi = SQAPIDatasources(api_token=args.api_key, url=args.url)
platform = sqapi.select_platform()


def sync_deployments():
    logging.info("*** STARTING SYNCHRONISATION OF DATA FOR PLATFORM: {}".format(platform["name"]))
    campaign_list = sqapi.get_datasource_list(platform['data'])
    user = sqapi.get_user()
    stats = {"deployment_count":0, "deployments_saved":0, "errors":0}
    start_time = timeit.default_timer()
    for c in campaign_list:
        campaign_name = os.path.basename(os.path.normpath(c))
        deployment_list = sqapi.get_datasource_list(platform['data'], urlkey=c)
        for d in deployment_list:
            deployment_name = os.path.basename(os.path.normpath(d))
            try:
                status = sqapi.import_deployment(platform, user, campaign_name, deployment_name)
                stats["deployment_count"] += 1
                stats["deployments_saved"] += 1 if status > 0 else 0
                stats["errors"] += 1 if status < 0 else 0
            except KeyboardInterrupt:
                schedule.CancelJob
                sys.exit()
            except Exception as e:
                traceback.print_exc()
                print "ERROR DEPLOYMENT:", d
                logging.error("ERROR: cannot import {} > {}".format(campaign_name, deployment_name))
                logging.error(e, exc_info=True)

    logging.info("*** ENDING SYNCHRONISATION FOR PLATFORM: {}... Took {}s (stats: {})".format(platform["name"], timeit.default_timer()-start_time, stats))

if __name__ == "__main__":

    if args.runonce:
        print("Running once...")
        sync_deployments()
    else:
        # set to run every sunday at midnight
        print ("Starting scheduler: will run every SUNDAY at 00:00 AEST...")
        schedule.every().sunday.at("14:00").do(sync_deployments)
        #schedule.every(20).seconds.do(sync_deployments)

        while True:
            schedule.run_pending()
            time.sleep(30)   # poll every 30 second increments


