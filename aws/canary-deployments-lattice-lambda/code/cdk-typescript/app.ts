// Add VPC Lattice invoke permissions
lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: ['lambda:InvokeFunction'],
  resources: [
    // Restrict to only the production and canary Lambda functions
    // These ARNs will resolve correctly after function creation
    // Use '*' for now, but will be replaced after function creation below
  ],
}));