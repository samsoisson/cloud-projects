#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-sub

// Assuming the S3 bucket operation is on line 115
const bucket = new s3.Bucket(this, 'MyBucket', {
  versioned: true,
  removalPolicy: cdk.RemovalPolicy.RETAIN,
  autoDeleteObjects: false,
});

const bucketOwner = new iam.AccountPrincipal('123456789012'); // Replace with actual account ID

const bucketPolicy = new iam.PolicyStatement({
  actions: ['s3:GetObject'],
  resources: [bucket.bucketArn + '/*'],
  principals: [bucketOwner],
  conditions: {
    "StringEquals": {
      "s3:ExistingObjectTag/Owner": bucketOwner.accountId
    }
  }
});

bucket.addToResourcePolicy(bucketPolicy);