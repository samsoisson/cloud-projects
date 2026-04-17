# Remove the inline policy "CodeDeployHooks" from self.hooks_lambda_role to prevent privilege escalation
# Specifically, the inline policy granting broad permissions should be removed

# Updated code snippet for the _create_iam_roles method:

def _create_iam_roles(self) -> None:
    """Create IAM roles with least privilege permissions."""
    # ECS Task Execution Role
    self.ecs_execution_role = iam.Role(
        self, "ECSExecutionRole",
        role_name=f"{self.project_name}-ecs-execution-role",
        assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AmazonECSTaskExecutionRolePolicy"
            ),
        ],
    )

    # ECS Task Role
    self.ecs_task_role = iam.Role(
        self, "ECSTaskRole",
        role_name=f"{self.project_name}-ecs-task-role",
        assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        inline_policies={
            "CloudWatchMetrics": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "cloudwatch:PutMetricData",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                        ],
                        resources=["*"],
                    )
                ]
            )
        },
    )

    # Lambda Execution Role
    self.lambda_execution_role = iam.Role(
        self, "LambdaExecutionRole",
        role_name=f"{self.project_name}-lambda-execution-role",
        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole"
            ),
        ],
    )

    # CodeDeploy Service Role
    self.codedeploy_role = iam.Role(
        self, "CodeDeployRole",
        role_name=f"{self.project_name}-codedeploy-role",
        assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSCodeDeployRoleForECS"
            ),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSCodeDeployRoleForLambda"
            ),
        ],
    )

    # Deployment Hooks Lambda Role
    self.hooks_lambda_role = iam.Role(
        self, "HooksLambdaRole",
        role_name=f"{self.project_name}-hooks-lambda-role",
        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            ),
        ],
        # Removed the inline policy "CodeDeployHooks" to eliminate over-permissive access
        # If specific permissions are needed, add minimal necessary policies here
    )