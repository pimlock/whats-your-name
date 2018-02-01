import os


class Config(object):
    def __init__(self, face_collection_id, faces_bucket_name):
        self._face_collection_id = face_collection_id
        self._faces_bucket_name = faces_bucket_name

    @property
    def face_collection_id(self):
        return self._face_collection_id

    @property
    def face_bucket_name(self):
        return self._faces_bucket_name

    @staticmethod
    def create_from_env():
        return Config(
            os.environ.get('REKOGNITION_COLLECTION_ID'),
            os.environ.get('FACES_BUCKET_NAME')
        )
