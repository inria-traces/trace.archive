# * Author: Generoso Pagano
#
# * Description:
#
# Script to publish a file on Zenodo.
#
# To be abole to publish a file on Zenodo, you need to create an
# account on Zenodo and get a personal token, as explained here:
# https://zenodo.org/dev (search for 'token').
#
# The first time you launch the script, a configuration file will be
# created in the script folder. YOU MUST EDIT THIS FILE, writing the
# correct value of your token.
#
# * Usage:
#
# Use the following command to get the complete list of command line
# arguments:
#
#     python zenodo_publish.py -h
#

import requests
import json
import argparse
import os.path

# Constants
DIR=os.path.dirname(os.path.realpath(__file__)) # Script directory
ZENODO_CONF_FILE=DIR+"/zenodo_conf.json"
DEPOSIT_URL="https://zenodo.org/api/deposit/depositions"
ZENODO_SEPARATOR="* ZENODO content (written automatically)"

# Utilities
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path of the file we want to publish")
    parser.add_argument("orgpath", help="Path of the 'index.org' file in the trace folder")
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

def check_file(path):
    if os.path.isfile(path) == False :
        print("File '"+path+"' does not exist.")
        return False
    return True

def write_link(orgpath, link):
    f = open(orgpath,'r')
    filedata = f.read()
    section = ZENODO_SEPARATOR+"\n"+link+"\n"
    f.close()
    if filedata.find(ZENODO_SEPARATOR) == -1:
        f = open(orgpath,'a')
        f.write("\n" + section)
        f.close()
        print("Zenodo link section not found in '%s': one has been created." % orgpath)
        log(verbose, "--\n" + section + "--" )
    else:
        newdata = filedata.replace(ZENODO_SEPARATOR, ZENODO_SEPARATOR+"\n"+link+"\n")
        f = open(orgpath,'w')
        f.write(newdata)
        f.close()

##################### Input Validation  ######################
# Parse arguments
args = parse_arguments()
filepath=args.filepath
orgpath=args.orgpath
verbose = args.verbose
dry = args.nopub
title=(args.title, os.path.basename(filepath))[args.title==None]
description=(args.description, "File: " + os.path.basename(filepath))[args.description==None]

# Check user configuration
config=load_user_conf()
if config == None:
    print("Configuration file '" + ZENODO_CONF_FILE + "' not found.")
    print("A default one has been created. PLEASE EDIT THE VALUES!")
    exit(1)
else:
    log(verbose, "User configuration found: " + str(config))
name=config['user']
affiliation=config['affiliation']
token=config['token']

# Check REST API
ok, code = zenodo_api_check(DEPOSIT_URL, token)
if ok == False:
    print("Impossible to use the REST API (code " + str(code) + ").")
    print("Check the content of '" + ZENODO_CONF_FILE + "'.")
    exit(1)
else:
    log(verbose, "REST API access: OK")

# Check files
if check_file(filepath) == False :
    exit(1)
if check_file(orgpath) == False :
    exit(1)

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
log(verbose, "Deposition::Create: code " + str(r.status_code))
if r.status_code != 201 :
    print(r.json())
    exit()
    
deposition_id = r.json()['id']
log(verbose, "Deposition Id: " + str(deposition_id))

# 2. Upload the file
# [Deposition files::Create(upload)]
data = {'filename': os.path.basename(filepath)}
files = {'file': open(filepath, 'rb')}
r = requests.post("%s/%s/files?access_token=%s" % (DEPOSIT_URL, deposition_id, token), data=data, files=files)
log(verbose, "Deposition files::Create(upload): code " + str(r.status_code))
if r.status_code != 201 :
    print(r.json())
    exit(1)

# 3. Actually publishing the file (AFTER THIS STEP THE FILE CAN NOT BE DELETED!!) 
# [Deposition Actions::Publish]
if dry == False:
    r = requests.post("%s/%s/actions/publish?access_token=%s" % (DEPOSIT_URL, deposition_id, token))
    if r.status_code != 202 :
        print(r.json())
        exit(1)
    log(verbose, "Deposition Actions::Publish: " + str(r.status_code))
    log(verbose, "Record Url: " + r.json()['record_url'])
    log(verbose, "Deposition Id: " + r.json()['id'])
    zenodo_link=r.json()['record_url'] + "/files/" + os.path.basename(filepath)
    print("File published.")
    write_link(orgpath, zenodo_link)
    print("Zenodo link '" + zenodo_link + "' written in index.org.")
else:
    zenodo_link="https://zenodo.org/record/"+str(deposition_id)+"/files/"+os.path.basename(filepath)
    print("Dry run done. File not actually published.")
    write_link(orgpath, zenodo_link)
    print("Zenodo link '" + zenodo_link + "' written in '" + orgpath + "'")
