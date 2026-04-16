self.hooks_lambda_role = iam.Role(
    self, "HooksLambdaRole",
    role_name=f"{self.project_name}-hooks-lambda-role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
    managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name(
            "service-role/AWSLambdaBasicExecutionRole"
        ),
    ],
    inline_policies={
        "CodeDeployHooks": iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "codedeploy:PutLifecycleEventHookExecutionStatus",
                        "lambda:InvokeFunction",
                        "cloudwatch:PutMetricData",
                        "ecs:DescribeServices",
                        "ecs:DescribeTasks",
                    ],
                    # Restrict resources to only those needed for deployment hooks
                    resources=[
                        f"arn:aws:codedeploy:{self.region}:{self.account}:deploymentgroup:{self.project_name}-*/*",
                        f"arn:aws:lambda:{self.region}:{self.account}:function:{self.project_name}-*",
                        f"arn:aws:cloudwatch:{self.region}:{self.account}:*",
                        f"arn:aws:ecs:{self.region}:{self.account}:service/{self.project_name}-*/*",
                        f"arn:aws:ecs:{self.region}:{self.account}:task/*",
                    ],
                )
            ]
        )
    },
)
