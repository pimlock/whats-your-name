import base64
import json
import logging

import boto3
from botocore.exceptions import ClientError

from pmlocek.common.log import setup_lambda_logging
from pmlocek.common.s3 import S3ObjectInfo
from whats_your_name.config import Config
from whats_your_name.html import file_upload_page
from whats_your_name.rekognition import FaceIndexer, FaceRecognizer, FaceCollection
from whats_your_name.sns import AppLinkSender

logger = logging.getLogger(__name__)

_face_collection = None


class Handler:
    def __init__(self, context, config):
        self.context = context
        self.config = config

    def handle(self, event):
        logger.info(event)

        records = event.get('Records', [])
        if records and records[0].get('eventSource') == 'aws:s3':
            return self._process_s3_event(event)

        request_context = event.get('requestContext')
        if request_context:
            if event.get('httpMethod') == 'GET':
                return self._process_website(event)
            elif event.get('httpMethod') == 'POST':
                return self._process_whats_your_name(event)
        else:
            raise Exception('Invalid input!')

    def _process_s3_event(self, event):
        face_collection = self._create_face_collection()
        face_indexer = FaceIndexer(face_collection)

        for record in event.get('Records', []):
            s3_object_info = S3ObjectInfo.create_from_s3_notification(record)
            face_indexer.index_face_from_s3(s3_object_info)

    def _process_send_link(self, event):
        phone_number = event.get('phoneNumber')
        if not phone_number:
            raise Exception('Invalid input: missing "phoneNumber" attribute!')

        app_link_sender = AppLinkSender(boto3.client('sns'), self._app_url(event))
        app_link_sender.send_link_to_phone_number(phone_number)

    def _app_url(self, event):
        return 'https://{}.execute-api.us-east-1.amazonaws.com/Prod'.format(event.get('requestContext').get('apiId'))

    def _process_whats_your_name(self, event):
        face_collection = self._create_face_collection()
        face_recognizer = FaceRecognizer(face_collection)

        image_data = event.get('body', '')
        position = image_data.find('base64,')
        if not image_data or position == -1:
            return {
                'statusCode': '502',
                'body': 'Wrong input!'
            }

        image_data = base64.b64decode(image_data[position + 7:])
        recognized_faces = face_recognizer.recognize_face_from_image(image_data)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'faces': [face.user_id for face in recognized_faces]
            }, separators=(',', ':')),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    def _create_face_collection(self):
        global _face_collection
        if _face_collection is None:
            rekognition = boto3.client('rekognition')
            _face_collection = FaceCollection(rekognition, self.config.face_collection_id)
            try:
                _face_collection.create_collection()
            except ClientError as e:
                if not e.response.get('Error', {}).get('Code') == 'ResourceAlreadyExistsException':
                    logger.exception('Exception when creating Rekognition collection')

        return _face_collection

    def _process_website(self, event):
        html = file_upload_page \
            .replace('<%APP_URL%>', self._app_url(event))

        return {
            'body': html,
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            }
        }


def main(event, context):
    setup_lambda_logging()

    handler = Handler(context, Config.create_from_env())
    return handler.handle(event)
