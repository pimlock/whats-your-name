import logging

logger = logging.getLogger(__name__)


class S3ObjectInfo:
    def __init__(self, bucket_name, object_key, object_size=None):
        self._bucket_name = bucket_name
        self._object_key = object_key

        self._object_size = object_size

    @property
    def bucket_name(self):
        return self._bucket_name

    @property
    def object_key(self):
        return self._object_key

    @property
    def object_size(self):
        return self._object_size

    def __str__(self):
        return '{}/{}'.format(self._bucket_name, self._object_key)

    @staticmethod
    def create_from_s3_notification(record):
        s3_info = record['s3']
        object_info = s3_info['object']

        return S3ObjectInfo(
            s3_info['bucket']['name'],
            object_info['key'],
            object_info['size']
        )
