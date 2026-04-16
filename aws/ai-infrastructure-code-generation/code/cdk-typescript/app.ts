// CloudFormation permissions for template validation and stack operations
new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: [
    'cloudformation:ValidateTemplate',
    'cloudformation:DescribeStacks',
    'cloudformation:DescribeStackEvents',
    'cloudformation:UpdateStack',
    'cloudformation:DeleteStack',
    'cloudformation:ListStacks',
    // 'iam:PassRole' action is intentionally omitted to prevent privilege escalation
  ],
  resources: ['*'],
}),