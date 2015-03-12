import requests
import json

# dry run
dry = True

# specific metadata
title="sample title"
description="sample description"

# Personal data
name="Pagano, Generoso"
affiliation="Inria"
# my personal token, created using the web interface
TOKEN="dummy-value" # the real value must be your secret!

# Base upload url (constant)
url="https://zenodo.org/api/deposit/depositions"

# try to access the API (just for testing)
print "Try to access API"
r = requests.get("%s?access_token=%s" % (url, TOKEN))
print r.status_code

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
if r.status_code != 201 :
    print r.json()
    exit()

# 3. Actually publishing the file (AFTER THIS STEP THE FILE CAN NOT BE DELETED!!) 
# [Deposition Actions::Publish]
if dry == False:
    r = requests.post("%s/%s/actions/publish?access_token=%s" % (url, deposition_id, TOKEN))
    print "Deposition Actions::Publish: " + str(r.status_code)
    if r.status_code != 202 :
        print r.json()
        exit()
else:
    print "Dry run: don't publish the file"

############ END OF PROCEDURE ############
