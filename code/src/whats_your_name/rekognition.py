import logging

logger = logging.getLogger(__name__)


class Celebrity(object):
    def __init__(self, face, raw_json):
        self.face = face
        self.raw_json = raw_json

    @property
    def id(self):
        return self.raw_json.get('Id')

    @property
    def name(self):
        return self.raw_json.get('Name')

    @property
    def urls(self):
        return self.raw_json.get('Urls', [])


class Face(object):
    def __init__(self, raw_json):
        self.raw_json = raw_json

    @property
    def user_id(self):
        return self.raw_json['Face'].get('ExternalImageId')

    @property
    def face_id(self):
        return self.raw_json['Face'].get('FaceId')

    @property
    def confidence(self):
        return self.raw_json['Face'].get('Confidence')


class FaceCollection(object):
    def __init__(self, rekognition, collection_id):
        self.rekognition = rekognition
        self.collection_id = collection_id

    def index_face_from_s3(self, s3_object_info, external_id):
        """
        :type external_id: string
        :type s3_object_info: pmlocek.common.s3.S3ObjectInfo
        """
        logger.info('Indexing face from s3 path: %s with externalId: %s', s3_object_info, external_id)
        response = self.rekognition.index_faces(
            CollectionId=self.collection_id,
            ExternalImageId=external_id,
            Image={
                'S3Object': {
                    'Bucket': s3_object_info.bucket_name,
                    'Name': s3_object_info.object_key
                }
            }
        )
        logger.info('Indexed: %s', response)

    def index_face_from_file(self, image_path, external_id):
        logger.info('Indexing face from path: %s for externalId: %s', image_path, external_id)

        with open(image_path, 'rb') as image_file:
            response = self.rekognition.index_faces(
                CollectionId=self.collection_id,
                ExternalImageId=external_id,
                Image={
                    'Bytes': image_file.read()
                }
            )
            logger.info('Indexed: %s', response)

    def detect_faces_from_file(self, image_path):
        logger.info('Detecting faces from image: %s', image_path)
        with open(image_path, 'rb') as image_file:
            return self.detect_faces_from_image_data(image_file.read())

    def detect_faces_from_image_data(self, image_data):
        detected_faces = []
        try:
            response = self.rekognition.search_faces_by_image(
                CollectionId=self.collection_id,
                Image={'Bytes': image_data},
                MaxFaces=2
            )
            face_matches = response.get('FaceMatches', [])
            if face_matches:
                for face_match in face_matches:
                    detected_faces.append(Face(face_match))
            logger.info('Found: %s', response)
        except Exception as e:
            logger.exception('Could not find any faces!')
            logger.info(type(e))

        return detected_faces

    def create_collection(self):
        self.rekognition.create_collection(CollectionId=self.collection_id)


class CelebritiesDetector(object):
    def __init__(self, rekognition):
        self.rekognition = rekognition

    def detect_celebrities_from_image_data(self, image_data):
        detected_celebrities = []
        try:
            response = self.rekognition.recognize_celebrities(
                Image={'Bytes': image_data}
            )
            celebrities = response.get('CelebrityFaces', [])
            if celebrities:
                for celebrity_json in celebrities:
                    detected_celebrities.append(Celebrity(Face(celebrity_json), celebrity_json))
            logger.info('Found: %s', response)
        except Exception as e:
            logger.exception('No celebrities found!')
            logger.info(type(e))

        return detected_celebrities


class FaceIndexer(object):

    def __init__(self, face_collection):
        """
        :type face_collection: FaceCollection
        """
        self.face_collection = face_collection

    def index_face_from_s3(self, s3_object_info):
        """
        :type s3_object_info: pmlocek.common.s3.S3ObjectInfo
        """
        # we assume that name of the object will be an ID
        external_id = s3_object_info.object_key.split('/')[-1].replace('+', '_')
        if '.' in external_id:
            external_id = external_id[:external_id.find('.')]

        return self.face_collection.index_face_from_s3(s3_object_info, external_id)


class FaceRecognizer(object):

    def __init__(self, face_collection):
        """
        :type face_collection: FaceCollection
        """
        self.face_collection = face_collection

    def recognize_face_from_image(self, image_data):
        """
        :type image_data: binary
        """
        return self.face_collection.detect_faces_from_image_data(image_data)
