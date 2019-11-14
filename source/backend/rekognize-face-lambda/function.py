#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.   #
#                                                                            #
#  Licensed under the Amazon Software License (the "License"). You may not   #
#  use this file except in compliance with the License. A copy of the        #
#  License is located at                                                     #
#                                                                            #
#      http://aws.amazon.com/asl/                                            #
#                                                                            #
#  or in the "license" file accompanying this file. This file is distributed #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,        #
#  express or implied. See the License for the specific language governing   #
#  permissions and limitations under the License.                            #
##############################################################################
from botocore.exceptions import ClientError
import boto3
import os
import logging
import base64
import json
import time

REKOGNITION_FACE_SIMILARITY_THRESHOLD = int(os.environ['RekognitionFaceSimilarityThreshold'])
COLLECTION_ID = os.environ['RekognitionCollectionName']
DYNAMODB_TABLE_NAME = os.environ['DynamoDBTableName']
LOG_LEVEL = os.environ['LogLevel']
SEND_ANONYMOUS_DATA = os.environ['SendAnonymousData']

dynamodb = boto3.client('dynamodb')
rekognition = boto3.client('rekognition')

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)


def generate_response(result, name, similarity):
    return {
        'statusCode': 200,
        'headers': {"Content-Type": "application/json"},
        'body': json.dumps({'result': result, 'name': name, 'similarity' : similarity})
    }

def update_item(face_id, similarity):
    ts = int(time.time())
    dynamodb.update_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={'RekognitionId': {'S': face_id}},
        UpdateExpression="SET GatePassed = :ts",
        ExpressionAttributeValues={':ts':{'S': str(ts)}}
        )

def lambda_handler(event, context):
    # logger.info(event)
    binary_image = base64.b64decode(event['body'])

    try:
        try:
            response = rekognition.search_faces_by_image(
                CollectionId=COLLECTION_ID,
                Image={'Bytes': binary_image},
                FaceMatchThreshold=REKOGNITION_FACE_SIMILARITY_THRESHOLD,
                MaxFaces=1
            )

        except ClientError as err:
            code = err.response['Error']['Code']
            if code in ['ProvisionedThroughputExceededException', 'ThrottlingException']:
                logger.exception()
            elif code in ['InvalidParameterException']:
                logger.info('No face in Rekognition')
            else:
                logger.exception(err)
            return generate_response('INVALID', '', 0)

        face_matches = response['FaceMatches']
        if len(face_matches) > 0:
            face_match = face_matches[0]
            similarity = face_match['Similarity']
            face = face_match['Face']
            face_id = face['FaceId']

            try:
                response = dynamodb.get_item(
                    TableName=DYNAMODB_TABLE_NAME,
                    Key={'RekognitionId': {'S': face_id}}
                )
                name = response['Item']['Name']['S']
                update_item(face_id, similarity)
            except Exception as err:
                logger.exception(err)
                return generate_response('INVALID', '', 0)

            logger.info('Above Rekognition Threshold. Similarity: {}'.format(similarity))
            return generate_response('OK', name, similarity)

        else:
            logger.info('Similar Faces Not Found')
            return generate_response('NO_MATCH', '', 0)

    except Exception as err:
        logger.exception(err)
        return generate_response('INVALID', '', 0)
