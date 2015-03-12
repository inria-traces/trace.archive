# Author: Generoso Pagano
# Description: script to publish a file on Zenodo

import requests
import json
import argparse
import os.path

# Constants
DIR=os.path.dirname(os.path.realpath(__file__)) # Script directory
ZENODO_CONF_FILE=DIR+"/zenodo_conf.json"
DEPOSIT_URL="https://zenodo.org/api/deposit/depositions"

# Utilities
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="File path")
    parser.add_argument("-t", "--title", help="File title")
    parser.add_argument("-d", "--description", help="File description")
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    parser.add_argument("-n", "--nopub", help="Create metadata without publishing the file (dry run)", action="store_true")
    return parser.parse_args()

def zenodo_api_check(url, token):
    """Verify the correct access to the API"""
    r = requests.get("%s?access_token=%s" % (url, token))
    if r.status_code != 200:
        return False, r.status_code
    return True, r.status_code

def load_user_conf():
    """ Load Zenodo User's Configuration"""
    if os.path.isfile(ZENODO_CONF_FILE) == False :
        with open(ZENODO_CONF_FILE, 'wb') as f:
            json.dump({'user': 'Doe, John', 'affiliation':'NASA', 'token': 'this-is-a-dummy-token'}, f)
            return None
    else:
        f = open(ZENODO_CONF_FILE, 'r')
        config = json.load(f)
        f.close()
        return config

def log(do, string):
    if do:
        print(string)


##################### Input Validation  ######################
# Parse arguments
args = parse_arguments()
filepath=args.filepath
verbose = args.verbose
dry = args.nopub
title=(args.title, os.path.basename(filepath))[args.title==None]
description=(args.description, "")[args.description==None]

# Check user configuration
config=load_user_conf()
if config == None:
    print("Configuration file '" + ZENODO_CONF_FILE + "' not found.")
    print("A default one has been created. PLEASE EDIT THE VALUES!")
    exit()
else:
    log(verbose, "User configuration found: " + str(config))
name=config['user']
affiliation=config['affiliation']
token=config['token']

# Check REST API
ok, code = zenodo_api_check(DEPOSIT_URL, token)
if ok == False:
    print("Impossible to use the REST API (Code " + str(code) + ").")
    print("Check the content of '" + ZENODO_CONF_FILE + "'.")
    exit()
else:
    log(verbose, "REST API access: OK")

# Check file
if os.path.isfile(filepath) == False :
    print("File '"+filepath+"' does not exist.")
    exit()
else:
    log(verbose, "File '"+filepath+"' exists.")

##################### PUBLISHING PROCEDURE ######################
# For each step, in square brackets there is the reference in the
# documentation (https://zenodo.org/dev).
# The format is: [Section::Function].

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
r = requests.post("%s?access_token=%s" % (DEPOSIT_URL, token), data=json.dumps(data), headers=headers)
log(verbose, "Deposition::Create: " + str(r.status_code))
if r.status_code != 201 :
    print(r.json())
    exit()
    
deposition_id = r.json()['id']
log(True, "- Deposition Id: " + str(deposition_id))

# 2. Upload the file
# [Deposition files::Create(upload)]
data = {'filename': os.path.basename(filepath)}
files = {'file': open(filepath, 'rb')}
r = requests.post("%s/%s/files?access_token=%s" % (DEPOSIT_URL, deposition_id, token), data=data, files=files)
log(verbose, "Deposition files::Create(upload): " + str(r.status_code))
if r.status_code != 201 :
    print(r.json())
    exit()

# TEST always DRY
dry = True

# 3. Actually publishing the file (AFTER THIS STEP THE FILE CAN NOT BE DELETED!!) 
# [Deposition Actions::Publish]
if dry == False:
    r = requests.post("%s/%s/actions/publish?access_token=%s" % (DEPOSIT_URL, deposition_id, token))
    log(verbose, "Deposition Actions::Publish: " + str(r.status_code))
    log(verbose, r.json())
    print("Record Url: " + r.json()['record_url'])
    print("Deposit Id: " + r.json()['id'])
    if r.status_code != 202 :
        print(r.json())
        exit()
else:
    print("Dry run: don't publish the file")
