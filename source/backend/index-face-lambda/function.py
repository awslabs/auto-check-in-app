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

COLLECTION_NAME = os.environ['RekognitionCollectionName']
DYNAMODB_TABLE_NAME = os.environ['DynamoDBTableName']
LOG_LEVEL = os.environ['LogLevel']
SEND_ANONYMOUS_DATA = os.environ['SendAnonymousData']

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)


def lambda_handler(event, context):
    logger.info('Invoked the IndexFace Lambda function.')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    name = os.path.splitext(os.path.basename(key))[0]

    # Register a face image to Rekognition
    logger.info('Register a face image to Rekognition.')
    response = rekognition.index_faces(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key
            }
        },
        CollectionId=COLLECTION_NAME
    )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200 or len(response['FaceRecords']) == 0:
        raise RuntimeError('Fail to register a face to Rekognition.')

    faceId = response['FaceRecords'][0]['Face']['FaceId']

    # Insert the face data to DynamoDB
    logger.info('Insert the face ID to the DynamoDB table.')
    try:
        response = dynamodb.put_item(
            TableName=DYNAMODB_TABLE_NAME,
            Item={
                'RekognitionId': {'S': faceId},
                'Name': {'S': name},
            }
        )
    except ClientError as err:
        rekognition.delete_faces(
            CollectionId=COLLECTION_NAME,
            FaceId=faceId
        )
        raise err

    # If the face image was registered successfully, delete the image from s3.
    s3.delete_object(Bucket=bucket, Key=key)
    logger.info('Registered a face image successfully.')
