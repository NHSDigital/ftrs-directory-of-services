import html
import re

from ftrs_data_layer.domain.legacy import Service

from service_migration.validation.base import (
    FieldValidationResult,
    ValidationResult,
    Validator,
)
from service_migration.validation.types import ValidationIssue


class ServiceValidator(Validator[Service]):
    """
    Generic service validator for all service records
    Should be expanded/subclassed if required for specific service types
    """

    def validate(self, data: Service) -> ValidationResult[Service]:
        """
        Run validation over the service.

        Runs:
        - Email validation
        - Phone number validation (publicphone)
        """
        validation_result = ValidationResult[Service](
            origin_record_id=data.id,
            issues=[],
            sanitised=data,
        )

        # Store sanitized values
        sanitised_email = data.email
        sanitised_publicphone = data.publicphone
        sanitised_nonpublicphone = data.nonpublicphone

        if email_result := self.validate_email(data.email):
            sanitised_email = email_result.sanitised
            validation_result.issues.extend(email_result.issues)

        if publicphone_result := self.validate_phone_number(data.publicphone):
            sanitised_publicphone = publicphone_result.sanitised
            validation_result.issues.extend(publicphone_result.issues)

        if nonpublicphone_result := self.validate_phone_number(
            data.nonpublicphone,
            expression="nonpublicphone",
        ):
            sanitised_nonpublicphone = nonpublicphone_result.sanitised
            validation_result.issues.extend(nonpublicphone_result.issues)

        # Create new Service instance with sanitised values
        validation_result.sanitised = Service(
            id=data.id,
            publicname=data.publicname,
            email=sanitised_email,
            publicphone=sanitised_publicphone,
            nonpublicphone=sanitised_nonpublicphone,
        )

        return validation_result


class GPPracticeValidator(ServiceValidator):
    # Allowed characters after decoding (alphanumeric, spaces, common punctuation)
    SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\s\-'&.,()]+$")

    def validate(self, data: Service) -> ValidationResult[Service]:
        result = super().validate(data)

        sanitised_name = data.publicname
        name_result = self.validate_name(data.publicname)
        if name_result:
            sanitised_name = name_result.sanitised
            result.issues.extend(name_result.issues)

        # Create new Service instance with sanitised name
        result.sanitised = Service(
            id=result.sanitised.id,
            publicname=sanitised_name,
            email=result.sanitised.email,
            publicphone=result.sanitised.publicphone,
            nonpublicphone=result.sanitised.nonpublicphone,
        )

        return result

    def validate_name(self, name: str | None) -> FieldValidationResult[str]:
        """
        Validate and sanitize GP practice name.

        Decodes HTML entities and checks for suspicious characters.

        Args:
            name: The practice name to validate

        Returns:
            FieldValidationResult containing sanitised name and any validation issues
        """
        if not name:
            return FieldValidationResult(
                original=name,
                sanitised=None,
                issues=[
                    ValidationIssue(
                        severity="error",
                        code="publicname_required",
                        diagnostics="Public name is required for GP practices",
                        expression=["publicname"],
                    )
                ],
            )

        result = FieldValidationResult(
            original=name,
            sanitised=None,
            issues=[],
        )

        # Decode HTML entities to UTF-8
        decoded_name = html.unescape(name)

        # Check for suspicious characters BEFORE sanitization
        has_suspicious_chars = not self.SAFE_NAME_PATTERN.match(decoded_name)

        if has_suspicious_chars:
            result.issues.append(
                ValidationIssue(
                    severity="warning",
                    code="publicname_suspicious_characters",
                    diagnostics=f"Name contains unexpected characters after HTML decoding: {decoded_name}",
                    expression=["publicname"],
                )
            )

        # Always sanitize: strip suspicious characters and normalize whitespace
        # Strip characters not in allowed set
        decoded_name = re.sub(r"[^a-zA-Z0-9\s\-'&.,()]", "", decoded_name)
        # Normalize newlines and tabs to spaces
        decoded_name = re.sub(r"[\n\r\t]+", " ", decoded_name)
        # Collapse multiple spaces to single space
        decoded_name = re.sub(r"\s+", " ", decoded_name)

        # Apply existing cleaning logic (split on hyphen, strip whitespace)
        cleaned_name = decoded_name.split("-", maxsplit=1)[0].strip()
        result.sanitised = cleaned_name

        return result
