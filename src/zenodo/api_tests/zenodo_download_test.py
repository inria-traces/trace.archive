# Author: Generoso Pagano
# Description: this is only a sample code to interact with Zenodo using
# the REST API. This code won't work without setting a valid TOKEN.

import requests
import json

def download_file(url, size):    
    filesize_dl = 0
    print "Downloading: %s Bytes: %d" % (filename, filesize)
    u = requests.get(fileurl)
    with open(filename, 'wb') as f:
        for chunk in u.iter_content(chunk_size=8192):
            if chunk: # filter out keep-alive new chunks
                filesize_dl += len(chunk)
                f.write(chunk)
                status = r"%10d  [%3.2f%%]" % (filesize_dl, filesize_dl * 100. / filesize)
                status = status + chr(8)*(len(status)+1)
                print status,

# Personal token
TOKEN="this-is-a-dummy-value"

# Base deposit url (constant)
URL="https://zenodo.org/api/deposit/depositions"

# input
deposition_id="24371"

# Get single file metadata
r = requests.get("%s/%s?access_token=%s" % (URL, deposition_id, TOKEN))
print r.status_code
print r.json()
if r.status_code != 200:
    exit()
record_url=r.json()["record_url"]
filemeta=r.json()["files"][0]
    
# Download the file
filename=filemeta["filename"]
filesize=int(filemeta["filesize"])
fileurl=record_url + "/files/" + filename
download_file(fileurl, filesize)

