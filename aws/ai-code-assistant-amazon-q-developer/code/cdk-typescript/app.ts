const adminPolicy = new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: [
    // Full Amazon Q administrative permissions
    'q:*',
    'codewhisperer:*',
    // IAM management for Q Developer users
    'iam:CreateRole',
    // 'iam:AttachRolePolicy', // Removed to prevent privilege escalation
    'iam:DetachRolePolicy',
    'iam:UpdateRole',
    'iam:TagRole',
    'iam:UntagRole',
    // Organization management
    'organizations:ListAccounts',
    'organizations:DescribeAccount',
    'organizations:DescribeOrganization',
    // SSO administration
    'sso-admin:*',
  ],
  resources: ['*'],
});