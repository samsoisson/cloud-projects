#!/usr/bin/env python3
import os
from typing import Any, Dict

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    App,
    Environment,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_s3_notifications as s3n,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct


class QDeveloperInfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        random_suffix = self._generate_random_suffix()
        
        self.template_bucket = self._create_template_bucket(random_suffix)
        
        self.lambda_role = self._create_lambda_execution_role(random_suffix)
        
        self.template_processor = self._create_template_processor_function(random_suffix)
        
        self._configure_s3_event_notification()
        
        self._create_log_group()
        
        self._create_outputs()

    def _generate_random_suffix(self) -> str:
        random_param = secretsmanager.Secret(
            self, "RandomSuffix",
            description="Random suffix for resource naming",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                length=6,
                exclude_punctuation=True,
                exclude_uppercase=True,
                require_each_included_type=True
            ),
            removal_policy=RemovalPolicy.DESTROY
        )
        
        return random_param.secret_value.unsafe_unwrap()[:6]

    def _create_template_bucket(self, suffix: str) -> s3.Bucket:
        bucket = s3.Bucket(
            self, "QDeveloperTemplatesBucket",
            bucket_name=f"q-developer-templates-{suffix}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ValidationResultsCleanup",
                    prefix="validation-results/",
                    expiration=Duration.days(30),
                    abort_incomplete_multipart_upload_after=Duration.days(1)
                ),
                s3.LifecycleRule(
                    id="OldVersionCleanup",
                    noncurrent_version_expiration=Duration.days(90)
                )
            ]
        )
        
        bucket.add_cors_rule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT],
            allowed_origins=["*"],
            allowed_headers=["*"],
            max_age=3000
        )
        
        return bucket

    def _create_lambda_execution_role(self, suffix: str) -> iam.Role:
        role = iam.Role(
            self, "QDeveloperLambdaRole",
            role_name=f"q-developer-automation-role-{suffix}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role for Q Developer template processing Lambda function",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )
        
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:PutObject",
                    "s3:ListBucket"
                ],
                resources=[
                    self.template_bucket.bucket_arn,
                    f"{self.template_bucket.bucket_arn}/*"
                ]
            )
        )
        
        return role

    def _create_template_processor_function(self, suffix: str) -> lambda_.Function:
        function_code = '''
import json
import boto3
import logging
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
cfn_client = boto3.client('cloudformation')

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            
            logger.info(f"Processing template: {key} from bucket: {bucket}")
            
            response = s3_client.get_object(Bucket=bucket, Key=key)
            template_body = response['Body'].read().decode('utf-8')
            
            try:
                validation_response = cfn_client.validate_template(
                    TemplateBody=template_body
                )
                logger.info(f"Template validation successful: {validation_response.get('Description', 'No description')}")
                
                template_data = json.loads(template_body) if template_body.strip().startswith('{') else {}
                stack_name = template_data.get('Metadata', {}).get('StackName', f"q-developer-stack-{key.replace('.json', '').replace('/', '-')}")
                
                if key.startswith('auto-deploy/'):
                    logger.info(f"Auto-deploying stack: {stack_name}")
                    cfn_client.create_stack(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                        Tags=[
                            {'Key': 'Source', 'Value': 'QDeveloperAutomation'},
                            {'Key': 'TemplateFile', 'Value': key}
                        ]
                    )
                    
                validation_result = {
                    'template_file': key,
                    'validation_status': 'VALID',
                    'description': validation_response.get('Description', ''),
                    'parameters': validation_response.get('Parameters', []),
                    'capabilities': validation_response.get('Capabilities', [])
                }
                
                result_key = f"validation-results/{key.replace('.json', '-validation.json')}"
                s3_client.put_object(
                    Bucket=bucket,
                    Key=result_key,
                    Body=json.dumps(validation_result, indent=2),
                    ContentType='application/json'
                )
                
            except Exception as validation_error:
                logger.error(f"Template validation failed: {str(validation_error)}")
                
                error_result = {
                    'template_file': key,
                    'validation_status': 'INVALID',
                    'error': str(validation_error)
                }
                
                result_key = f"validation-results/{key.replace('.json', '-error.json')}"
                s3_client.put_object(
                    Bucket=bucket,
                    Key=result_key,
                    Body=json.dumps(error_result, indent=2),
                    ContentType='application/json'
                )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Template processing completed successfully')
        }
        
    except Exception as e:
        logger.error(f"Lambda execution error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing template: {str(e)}')
        }
'''
        
        function = lambda_.Function(
            self, "TemplateProcessorFunction",
            function_name=f"template-processor-{suffix}",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=lambda_.Code.from_inline(function_code),
            role=self.lambda_role,
            timeout=Duration.seconds(60),
            memory_size=256,
            description="Processes CloudFormation templates from Amazon Q Developer",
            environment={
                "BUCKET_NAME": self.template_bucket.bucket_name,
                "LOG_LEVEL": "INFO"
            },
            retry_attempts=2
        )
        
        return function

    def _configure_s3_event_notification(self) -> None:
        self.template_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(self.template_processor),
            s3.NotificationKeyFilter(
                prefix="templates/",
                suffix=".json"
            )
        )

    def _create_log_group(self) -> None:
        logs.LogGroup(
            self, "TemplateProcessorLogGroup",
            log_group_name=f"/aws/lambda/{self.template_processor.function_name}",
            retention=logs.RetentionDays.TWO_WEEKS,
            removal_policy=RemovalPolicy.DESTROY
        )

    def _create_outputs(self) -> None:
        CfnOutput(
            self, "TemplateBucketName",
            value=self.template_bucket.bucket_name,
            description="S3 bucket name for storing infrastructure templates",
            export_name=f"{self.stack_name}-TemplateBucket"
        )
        
        CfnOutput(
            self, "TemplateBucketArn",
            value=self.template_bucket.bucket_arn,
            description="S3 bucket ARN for storing infrastructure templates"
        )
        
        CfnOutput(
            self, "LambdaFunctionName",
            value=self.template_processor.function_name,
            description="Lambda function name for template processing",
            export_name=f"{self.stack_name}-LambdaFunction"
        )
        
        CfnOutput(
            self, "LambdaFunctionArn",
            value=self.template_processor.function_arn,
            description="Lambda function ARN for template processing"
        )
        
        CfnOutput(
            self, "IAMRoleName",
            value=self.lambda_role.role_name,
            description="IAM role name for Lambda execution"
        )
        
        CfnOutput(
            self, "IAMRoleArn",
            value=self.lambda_role.role_arn,
            description="IAM role ARN for Lambda execution"
        )


def main() -> None:
    app = App()
    
    env = Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1")
    )
    
    QDeveloperInfrastructureStack(
        app, "QDeveloperInfrastructureStack",
        env=env,
        description="Amazon Q Developer Infrastructure Code Generation System",
        tags={
            "Project": "Q-Developer-Automation",
            "Environment": "Development",
            "ManagedBy": "CDK"
        }
    )
    
    app.synth()


if __name__ == "__main__":
    main()