#!/usr/bin/env python3
"""
AWS CDK Python application for Business Continuity Testing Framework.

This application creates a comprehensive business continuity testing framework using
AWS Systems Manager Automation, Lambda functions, EventBridge, and CloudWatch.
The framework enables automated testing of backup validation, database recovery,
and application failover scenarios.
"""

import os
from typing import Dict, Any

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_ssm as ssm,
    aws_cloudwatch as cloudwatch,
    aws_logs as logs,
)
from constructs import Construct


class BusinessContinuityTestingStack(Stack):
    """
    CDK Stack for Business Continuity Testing Framework.
    
    Creates automation documents, Lambda functions, EventBridge rules,
    and monitoring infrastructure for comprehensive BC testing.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Stack parameters
        self.project_id = self.node.try_get_context("project_id") or "bctest"
        self.notification_email = self.node.try_get_context("notification_email") or "admin@example.com"
        
        # Create core infrastructure
        self._create_iam_roles()
        self._create_s3_bucket()
        self._create_sns_topic()
        self._create_automation_documents()
        self._create_lambda_functions()
        self._create_event_rules()
        self._create_cloudwatch_dashboard()
        
        # Create outputs
        self._create_outputs()

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
                                "ssm:StartAutomationExecution",
                                "ssm:DescribeAutomationExecutions",
                                "ec2:StartInstances",
                                "ec2:StopInstances",
                                "rds:StartDBInstance",
                                "rds:StopDBInstance",
                                "s3:PutObject",
                                "s3:GetObject",
                                "lambda:InvokeFunction",
                                "states:StartExecution",
                                "states:DescribeExecution",
                                "events:PutEvents",
                                "cloudwatch:PutMetricData",
                                "sns:Publish",
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "backup:StartRestoreJob",
                                "