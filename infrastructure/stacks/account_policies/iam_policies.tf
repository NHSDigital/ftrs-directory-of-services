locals {
  billing_ro_policy                   = jsondecode(file("${path.module}/policies/ro_billing.json"))
  compute_rw_policy                   = jsondecode(file("${path.module}/policies/rw_compute.json"))
  compute_ro_policy                   = jsondecode(file("${path.module}/policies/ro_compute.json"))
  data_rw_policy                      = jsondecode(file("${path.module}/policies/rw_data.json"))
  data_ro_policy                      = jsondecode(file("${path.module}/policies/ro_data.json"))
  networking_rw_policy                = jsondecode(file("${path.module}/policies/rw_networking.json"))
  networking_ro_policy                = jsondecode(file("${path.module}/policies/ro_networking.json"))
  security_rw_policy                  = jsondecode(file("${path.module}/policies/rw_security.json"))
  security_ro_policy                  = jsondecode(file("${path.module}/policies/ro_security.json"))
  monitoring_rw_policy                = jsondecode(file("${path.module}/policies/rw_monitoring.json"))
  monitoring_ro_policy                = jsondecode(file("${path.module}/policies/ro_monitoring.json"))
  management_rw_policy                = jsondecode(file("${path.module}/policies/rw_management.json"))
  management_ro_policy                = jsondecode(file("${path.module}/policies/ro_management.json"))
  infrastructure_security_rw_policy   = jsondecode(file("${path.module}/policies/rw_infrastructure_security.json"))
  infrastructure_security_ro_policy   = jsondecode(file("${path.module}/policies/ro_infrastructure_security.json"))
  infrastructure_management_rw_policy = jsondecode(file("${path.module}/policies/rw_infrastructure_management.json"))
  infrastructure_management_ro_policy = jsondecode(file("${path.module}/policies/ro_infrastructure_management.json"))
  infrastructure_resilience_rw_policy = jsondecode(file("${path.module}/policies/rw_infrastructure_resilience.json"))
}

resource "aws_iam_policy" "billing_policy_ro" {
  name        = "ro_billing"
  description = "Read-only policies for aws billing services"
  policy      = jsonencode(local.billing_ro_policy)
}

resource "aws_iam_policy" "compute_policy_rw" {
  name        = "rw_compute"
  description = "Read-write policies for aws compute-related services"
  policy      = jsonencode(local.compute_rw_policy)
}

resource "aws_iam_policy" "compute_policy_ro" {
  name        = "ro_compute"
  description = "Read-only policies for aws compute-related services"
  policy      = jsonencode(local.compute_ro_policy)
}

resource "aws_iam_policy" "data_rw" {
  name        = "rw_data"
  description = "Read-write policies for aws data services"
  policy      = jsonencode(local.data_rw_policy)
}

resource "aws_iam_policy" "data_ro" {
  name        = "ro_data"
  description = "Read-only policies for aws data services"
  policy      = jsonencode(local.data_ro_policy)
}

resource "aws_iam_policy" "networking_rw" {
  name        = "rw_networking"
  description = "Read-write policies for aws networking services"
  policy      = jsonencode(local.networking_rw_policy)
}

resource "aws_iam_policy" "networking_ro" {
  name        = "ro_networking"
  description = "Read-only policies for aws networking services"
  policy      = jsonencode(local.networking_ro_policy)
}

resource "aws_iam_policy" "security_rw" {
  name        = "rw_security"
  description = "Read-write policies for aws security services"
  policy      = jsonencode(local.security_rw_policy)
}

resource "aws_iam_policy" "security_ro" {
  name        = "ro_security"
  description = "Read-only policies for aws security services"
  policy      = jsonencode(local.security_ro_policy)
}

resource "aws_iam_policy" "monitoring_rw" {
  name        = "rw_monitoring"
  description = "Read-write policies for aws monitoring services"
  policy      = jsonencode(local.monitoring_rw_policy)
}

resource "aws_iam_policy" "monitoring_ro" {
  name        = "ro_monitoring"
  description = "Read-only policies for aws monitoring services"
  policy      = jsonencode(local.monitoring_ro_policy)
}

resource "aws_iam_policy" "management_rw" {
  name        = "rw_management"
  description = "Read-write policies for aws management services"
  policy      = jsonencode(local.management_rw_policy)
}

resource "aws_iam_policy" "management_ro" {
  name        = "ro_management"
  description = "Read-only policies for aws management services"
  policy      = jsonencode(local.management_ro_policy)
}

resource "aws_iam_policy" "infrastructure_security_ro" {
  name        = "ro_infrastructure_security"
  description = "Read-only policies for aws infrastructure security services"
  policy      = jsonencode(local.infrastructure_security_ro_policy)
}

resource "aws_iam_policy" "infrastructure_management_rw" {
  name        = "rw_infrastructure_management"
  description = "Read-write policies for aws infrastructure management services"
  policy      = jsonencode(local.infrastructure_management_rw_policy)
}

resource "aws_iam_policy" "infrastructure_management_ro" {
  name        = "ro_infrastructure_management"
  description = "Read-only policies for aws infrastructure management services"
  policy      = jsonencode(local.infrastructure_management_ro_policy)
}

resource "aws_iam_policy" "infrastructure_resilience_rw" {
  name        = "rw_infrastructure_resilience"
  description = "Read-write policies for aws resilience hub services"
  policy      = jsonencode(local.infrastructure_management_ro_policy)
}


