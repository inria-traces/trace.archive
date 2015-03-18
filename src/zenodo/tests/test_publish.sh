#!/bin/bash

# Test publishing (dry run)
touch index.org

python ../zenodo_publish.py -nv -t "Test Trace" -d "This is a test trace." fake.trace index.org

rm index.org
