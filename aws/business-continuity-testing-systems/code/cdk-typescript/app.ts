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
    // 'iam:PassRole' removed for least privilege
  ],
  resources: ['*']
}));

// Add a restricted PassRole statement for only the automation role itself
role.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: [
    'iam:PassRole'
  ],
  resources: [role.roleArn]
}));