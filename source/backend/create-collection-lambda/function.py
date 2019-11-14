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
import boto3
import json
import cfnresponse
import os
import logging

LOG_LEVEL = os.environ['LogLevel']
SEND_ANONYMOUS_DATA = os.environ['SendAnonymousData']

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

rekognition = boto3.client('rekognition')


def lambda_handler(event, context):

    collection_id = event['ResourceProperties']['RekognitionCollectionName']

    if event['RequestType'] == 'Delete':
        try:
            ret = rekognition.delete_collection(CollectionId=collection_id)
            if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('Resource deleted')
                cfnresponse.send(event, context, "SUCCESS", {})
            return
        except:
            logger.exception('Failed to delete Rekognition collection')
            cfnresponse.send(event, context, "FAILED", {})
    else:
        try:
            ret = rekognition.create_collection(CollectionId=collection_id)
            if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('Resource created')
                cfnresponse.send(event, context, "SUCCESS", {})
        except:
            logger.exception('Failed to create Rekognition collection')
            cfnresponse.send(event, context, "FAILED", {})
