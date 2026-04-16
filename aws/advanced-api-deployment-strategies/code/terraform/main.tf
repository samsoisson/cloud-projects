resource "aws_api_gateway_domain_name" "custom_domain" {
  count           = var.custom_domain_name != null ? 1 : 0
  domain_name     = var.custom_domain_name
  certificate_arn = var.certificate_arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  security_policy = "TLS_1_2"

  tags = local.common_tags
}