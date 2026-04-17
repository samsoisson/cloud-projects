#!/usr/bin/env python3
"""
Advanced Blue-Green Deployments with ECS, Lambda, and CodeDeploy

This CDK application creates a sophisticated blue-green deployment infrastructure
that supports both containerized (ECS) and serverless (Lambda) workloads with
automated rollback capabilities, comprehensive monitoring, and deployment hooks.

The infrastructure includes:
- VPC with public and private subnets
- Application Load Balancer with blue/green target groups
- ECS Fargate cluster and service
- Lambda functions with versioning and aliases
- CodeDeploy applications for both ECS and Lambda
- CloudWatch monitoring and alarms
- SNS notifications
- IAM roles with least privilege access
- ECR repository for container images
- Deployment automation hooks
"""

import os
from aws_cdk import (
    App,
    Stack,
    Environment,
    Tags,
    CfnOutput,
    Duration,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_lambda as lambda_,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_applicationautoscaling as appscaling,
)
from constructs import Construct


class AdvancedBlueGreenDeploymentStack(Stack):
    """
    Advanced Blue-Green Deployment Stack
    
    Creates a comprehensive blue-green deployment infrastructure supporting
    both ECS and Lambda with automated rollback and monitoring capabilities.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Stack parameters
        self.project_name = self.node.try_get_context("project_name") or "advanced-deployment"
        self.environment_name = self.node.try_get_context("environment") or "production"
        
        # Create core infrastructure
        self._create_vpc_infrastructure()
        self._create_security_groups()
        self._create_iam_roles()
        self._create_ecr_repository()
        self._create_application_load_balancer()
        self._create_ecs_infrastructure()
        self._create_lambda_infrastructure()
        self._create_codedeploy_applications()
        self._create_monitoring_and_alarms()
        self._create_deployment_hooks()
        
        # Add stack-level tags
        Tags.of(self).add("Project", self.project_name)
        Tags.of(self).add("Environment", self.environment_name)
        Tags.of(self).add("DeploymentPattern", "BlueGreen")

    def _create_vpc_infrastructure(self) -> None:
        """Create VPC with public and private subnets for multi-AZ deployment."""
        self.vpc = ec2.Vpc(
            self, "VPC",
            vpc_name=f"{self.project_name}-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

        # VPC Flow Logs for security monitoring
        vpc_flow_logs_role = iam.Role(
            self, "VPCFlowLogsRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
            inline_policies={
                "FlowLogsPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:DescribeLogGroups",
                                "logs:DescribeLogStreams",
                            ],
                            resources=["*"],
                        )
                    ]
                )
            },
        )

        vpc_flow_logs = ec2.FlowLog(
            self, "VPCFlowLogs",
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(
                logs.LogGroup(
                    self, "VPCFlowLogsGroup",
                    log_group_name=f"/aws/vpc/flowlogs/{self.project_name}",
                    retention=logs.RetentionDays.ONE_WEEK,
                    removal_policy=RemovalPolicy.DESTROY,
                ),
                vpc_flow_logs_role,
            ),
        )

    def _create_security_groups(self) -> None:
        """Create security groups with least privilege access."""
        # ALB Security Group
        self.alb_security_group = ec2.SecurityGroup(
            self, "ALBSecurityGroup",
            vpc=self.vpc,
            description="Security group for Application Load Balancer",
            security_group_name=f"{self.project_name}-alb-sg",
        )
        
        self.alb_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic",
        )
        
        self.alb_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS traffic",
        )

        # ECS Security Group
        self.ecs_security_group = ec2.SecurityGroup(
            self, "ECSSecurity