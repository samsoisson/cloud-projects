# Updated code with restricted IAM permissions to prevent privilege escalation

role.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "iam:PassRole"
        ],
        resources=[
            self.lambda_role.role_arn
        ],
        conditions={
            "StringEquals": {
                "iam:PassedToService": "lambda.amazonaws.com"
            }
        }
    )
)