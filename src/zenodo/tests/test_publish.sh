#!/bin/bash

# Test publishing (dry run)
touch index.org

echo ""
echo "--------"
echo "Python 3"
echo "--------"
echo ""
python3 ../zenodo_publish.py -nv -t "Test Trace" -d "This is a test trace." fake.trace index.org
echo ""
echo "--------"
echo "Python 2"
echo "--------"
echo ""
python2 ../zenodo_publish.py -nv -t "Test Trace" -d "This is a test trace." fake.trace index.org
echo ""

rm index.org
