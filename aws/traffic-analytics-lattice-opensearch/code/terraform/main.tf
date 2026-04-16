resource "aws_opensearch_domain" "traffic_analytics" {
  domain_name    = "${var.project_name}-${local.name_suffix}"
  engine_version = var.opensearch_version

  cluster_config {
    instance_type  = var.opensearch_instance_type
    instance_count = var.opensearch_instance_count
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = var.opensearch_volume_size
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https        = true
    tls_security_policy  = "Policy-Min-TLS-1-2-2019-07"
  }

  # Open access policy for demo purposes - restrict in production
  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${var.project_name}-${local.name_suffix}/*"
      }
    ]
  })

  tags = local.common_tags

  depends_on = [aws_iam_service_linked_role.opensearch]
}