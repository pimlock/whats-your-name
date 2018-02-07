import base64
import json
import logging

import boto3
from botocore.exceptions import ClientError

from pmlocek.common.log import setup_lambda_logging
from pmlocek.common.s3 import S3ObjectInfo
from whats_your_name.config import Config
from whats_your_name.html import file_upload_page
from whats_your_name.rekognition import FaceIndexer, FaceRecognizer, FaceCollection, CelebritiesDetector
from whats_your_name.sns import AppLinkSender

logger = logging.getLogger(__name__)

_face_collection = None
_celebrities_detector = None


class Handler:
    def __init__(self, context, config):
        self.context = context
        self.config = config

    def handle(self, event):
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
        image_data = event.get('body', '')
        position = image_data.find('base64,')
        if not image_data or position == -1:
            return {
                'statusCode': 502,
                'body': 'Wrong input!'
            }

        image_data = base64.b64decode(image_data[position + 7:])
        response = self._recognize_faces(image_data)
        if not response:
            response = self._recognize_celebrities(image_data)
        if not response:
            response = self._create_json_response({})

        return response

    def _recognize_faces(self, image_data):
        face_collection = self._create_face_collection()
        face_recognizer = FaceRecognizer(face_collection)

        recognized_faces = face_recognizer.recognize_face_from_image(image_data)
        if recognized_faces:
            return self._create_json_response({
                'faces': [{
                    'face_id': face.user_id
                } for face in recognized_faces]
            })

    def _recognize_celebrities(self, image_data):
        celebrities = self._create_celebrities_detector().detect_celebrities_from_image_data(image_data)
        if celebrities:
            return self._create_json_response({
                'celebrities': [{
                    'face_id': celebrity.id,
                    'name': celebrity.name,
                    'urls': celebrity.urls
                } for celebrity in celebrities]
            })

    def _create_json_response(self, body_dict, status_code=200):
        return {
            'statusCode': status_code,
            'body': json.dumps(body_dict, separators=(',', ':')),
            'headers': {
                'Content-Type': 'application/json',
            }
        }

    def _create_face_collection(self):
        global _face_collection
        if _face_collection is None:
            _face_collection = FaceCollection(boto3.client('rekognition'), self.config.face_collection_id)
            try:
                _face_collection.create_collection()
            except ClientError as e:
                if not e.response.get('Error', {}).get('Code') == 'ResourceAlreadyExistsException':
                    logger.exception('Exception when creating Rekognition collection')

        return _face_collection

    def _create_celebrities_detector(self):
        global _celebrities_detector
        if _celebrities_detector is None:
            _celebrities_detector = CelebritiesDetector(boto3.client('rekognition'))

        return _celebrities_detector

    def _process_website(self, event):
        return {
            'body': file_upload_page,
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            }
        }


def main(event, context):
    setup_lambda_logging()

    handler = Handler(context, Config.create_from_env())
    return handler.handle(event)
