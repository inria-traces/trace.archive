# * Author: Generoso Pagano
#
# * Description:
#
# Script to download a file from Zenodo.
#
# * Usage:
#
# Use the following command to get the complete list of command line
# arguments:
#
#     python zenodo_retrieve.py -h
#

import requests
import json
import argparse

# Utilities
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--orgpath", help="Path of the 'index.org' file in the trace folder, containing the Zenodo link.")
    parser.add_argument("-l", "--link", help="Zenodo link")
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    parser.add_argument("-n", "--nodownload", help="Do not download the file (dry run).", action="store_true")
    return parser.parse_args()

# TODO size must be read from HTML response
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

