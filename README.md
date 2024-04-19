# site-assets-deployment

A custom CloudFormation resource that deploys static web assets to an S3 bucket.

## Description

CloudFormation lacks built in support for uploading static website assets such as JavaScript files, HTML pages or CSS files as part of a CloudFormation deployment. site-assets-deployment is a CloudFormation custom resource that lets you define the assets you want to upload to your s3 bucket in a lambda layer, and then package, deploy, update and delete those assets as part of the standard CloudFormation stack lifecycle.

## Getting started

site-assets-deployment is available via the AWS Serverless Application Repository. To include it in your CloudFormation template and use it to manage your static assets as part of the CloudFormation stack lifecycle:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'
Description: An example stack showing the use of static-assets-deployment
Resources:

  StaticAssetsDeployment:
    Type: AWS::Serverless::Application
    Properties:
      Location:
        ApplicationId: 'arn:aws:serverlessrepo:eu-west-2:211125310871:applications/static-assets-deployment'
        SemanticVersion: <CURRENT_VERSION>
      Parameters:
        StaticAssetsBucket: !Ref SiteStaticAssetsBucket
        StaticAssetsLayerArn: !Ref StaticAssetsLayer

  StaticAssetsLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: static-assets
      Description: Static assets layer.
      ContentUri: ./static-assets
      CompatibleRuntimes:
        - python3.12
      CompatibleArchitectures:
        - arm64
      RetentionPolicy: Delete
    Metadata:
      BuildMethod: python3.12
      BuildArchitecture: arm64

  SiteStaticAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
```

Then you can deploy your stack. These steps assume you have the [SAM CLI installed and set up for your environment](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html):

```
$ sam build
$ sam deploy \
    --capabilities CAPABILITIES_IAM CAPABILITIES_AUTO_EXPAND \
    --stack-name example-stack \
    --resolve-s3
```
