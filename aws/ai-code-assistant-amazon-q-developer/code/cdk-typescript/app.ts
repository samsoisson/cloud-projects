#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as logs from 'aws-cdk-lib/aws-logs';

export interface AmazonQDeveloperStackProps extends cdk.StackProps {
  readonly environmentName?: string;
  readonly enableDetailedLogging?: boolean;
  readonly organizationName?: string;
  readonly enableEnterpriseFeatures?: boolean;
}

export class AmazonQDeveloperStack extends cdk.Stack {
  public readonly developerRole: iam.Role;
  public readonly artifactsBucket: s3.Bucket;
  public readonly logGroup: logs.LogGroup;

  constructor(scope: Construct, id: string, props: AmazonQDeveloperStackProps = {}) {
    super(scope, id, props);

    const {
      environmentName = 'dev',
      enableDetailedLogging = true,
      organizationName = 'MyOrganization',
      enableEnterpriseFeatures = false
    } = props;

    const resourcePrefix = `amazon-q-${environmentName}`;

    this.logGroup = new logs.LogGroup(this, 'AmazonQLogGroup', {
      logGroupName: `/aws/amazon-q-developer/${environmentName}`,
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.artifactsBucket = new s3.Bucket(this, 'AmazonQArtifactsBucket', {
      bucketName: `${resourcePrefix}-artifacts-${cdk.Aws.ACCOUNT_ID}-${cdk.Aws.REGION}`,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      lifecycleRules: [
        {
          id: 'DeleteOldVersions',
          enabled: true,
          noncurrentVersionExpiration: cdk.Duration.days(30),
        },
        {
          id: 'TransitionToIA',
          enabled: true,
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(30),
            },
          ],
        },
      ],
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    this.developerRole = new iam.Role(this, 'AmazonQDeveloperRole', {
      roleName: `${resourcePrefix}-developer-role`,
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      description: 'IAM role for Amazon Q Developer enhanced functionality',
      maxSessionDuration: cdk.Duration.hours(12),
    });

    const amazonQBasicPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'q:*',
        'codewhisperer:*',
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
        'logs:DescribeLogGroups',
        'logs:DescribeLogStreams',
        'sts:GetCallerIdentity',
        'iam:GetUser',
        'iam:ListAttachedRolePolicies',
        'iam:ListRolePolicies',
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
      ],
      resources: [
        this.logGroup.logGroupArn,
        `${this.logGroup.logGroupArn}:*`,
        this.artifactsBucket.bucketArn,
        `${this.artifactsBucket.bucketArn}/*`,
        '*',
      ],
    });

    this.developerRole.addToPolicy(amazonQBasicPolicy);

