private createLaunchRole(): iam.Role {
    const role = new iam.Role(this, 'LaunchRole', {
      roleName: `ServiceCatalogLaunchRole-${cdk.Stack.of(this).stackName}`,
      assumedBy: new iam.ServicePrincipal('servicecatalog.amazonaws.com'),
      description: 'IAM role for Service Catalog launch constraints',
    });

    // Add policy with required permissions for S3 and Lambda resources
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        // S3 permissions
        's3:CreateBucket',
        's3:DeleteBucket',
        's3:PutBucketEncryption',
        's3:PutBucketVersioning',
        's3:PutBucketPublicAccessBlock',
        's3:PutBucketTagging',
        // Lambda permissions
        // 'lambda:CreateFunction', // Removed to mitigate privilege escalation
        'lambda:DeleteFunction',
        'lambda:UpdateFunctionCode',
        'lambda:UpdateFunctionConfiguration',
        'lambda:TagResource',
        'lambda:UntagResource',
        // IAM permissions
        'iam:CreateRole',
        'iam:DeleteRole',
        'iam:AttachRolePolicy',
        'iam:DetachRolePolicy',
        'iam:PassRole',
        'iam:TagRole',
        'iam:UntagRole',
      ],
      resources: ['*'],
    }));

    return role;
  }
