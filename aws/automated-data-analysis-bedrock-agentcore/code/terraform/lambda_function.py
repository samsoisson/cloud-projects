role.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: [
    'ssm:*',
    'ec2:*',
    'rds:*',
    's3:*',
    'lambda:*',
    'states:*',
    'events:*',
    'cloudwatch:*',
    'sns:*',
    'logs:*',
    'backup:*',
    // 'iam:PassRole' removed to mitigate privilege escalation
  ],
  resources: ['*'],
  conditions: {
    StringEquals: {
      's3:ExpectedBucketOwner': 'YOUR_AWS_ACCOUNT_ID'
    }
  }
}));