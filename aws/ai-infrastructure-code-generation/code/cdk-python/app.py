role.add_to_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "iam:PassRole"
        ],
        # Restrict PassRole to only allow passing the Lambda execution role itself
        resources=[f"arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:role/q-developer-automation-role-{suffix}"]
    )
)