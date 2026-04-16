new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: [
    'cloudformation:ValidateTemplate',
    'cloudformation:DescribeStacks',
    'cloudformation:DescribeStackEvents',
    'cloudformation:ListStacks',
  ],
  // Restrict resources to specific ARNs as appropriate for your use case.
  // Avoid using '*' to prevent privilege escalation.
  resources: [
    'arn:aws:cloudformation:YOUR_REGION:YOUR_ACCOUNT_ID:stack/YOUR_STACK_NAME/*'
  ],
}),