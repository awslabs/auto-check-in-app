# Auto Check-in App
Event check-in is the first on-site touchpoint for most events, and the process is your first opportunity to make a good impression with your attendees. An optimized check-in process can help alleviate long lines and attendee confusion, which improves your attendee experience and helps set the tone of your event. 
One way to optimize the check-in process is to automate it using self-check-in. Self-check-in kiosks and apps can enable attendees to check-in through a name search or QR code scan, print their badges, and enter your event quicker. But, self-check-in requires attendees to enter their name in a search interface, or present a QR code to be scanned which can slow the check-in process.
Facial comparison can make it even easier and quicker for attendees to check-in by eliminating the need to enter names or show QR codes. Attendees can have their picture taken and compared with a pre-registered attendee face collection in seconds.
Amazon Rekognition is a fully managed service that makes it easy to add deep learning powered visual analysis to your applications. With Amazon Rekognition, you can compare faces for a wide variety of use cases, including event attendee verification.  
To help make it easier for customers to automate the check-in process, Amazon Web Services (AWS)  offers the Auto Check-In App. This solution automatically provisions the products and services necessary to provide facial comparison for event attendee check-in.  

## Setup
Launch the stack and upload images to Amazon S3. 
### Download and Configure the App
1.    On the laptop you will use during your event, run the following command in your preferred directory to clone the application source code from GitHub.
`$ git clone https://github.com/awslabs/auto-check-in-app.git`
2.    After the code is cloned, navigate to the `auto-check-in-app/source/frontend` directory.
3.    Run the following command.
`chmod +x register-operator.sh`
4.    Run the following command
`./register-operator.sh <operator E-mail address>` 
    - Note: Specify the applicable AWS Region and AWS CloudFormation stack name in the script. 
5.    Enter a password.
6.    Copy the `default.env.json` file to `env.json`. 
7.    Modify the file with the applicable values. 
    - Note: You can find the applicable values in the stack Outputs tab.

### Authenticate Attendees
1.    To launch the check-in app, run the following command. 
`$ python main.py`
2.    When prompted, enter your user name and password.
3.    Use a built-in camera or a USB camera to take a picture of the attendee’s face. While the image is being processed, the status will change from `Stop here` (no face is detected) to `Checking` (the face is detected and being compared to the face collection) to `Welcome` (a face is found with high similarity). 
    - Note: After the status changes to `Welcome`, it will change back to `Checking` for 10 seconds, by default, to avoid recurrent acceptance signals. To change the amount of time, modify the `VisibilityTimeout` parameter in the `env.json` file.
4.    After the image is taken, a window opens to show the face detection and recognition results.
```
{'result': 'OK', 'name': '<username>', 'similarity': 99.71908569335938}
{'result': 'OK', 'name': '<username>', 'similarity': 99.79707336425781}
{'result': 'OK', 'name': '<username>', 'similarity': 99.7418441772461}
```


## Running unit tests for customization
* Clone the repository, then make the desired code changes
* Next, run unit tests to make sure added customization passes the tests
```
cd ./deployment
chmod +x ./run-unit-tests.sh  \n
./run-unit-tests.sh \n
```

## Building distributable for customization
* Configure the bucket name of your target Amazon S3 distribution bucket
```
export DIST_OUTPUT_BUCKET=my-bucket-name # bucket where customized code will reside
export SOLUTION_NAME=my-solution-name
export VERSION=my-version # version number for the customized code
```
_Note:_ You would have to create an S3 bucket with the prefix 'my-bucket-name-<aws_region>'; aws_region is where you are testing the customized solution. Also, the assets in bucket should be publicly accessible.

* Now build the distributable:
```
chmod +x ./build-s3-dist.sh \n
./build-s3-dist.sh $DIST_OUTPUT_BUCKET $SOLUTION_NAME $VERSION \n
```

* Deploy the distributable to an Amazon S3 bucket in your account. _Note:_ you must have the AWS Command Line Interface installed.
```
aws s3 cp ./dist/ s3://my-bucket-name-<aws_region>/$SOLUTION_NAME/$VERSION/ --recursive --acl bucket-owner-full-control --profile aws-cred-profile-name \n
```

* Get the link of the solution template uploaded to your Amazon S3 bucket.
* Deploy the solution to your account by launching a new AWS CloudFormation stack using the link of the solution template in Amazon S3.

*** 

## File Structure

```
|-deployment/
  |-auto-check-in-app.yaml       [ solution CloudFormation deployment template ]
  |-build-s3-dist.sh             [ shell script for packaging distribution assets ]
  |-run-unit-tests.sh            [ shell script for executing unit tests ]
|-source/
  |-backend/                     [ Python scripts for AWS Lambda functions ]
    |-create-collection-lambda/
    |-index-face-lambda/
    |-rekognize-face-lambda/
  |-frontend/
    |-assets/                    [ UI images, face detection models, and sound files ]
    |-controller.py
    |-default.env.json           [ template for env.json file ]
    |-detector.py
    |-main.py                    [ Python script for client operator ]
    |-register-operator.sh       [ registration script for operator ]
    |-video_capture.py
    |-viewer.py

```

Each Lambda function follows the structure of:

```
|-function-name/
  |-cfnresponse.py (optional) 
  |-function.py                  [ function code in Python ]
  |-requirements.txt (optional)  
```

***

Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://www.apache.org/licenses/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
