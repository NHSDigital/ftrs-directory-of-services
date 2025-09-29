# Shield Advanced Protection for specified resources
resource "aws_shield_protection" "shield_advanced_protection" {
  for_each     = var.arns_to_protect
  name         = "${var.resource_prefix}-${each.key}"
  resource_arn = each.value

  tags = {
    Name = "${var.resource_prefix}-${each.key}"
  }
}

# Health check association for protected resources
resource "aws_shield_protection_health_check_association" "health_check_association" {
  count    = var.isProactiveEngagementEnabled ? 1 : 0
  for_each = var.health_check_associations

  shield_protection_id = aws_shield_protection.shield_advanced_protection[each.key].id
  health_check_arn     = each.value
}

# To set up proactive engagement for AWS Shield Advanced SRT team.
# To be used only if we have business or enterprise support plan
resource "aws_shield_proactive_engagement" "proactive_engagement" {
  count = var.isProactiveEngagementEnabled ? 1 : 0

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
  count = var.isSRTAccessEnabled ? 1 : 0

  role_arn = aws_iam_role.srt_role.arn
}

resource "aws_shield_application_layer_automatic_response" "automatic_mitigation" {
  count = var.isAutomaticResponseEnabled ? 1 : 0

  for_each = toset(var.distribution_ids_to_protect)

  resource_arn = each.value
  action       = "COUNT"
}
