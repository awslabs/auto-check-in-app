import datetime, hashlib, hmac
import cv2
import requests
import math
import getpass
import boto3
from botocore.exceptions import ClientError

from video_capture import VideoCapture
from detector import Detector
from viewer import Viewer


class Controller(object):

    def __init__(self, env, video_device):
        try:
            self.API_ENDPOINT = env['ApiEndpoint']
            self.FACE_AREA_THRESHOLD = env['FaceAreaThreshold']
            self.NAME_TTL_SEC = env['NameTtlSec']
            self.FACE_SIMILARITY_THRESHOLD = env['FaceSimilarityThreshold']
            self.COGNITO_USERPOOL_ID = env['CognitoUserPoolId']
            self.COGNITO_USERPOOL_CLIENT_ID = env['CognitoUserPoolClientId']
            self.REGION = env['Region']
        except KeyError:
            print('Invalid config file')
            raise

        self.recent_name_list = []
        self.registered_name_set = set()
        self.video_capture = VideoCapture(env, video_device)
        self.detector = Detector(env)
        self.viewer = Viewer(env)

    def _update_name_list(self):
        limit_time = datetime.datetime.now() - datetime.timedelta(seconds=self.NAME_TTL_SEC)
        for d in self.recent_name_list[:]:
            if d.get('timestamp') < limit_time:
                self.recent_name_list.remove(d)

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        date = self._sign(('AWS4' + key).encode('utf-8'), date_stamp)
        region = self._sign(date, region_name)
        service = self._sign(region, service_name)
        signing = self._sign(service, 'aws4_request')
        return signing

    def _get_id_token_by_cognito(self, username, password):
        client = boto3.client('cognito-idp', self.REGION)
        response = client.initiate_auth(
            ClientId=self.COGNITO_USERPOOL_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response['AuthenticationResult']['IdToken']


    def run(self):
        
        # input username and password
        username = input("Enter username: ")
        password = getpass.getpass('Enter Password: ')

        try:
            id_token = self._get_id_token_by_cognito(username, password)
        except ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                print('User does not exist')
                return
            elif e.response['Error']['Code'] == 'NotAuthorizedException':
                print('Invalid password')
                return
            raise

        # Main loop
        while True:
            frame = self.video_capture.read()
            if frame is None:
                raise RuntimeError('A problem occurred with camera. Cannot read a new image.')

            face_exists, face_image = self.detector.detect(frame)

            if face_exists:
                self.viewer.show_checking(face_image)
                area = face_image.shape[0] * face_image.shape[1]
                if area > self.FACE_AREA_THRESHOLD * 2:
                    # resize
                    ratio = math.sqrt(area / (self.FACE_AREA_THRESHOLD * 2))
                    face_image = cv2.resize(face_image, (int(
                        face_image.shape[1] / ratio), int(face_image.shape[0] / ratio)))
                _, encoded_face_image = cv2.imencode('.jpg', face_image)

                # Call API
                try:
                    endpoint = 'https://' + self.API_ENDPOINT
                    t = datetime.datetime.utcnow()
                    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
                    headers = {
                        'Content-Type': 'image/jpg',
                        'X-Amz-Date':amz_date,
                        'Authorization': id_token
                    }
                    request_parameters = encoded_face_image.tostring()
                    res = requests.post(endpoint, data=request_parameters, headers=headers).json()
                    print(res)
                    # renponse samples:
                    #      {'result': 'OK', 'name': 'hoge', 'similarity': 95.15}
                    #      {'result': 'NO_MATCH', 'name': '', 'similarity': 0}
                    #      {'result': 'INVALID', 'name': '', 'similarity': 0}

                    result = res['result']
                except Exception as e:
                    print(e)

                else:
                    if result == 'OK':
                        name = res['name']
                        similarity = res['similarity']
                        if similarity > self.FACE_SIMILARITY_THRESHOLD:
                            self._update_name_list()
                            if name not in [d.get('name') for d in self.recent_name_list]:
                                # OK! Go Ahead!
                                self.registered_name_set.add(name)
                                self.recent_name_list.append(
                                    {'name': name, 'timestamp': datetime.datetime.now()})
                                self.viewer.show_welcome(face_image, name)

            else:
                # No face found
                self.viewer.show_next()

            key = cv2.waitKey(1)
            if key == ord('q'):
                raise RuntimeError("key 'q' is pressed")
