def _create_launch_role(self, suffix: str) -> iam.Role:
    """
    Create IAM role for Service Catalog launch constraints.
    
    Args:
        suffix: Unique suffix for resource naming
        
    Returns:
        IAM role for launch constraints
    """
    launch_role = iam.Role(
        self, "LaunchRole",
        role_name=f"ServiceCatalogLaunchRole-{suffix}",
        assumed_by=iam.ServicePrincipal("servicecatalog.amazonaws.com"),
        description="IAM role for Service Catalog product launch constraints",
    )

    # Create inline policy with necessary permissions
    launch_policy = iam.PolicyDocument(
        statements=[
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:CreateBucket",
                    "s3:DeleteBucket",
                    "s3:PutBucketEncryption",
                    "s3:PutBucketVersioning",
                    "s3:PutBucketPublicAccessBlock",
                    "s3:PutBucketTagging",
                    "s3:GetBucketLocation",
                    "s3:ListBucket",
                    "lambda:CreateFunction",
                    "lambda:DeleteFunction",
                    "lambda:UpdateFunctionCode",
                    "lambda:UpdateFunctionConfiguration",
                    "lambda:TagResource",
                    "lambda:UntagResource",
                    "lambda:GetFunction",
                    "lambda:ListTags",
                    # Removed privilege escalation-prone IAM actions
                    # "iam:CreateRole",
                    # "iam:DeleteRole",
                    # "iam:AttachRolePolicy",
                    # "iam:DetachRolePolicy",
                    "iam:PassRole",
                    # "iam:TagRole",
                    # "iam:UntagRole",
                    "iam:GetRole",
                    "iam:ListRolePolicies",
                    "iam:ListAttachedRolePolicies",
                ],
                resources=["*"],
            )
        ]
    )

    launch_role.attach_inline_policy(
        iam.Policy(
            self, "LaunchPolicy",
            document=launch_policy,
        )
    )

    return launch_role
