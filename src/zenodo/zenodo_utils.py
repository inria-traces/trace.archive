#!/usr/bin/env python

"""Common utilities and constants for Zenodo scripts"""

import os.path
import sys

__author__ = "Generoso Pagano"
__email__ = "generoso.pagano@inria.fr"

# Constants
DIR=os.path.dirname(os.path.realpath(__file__)) # Script directory
ZENODO_CONF_FILE=DIR+"/zenodo_conf.json"
DEPOSIT_URL="https://zenodo.org/api/deposit/depositions"
ZENODO_SEPARATOR="* ZENODO content (written automatically)"
COMMUNITY_IDENTIFIER="inria-traces"
PY3 = sys.version > '3'

# Utilities
def log(do, string):
    """ log a string """
    if do:
        print(string)

def check_file(path):
    """ Check if a file exists """
    if os.path.isfile(path) == False :
        print("File '"+path+"' does not exist.")
        return False
    return True

