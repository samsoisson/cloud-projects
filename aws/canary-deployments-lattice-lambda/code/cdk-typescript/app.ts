// Add VPC Lattice invoke permissions
lambdaExecutionRole.addToPolicy(new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: ['lambda:InvokeFunction'],
  resources: [], // No resources specified to avoid privilege escalation
}));