    if (enableEnterpriseFeatures) {
      const enterprisePolicy = new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'sso:ListInstances',
          'sso:DescribeInstance',
          'sso:ListAccounts',
          'sso:ListAccountsForProvisionedPermissionSet',
          'identitystore:DescribeUser',
          'identitystore:DescribeGroup',
          'identitystore:ListUsers',
          'identitystore:ListGroups',
          'cloudtrail:LookupEvents',
          'config:GetComplianceDetailsByResource',
          'config:GetResourceConfigHistory',
          'ce:GetCostAndUsage',
          'ce:GetUsageReport',
          'budgets:ViewBudget',
        ],
        resources: ['*'],
      });

      this.developerRole.addToPolicy(enterprisePolicy);

      const adminRole = new iam.Role(this, 'AmazonQAdminRole', {
        roleName: `${resourcePrefix}-admin-role`,
        assumedBy: new iam.CompositePrincipal(
          new iam.ServicePrincipal('lambda.amazonaws.com'),
          new iam.ArnPrincipal(`arn:aws:iam::${cdk.Aws.ACCOUNT_ID}:root`)
        ),
        description: 'Administrative role for Amazon Q Developer enterprise management',
      });

      const adminPolicy = new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'q:*',
          'codewhisperer:*',
          'iam:CreateRole',
          'iam:UpdateRole',
          'iam:TagRole',
          'iam:UntagRole',
          'organizations:ListAccounts',
          'organizations:DescribeAccount',
          'organizations:DescribeOrganization',
          'sso-admin:*',
        ],
        resources: ['*'],
      });

      adminRole.addToPolicy(adminPolicy);

      new cdk.CfnOutput(this, 'AmazonQAdminRoleArn', {
        value: adminRole.roleArn,
        description: 'ARN of the Amazon Q Developer admin role for enterprise management',
        exportName: `${resourcePrefix}-admin-role-arn`,
      });
    }

    const commonTags = {
      Environment: environmentName,
      Application: 'Amazon Q Developer',
      Organization: organizationName,
      ManagedBy: 'AWS CDK',
      CostCenter: 'Development Tools',
    };

    Object.entries(commonTags).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });

    new cdk.CfnOutput(this, 'DeveloperRoleArn', {
      value: this.developerRole.roleArn,
      description: 'ARN of the IAM role for Amazon Q Developer users',
      exportName: `${resourcePrefix}-developer-role-arn`,
    });

    new cdk.CfnOutput(this, 'ArtifactsBucketName', {
      value: this.artifactsBucket.bucketName,
      description: 'Name of the S3 bucket for Amazon Q Developer artifacts',
      exportName: `${resourcePrefix}-artifacts-bucket-name`,
    });

    new cdk.CfnOutput(this, 'LogGroupName', {
      value: this.logGroup.logGroupName,
      description: 'Name of the CloudWatch Log Group for Amazon Q Developer',
      exportName: `${resourcePrefix}-log-group-name`,
    });

    new cdk.CfnOutput(this, 'LogGroupArn', {
      value: this.logGroup.logGroupArn,
      description: 'ARN of the CloudWatch Log Group for Amazon Q Developer',
      exportName: `${resourcePrefix}-log-group-arn`,
    });

    new cdk.CfnOutput(this, 'SetupInstructions', {
      value: [
        '1. Install Amazon Q extension in VS Code',
        '2. Authenticate using AWS Builder ID or IAM Identity Center',
        '3. Configure settings in VS Code preferences',
        '4. Start coding with AI assistance!'
      ].join(' | '),
      description: 'Quick setup instructions for Amazon Q Developer',
    });

    if (enableDetailedLogging) {
      new cdk.CfnOutput(this, 'ComplianceNote', {
        value: 'CloudWatch logging enabled for compliance and monitoring. Review logs regularly for security and usage patterns.',
        description: 'Compliance and monitoring information',
      });
    }
  }

  public addDeveloperPolicy(policyStatement: iam.PolicyStatement): void {
    this.developerRole.addToPolicy(policyStatement);
  }

  public getArtifactsBucket(): s3.Bucket {
    return this.artifactsBucket;
  }

  public getLogGroup(): logs.LogGroup {
    return this.logGroup;
  }
}

const app = new cdk.App();

const environmentName = app.node.tryGetContext('environment') || process.env.ENVIRONMENT_NAME || 'dev';
const organizationName = app.node.tryGetContext('organization') || process.env.ORGANIZATION_NAME || 'MyOrganization';
const enableEnterpriseFeatures = app.node.tryGetContext('enableEnterprise') === 'true' || 
                                  process.env.ENABLE_ENTERPRISE_FEATURES === 'true';
const enableDetailedLogging = app.node.tryGetContext('enableLogging') !== 'false' && 
                              process.env.ENABLE_DETAILED_LOGGING !== 'false';

const stack = new AmazonQDeveloperStack(app, 'AmazonQDeveloperStack', {
  stackName: `amazon-q-developer-${environmentName}`,
  description: 'Infrastructure for Amazon Q Developer AI coding assistant setup and enterprise management',
  environmentName,
  organizationName,
  enableEnterpriseFeatures,
  enableDetailedLogging,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  tags: {
    Application: 'Amazon Q Developer',
    Environment: environmentName,
    ManagedBy: 'AWS CDK',
  },
});

app.synth();