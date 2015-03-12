# Author: Generoso Pagano
# Description: this script publish a file on Zenodo

import requests
import json
import argparse
import os.path

# CONSTANTS
DIR=os.path.dirname(os.path.realpath(__file__)) # Script directory
ZENODO_CONF_FILE=DIR+"/zenodo_conf.json"
DEPOSIT_URL="https://zenodo.org/api/deposit/depositions"

# Load Zenodo User's Configuration
if os.path.isfile(ZENODO_CONF_FILE) == False :
    with open(ZENODO_CONF_FILE, 'wb') as f:
        json.dump({'user': 'Doe, John', 'affiliation':'NASA', 'token': 'this-is-a-dummy-token'}, f)
    print "Configuration file " + ZENODO_CONF_FILE + " not found."
    print "A default one has been created. Please edit the values."
    exit()
f = open(ZENODO_CONF_FILE, 'r')
config = json.load(f)
f.close()
name=config['user']
affiliation=config['affiliation']
token=config['token']

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("filepath", help="File path")
parser.add_argument("-t", "--title", help="File title")
parser.add_argument("-d", "--description", help="File description")
parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
parser.add_argument("-n", "--nopub", help="Create metadata without publishing the file", action="store_true")
args = parser.parse_args()
print args
dry = args.nopub
title=args.title
description=args.description

def zenodo_api_check(url, token):
    """Verify the correct access to the API"""
    r = requests.get("%s?access_token=%s" % (url, token))
    print r.status_code
    if r.status_code != 200:
        print "Impossible to use the REST API. Check the content of " + ZENODO_CONF_FILE + "."
        return False
    print "REST API access: OK"
    return True

print zenodo_api_check(DEPOSIT_URL, token)

exit()

############ PUBLISHING PROCEDURE ############
# After each step, in square brackets I put the reference in the
# [[https://zenodo.org/dev][documentation]].  The format is:
# [Section::Function].

# 1. Create a new deposition resource 
# [Deposition::Create]
data = {"metadata": 
           {
            "title": title, 
            "upload_type": "dataset", 
            "description": description, 
            "communities": [{"identifier": "inria-traces"}],
            "creators": [{"name": name, "affiliation": affiliation}]
           }
       }
headers = {"Content-Type": "application/json"}
r = requests.post("%s?access_token=%s" % (url, TOKEN), data=json.dumps(data), headers=headers)
print "Deposition::Create: " + str(r.status_code)
print r.json()
if r.status_code != 201 :
    print r.json()
    exit()
    
deposition_id = r.json()['id']
print "- Deposition Id: " + str(deposition_id)

# 2. Upload the file 
# [Deposition files::Create(upload)]
data = {'filename': 'myfirstfile.csv'}
files = {'file': open('/home/generoso/myfirstfile.csv', 'rb')}
r = requests.post("%s/%s/files?access_token=%s" % (url, deposition_id, TOKEN), data=data, files=files)
print "Deposition files::Create(upload): " + str(r.status_code)
print r.json()
if r.status_code != 201 :
    print r.json()
    exit()

# 3. Actually publishing the file (AFTER THIS STEP THE FILE CAN NOT BE DELETED!!) 
# [Deposition Actions::Publish]
if dry == False:
    r = requests.post("%s/%s/actions/publish?access_token=%s" % (url, deposition_id, TOKEN))
    print "Deposition Actions::Publish: " + str(r.status_code)
    print r.json()
    print r.json()['record_url']
    print r.json()['id']
    print r.json()['file_id']
    if r.status_code != 202 :
        print r.json()
        exit()
else:
    print "Dry run: don't publish the file"

############ END OF PROCEDURE ############
