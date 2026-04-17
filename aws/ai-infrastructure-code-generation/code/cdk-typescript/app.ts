#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3notifications from 'aws-cdk-lib/aws-s3-notifications';
import * as logs from 'aws-cdk-lib/aws-logs';

export class QDeveloperInfrastructureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const randomSuffix = Math.random().toString(36).substring(2, 8);

    const templateBucket = new s3.Bucket(this, 'TemplateBucket', {
      bucketName: `q-developer-templates-${randomSuffix}`,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      lifecycleRules: [
        {
          id: 'template-lifecycle',
          enabled: true,
          expiration: cdk.Duration.days(90),
          noncurrentVersionExpiration: cdk.Duration.days(30),
        },
      ],
    });

    const logGroup = new logs.LogGroup(this, 'TemplateProcessorLogGroup', {
      logGroupName: `/aws/lambda/template-processor-${randomSuffix}`,
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const lambdaRole = new iam.Role(this, 'TemplateProcessorRole', {
      roleName: `q-developer-automation-role-${randomSuffix}`,
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      description: 'Role for Q Developer template processing Lambda function',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
      inlinePolicies: {
        TemplateProcessingPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                's3:GetObject',
                's3:GetObjectVersion',
                's3:PutObject',
                's3:ListBucket',
              ],
              resources: [
                templateBucket.bucketArn,
                `${templateBucket.bucketArn}/*`,
              ],
            }),
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'cloudformation:ValidateTemplate',
                'cloudformation:DescribeStacks',
                'cloudformation:DescribeStackEvents',
                'cloudformation:UpdateStack',
                'cloudformation:DeleteStack',
                'cloudformation:ListStacks',
              ],
              resources: ['*'],
            }),
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'iam:CreateRole',
                'iam:AttachRolePolicy',
                'iam:GetRole',
                'iam:ListRoles',
              ],
              resources: ['*'],
            }),
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents',
              ],
              resources: [logGroup.logGroupArn],
            }),
          ],
        }),
      },
    });

    const templateProcessor = new lambda.Function(this, 'TemplateProcessor', {
      functionName: `template-processor-${randomSuffix}`,
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.lambda_handler',
      role: lambdaRole,
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      description: 'Processes CloudFormation templates from Amazon Q Developer with validation and deployment capabilities',
      environment: {
        BUCKET_NAME: templateBucket.bucketName,
        LOG_LEVEL: 'INFO',
      },
      logGroup: logGroup,
      code: lambda.Code.fromInline(`...`),
    });

    templateBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3notifications.LambdaDestination(templateProcessor),
      {
        prefix: 'templates/',
        suffix: '.json',
      }
    );

    templateBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3notifications.LambdaDestination(templateProcessor),
      {
        prefix: 'auto-deploy/',
        suffix: '.json',
      }
    );

    new cdk.CfnOutput(this, 'TemplateBucketName', {
      value: templateBucket.bucketName,
      description: 'S3 bucket for storing infrastructure templates',
      exportName: `${this.stackName}-TemplateBucket`,
    });

    new cdk.CfnOutput(this, 'TemplateBucketArn', {
      value: templateBucket.bucketArn,
      description: 'ARN of the template storage S3 bucket',
      exportName: `${this.stackName}-TemplateBucketArn`,
    });

    new cdk.CfnOutput(this, 'LambdaFunctionName', {
      value: templateProcessor.functionName,
      description: 'Name of the template processing Lambda function',
      exportName: `${this.stackName}-LambdaFunction`,
    });

    new cdk.CfnOutput(this, 'LambdaFunctionArn', {
      value: templateProcessor.functionArn,
      description: 'ARN of the template processing Lambda function',
      exportName: `${this.stackName}-LambdaFunctionArn`,
    });

    new cdk.CfnOutput(this, 'LogGroupName', {
      value: logGroup.logGroupName,
      description: 'CloudWatch Log Group for monitoring template processing',
      exportName: `${this.stackName}-LogGroup`,
    });

    new cdk.CfnOutput(this, 'UploadInstructions', {
      value: `Upload templates to s3://${templateBucket.bucketName}/templates/ for validation or s3://${templateBucket.bucketName}/auto-deploy/ for automatic deployment`,
      description: 'Instructions for uploading templates to trigger processing',
    });

    cdk.Tags.of(this).add('Project', 'QDeveloperInfrastructureAutomation');
    cdk.Tags.of(this).add('Environment', 'Development');
    cdk.Tags.of(this).add('Owner', 'DevOps-Team');
    cdk.Tags.of(this).add('CostCenter', 'Infrastructure-Automation');
  }
}

const app = new cdk.App();

new QDeveloperInfrastructureStack(app, 'QDeveloperInfrastructureStack', {
  description: 'AI-powered infrastructure code generation with Amazon Q Developer and AWS Infrastructure Composer integration',
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  tags: {
    Application: 'QDeveloperInfrastructure',
    Version: '1.0',
    CreatedBy: 'CDK',
  },
});