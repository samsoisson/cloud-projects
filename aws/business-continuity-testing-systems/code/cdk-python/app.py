def _create_iam_roles(self) -> None:
    """Create IAM roles for automation and Lambda execution."""

    # Automation execution role
    self.automation_role = iam.Role(
        self,
        "AutomationRole",
        role_name=f"BCTestingRole-{self.project_id}",
        assumed_by=iam.CompositePrincipal(
            iam.ServicePrincipal("ssm.amazonaws.com"),
            iam.ServicePrincipal("lambda.amazonaws.com"),
            iam.ServicePrincipal("states.amazonaws.com"),
            iam.ServicePrincipal("events.amazonaws.com")
        ),
        description="Role for business continuity testing automation",
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        ],
        inline_policies={
            "BCTestingPolicy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "ssm:*",
                            "ec2:*",
                            "rds:*",
                            "s3:*",
                            "lambda:*",
                            "states:*",
                            "events:*",
                            "cloudwatch:*",
                            "sns:*",
                            "logs:*",
                            "backup:*",
                            # "iam:PassRole",  # Removed to prevent privilege escalation
                            "route53:*"
                        ],
                        resources=["*"]
                    )
                ]
            )
        }
    )