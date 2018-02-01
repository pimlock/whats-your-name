#!/usr/bin/env bash

aws cloudformation deploy \
    --template-file ./packaged-template.yaml \
    --stack-name WhatsYourName \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides FaceImagesBucketName=$FACES_BUCKET_NAME RekognitionCollectionId=$REKOGNITION_COLLECTION_ID