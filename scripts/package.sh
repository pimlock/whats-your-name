#!/usr/bin/env bash

if [ -z ${CODE_DEPLOYMENT_BUCKET+x} ];
then
    echo "You have to set 'CODE_DEPLOYMENT_BUCKET' var first and point it to the bucket where the code will be uploaded."
    exit 1
else
    echo "Code will be uploaded to this bucket: $CODE_DEPLOYMENT_BUCKET"
fi

# cleanup
rm -rf dist
rm -f whats-your-name-package.zip

# create directory for all the code to go to
mkdir dist

# copy source files
rsync -a \
    --prune-empty-dirs \
    --exclude '*.pyc' \
    code/src/ dist/

# copy dependencies
pip install -r requirements.txt
rsync -a \
    --prune-empty-dirs \
    --exclude '*.pyc' \
    --exclude 'pip*' \
    --exclude 'setuptools*' \
    --exclude 'wheel*' \
    --exclude 'boto*' \
    --exclude 'botocore*' \
    --exclude 'docutils*' \
    venv/lib/python3.6/site-packages/ dist/

# create package
pushd .
cd dist
zip -q -r ../whats-your-name-package.zip .
popd

aws cloudformation package \
    --template-file ./template.yaml \
    --s3-bucket $CODE_DEPLOYMENT_BUCKET \
    --output-template-file ./packaged-template.yaml