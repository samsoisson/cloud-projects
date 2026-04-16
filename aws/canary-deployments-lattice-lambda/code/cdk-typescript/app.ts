// Add VPC Lattice invoke permissions
lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: ['lambda:InvokeFunction'],
  resources: [
    // Restrict to only the production and canary Lambda functions
    // These ARNs are available after function creation, so we update the policy after both functions are created below
  ],
}));