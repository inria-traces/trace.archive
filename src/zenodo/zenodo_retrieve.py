#!/usr/bin/env python

"""Script to download a file from Zenodo.

Use the following command to get the complete list of command line
arguments:

    python zenodo_retrieve.py -h
"""

import argparse
import json
import re
from urllib import urlretrieve
from zenodo_utils import *

__author__ = "Generoso Pagano"
__email__ = "generoso.pagano@inria.fr"

# Utilities
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-o", "--orgpath", help="Path of the 'index.org' file in the trace folder, containing the Zenodo link.")
    group.add_argument("-l", "--link", help="Zenodo link")
    parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
    parser.add_argument("-n", "--nodownload", help="Do not download the file (dry run).", action="store_true")
    return parser.parse_args()

##################### Input Validation  ######################

# Parse arguments
args = parse_arguments()
orgpath=args.orgpath
link = args.link
verbose = args.verbose
dry = args.nodownload

# Get the link
if link == None and orgpath == None:
    print("Specify the Zenodo link or the 'index.org' path.")
    exit(1)
if link == None:
    if check_file(orgpath) == False:
        exit(1)
    f = open(orgpath,'r')
    filedata = f.read()
    f.close()
    split = filedata.split(ZENODO_SEPARATOR,1)
    if len(split) >= 2 :
        m = re.search("(?P<url>https?://[^\s]+)", split[1])
        if m != None :
            link = m.group("url")
    if link == None:
        print("The file '%s' is not valid. Link not found. Check that the section starting with '%s' actually exists and contains the link." % (orgpath, ZENODO_SEPARATOR));
        exit(1)
        
log(verbose, "Link: " + link)

##################### Download file  ######################

filename=link.split("/")[-1]
log(verbose, "Filename: " + filename)

if dry == False:
    urlretrieve(link, filename)
else:
    print("Dry run done. File not downloaded.")

    
