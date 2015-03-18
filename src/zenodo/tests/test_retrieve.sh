#!/bin/bash

# Retrieve a specific trace file

echo ""
echo "--------"
echo "Python 3"
echo "--------"
echo ""
python3 ../zenodo_retrieve.py -l https://zenodo.org/record/15989/files/scorep-mg.A.64.pjdump
echo ""
echo "--------"
echo "Python 2"
echo "--------"
echo ""
python2 ../zenodo_retrieve.py -l https://zenodo.org/record/15989/files/scorep-mg.A.64.pjdump
