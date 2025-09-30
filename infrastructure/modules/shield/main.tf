terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.5.0"
    }
  }
}

# Shield Advanced Protection for specified resources
resource "aws_shield_protection" "shield_advanced_protection" {
  name         = "${var.resource_prefix}-${var.resource_name}-shield-protection"
  resource_arn = var.arn_to_protect

  tags = {
    Name = "${var.resource_prefix}-${var.resource_name}-shield-protection"
  }
}

# Health check association for protected resources
resource "aws_shield_protection_health_check_association" "health_check_association" {
  count = var.isShieldProactiveEngagementEnabled && try(length(var.health_check_association_arn) > 0, false) ? 1 : 0

  shield_protection_id = aws_shield_protection.shield_advanced_protection.id
  health_check_arn     = var.health_check_association_arn
}

# To set up proactive engagement for AWS Shield Advanced SRT team.
# To be used only if we have business or enterprise support plan
resource "aws_shield_proactive_engagement" "proactive_engagement" {
  count = var.isShieldProactiveEngagementEnabled ? 1 : 0

  enabled = true

  dynamic "emergency_contact" {
    for_each = var.emergency_contacts
    content {
      email_address = each.email_address
      phone_number  = each.phone_number
      contact_notes = each.contact_notes
    }
  }
}

resource "aws_shield_drt_access_role_arn_association" "enable_srt_access" {
  count = var.isShieldSRTAccessEnabled ? 1 : 0

  role_arn = aws_iam_role.srt_role.arn
}

resource "aws_shield_application_layer_automatic_response" "automatic_mitigation" {
  count = var.isShieldAutomaticResponseEnabled ? 1 : 0

  resource_arn = var.distribution_id_to_protect
  action       = "COUNT"
}
