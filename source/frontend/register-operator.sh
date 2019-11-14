#!/bin/bash

REGION=us-west-2
STACK_NAME=auto-check-in-app

# Check to see if input has been provided:
if [ -z "$1" ]; then
    echo "Please provide the user name."
    echo "For example: ./register-admin-user.sh user@example.com"
    exit 1
fi

USERNAME=$1
USER_POOL_ID=`aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='CognitoUserPoolId'].OutputValue" --output text --region ${REGION}`

echo "aws cognito-idp admin-create-user --user-pool-id ${USER_POOL_ID} --username ${USERNAME} --region ${REGION}"
aws cognito-idp admin-create-user --user-pool-id ${USER_POOL_ID} --username ${USERNAME} --region ${REGION}

read -sp "Password for $USERNAME: " PASSWORD

echo "aws cognito-idp admin-set-user-password --user-pool-id ${USER_POOL_ID} --username ${USERNAME} --password <PASSWORD> --permanent --region ${REGION}"
aws cognito-idp admin-set-user-password --user-pool-id ${USER_POOL_ID} --username ${USERNAME} --password ${PASSWORD} --permanent --region ${REGION}
