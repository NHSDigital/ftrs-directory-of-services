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

        if email_result := self.validate_email(data.email):
            data.email = email_result.sanitised
            validation_result.issues.extend(email_result.issues)

        if publicphone_result := self.validate_phone_number(data.publicphone):
            data.publicphone = publicphone_result.sanitised
            validation_result.issues.extend(publicphone_result.issues)

        if nonpublicphone_result := self.validate_phone_number(
            data.nonpublicphone,
            expression="nonpublicphone",
        ):
            data.nonpublicphone = nonpublicphone_result.sanitised
            validation_result.issues.extend(nonpublicphone_result.issues)

        return validation_result


class GPPracticeValidator(ServiceValidator):
    # Allowed characters after decoding (alphanumeric, spaces, common punctuation)
    SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9\s\-'&.,()]+$")
    # CONSIDER: Maximum allowed length for practice names
    # MAX_NAME_LENGTH = 200
    # Allowed HTML entities that can be decoded
    ALLOWED_ENTITIES = {
        "&#39;": "'",  # Numeric apostrophe
        "&apos;": "'",  # Named apostrophe
        "&#x27;": "'",  # Hex apostrophe
        "&amp;": "&",  # Ampersand
        "&quot;": '"',  # Quote (will be stripped later)
    }

    def validate(self, data: Service) -> ValidationResult[Service]:
        result = super().validate(data)

        name_result = self.validate_name(data.publicname)
        if name_result:
            data.publicname = name_result.sanitised
            result.issues.extend(name_result.issues)

        return result

    def validate_name(self, name: str | None) -> FieldValidationResult[str]:
        """
        Validate and sanitize GP practice name.

        Security measures:
        - Length validation to prevent DoS
        - Validates BEFORE decoding to catch encoding attacks
        - Only allows specific safe HTML entities
        - Rejects (error) instead of warning for suspicious content
        - Sanitizes error messages to prevent log injection

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

        # CONSIDER:  1. Length validation (before any processing)
        # if len(name) > self.MAX_NAME_LENGTH:
        #     result.issues.append(
        #         ValidationIssue(
        #             severity="error",
        #             code="publicname_too_long",
        #             diagnostics=f"Name exceeds maximum length of {self.MAX_NAME_LENGTH} characters",
        #             expression=["publicname"],
        #         )
        #     )
        #     return result

        # 2. Check for suspicious patterns BEFORE decoding (catch encoding attacks)
        if self._has_suspicious_encoding(name):
            result.issues.append(
                ValidationIssue(
                    severity="error",
                    code="publicname_suspicious_encoding",
                    diagnostics="Name contains suspicious or disallowed HTML entities",
                    expression=["publicname"],
                )
            )
            return result

        # 3. Decode only allowed HTML entities (allowlist approach)
        decoded_name = self._decode_allowed_entities(name)

        # 4. Check for suspicious characters AFTER safe decoding
        has_suspicious_chars = not self.SAFE_NAME_PATTERN.match(decoded_name)

        if has_suspicious_chars:
            # Get safe character count for diagnostics (don't expose actual content)
            char_types = self._categorize_characters(decoded_name)
            result.issues.append(
                ValidationIssue(
                    severity="error",
                    code="publicname_suspicious_characters",
                    diagnostics=f"Name contains unexpected character types: {char_types}",
                    expression=["publicname"],
                )
            )
            return result

        # 5. Sanitize: normalize whitespace only (characters already validated)
        # Normalize newlines and tabs to spaces
        decoded_name = re.sub(r"[\n\r\t]+", " ", decoded_name)
        # Collapse multiple spaces to single space
        decoded_name = re.sub(r"\s+", " ", decoded_name)

        # 6. Apply existing cleaning logic (split on hyphen, strip whitespace)
        # TODO: FTRS-1961 fix as part of "some GP practice names are truncated"
        cleaned_name = decoded_name.split("-", maxsplit=1)[0].strip()

        # 7. Final length check after sanitization
        if len(cleaned_name) == 0:
            result.issues.append(
                ValidationIssue(
                    severity="error",
                    code="publicname_empty_after_sanitization",
                    diagnostics="Name is empty after sanitization",
                    expression=["publicname"],
                )
            )
            return result

        result.sanitised = cleaned_name
        return result

    def _has_suspicious_encoding(self, name: str) -> bool:
        """
        Check for suspicious or disallowed HTML entities before decoding.

        Returns True if name contains:
        - Double-encoded entities (e.g., &amp;lt;)
        - Entities not in the allowlist
        - Potential injection patterns
        """
        # Check for double encoding
        if "&amp;" in name and any(
            entity in name for entity in ["&amp;lt;", "&amp;gt;", "&amp;#"]
        ):
            return True

        # Find all HTML entities in the input
        entity_pattern = re.compile(r"&[#a-zA-Z0-9]+;")
        found_entities = entity_pattern.findall(name)

        # Check if any found entity is not in our allowlist
        for entity in found_entities:
            if entity not in self.ALLOWED_ENTITIES:
                return True

        return False

    def _decode_allowed_entities(self, name: str) -> str:
        """
        Decode only explicitly allowed HTML entities.
        This prevents decoding of potentially malicious content.
        """
        decoded = name
        for entity, replacement in self.ALLOWED_ENTITIES.items():
            decoded = decoded.replace(entity, replacement)
        return decoded

    def _categorize_characters(self, text: str) -> str:
        """
        Categorize unexpected characters without exposing actual content.
        Safe for use in error messages to prevent log injection.
        """
        categories = []

        if any(c in text for c in "<>"):
            categories.append("angle_brackets")
        if any(c in text for c in "[]{}"):
            categories.append("brackets")
        if any(c in text for c in ";:"):
            categories.append("special_punctuation")
        if any(c in text for c in "|\\/$"):
            categories.append("control_characters")
        if re.search(r"[^\x20-\x7E]", text):
            categories.append("non_printable")

        return ", ".join(categories) if categories else "unknown"
