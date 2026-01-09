import re

from ftrs_data_layer.domain.legacy import Service

from service_migration.formatting.address_formatter import format_address
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
            validation_result.sanitised.email = email_result.sanitised
            validation_result.issues.extend(email_result.issues)

        if publicphone_result := self.validate_phone_number(data.publicphone):
            validation_result.sanitised.publicphone = publicphone_result.sanitised
            validation_result.issues.extend(publicphone_result.issues)

        if nonpublicphone_result := self.validate_phone_number(
            data.nonpublicphone,
            expression="nonpublicphone",
        ):
            validation_result.sanitised.nonpublicphone = nonpublicphone_result.sanitised
            validation_result.issues.extend(nonpublicphone_result.issues)

        return validation_result


class GPPracticeValidator(ServiceValidator):
    # More restrictive pattern - only allow & when surrounded by spaces
    SAFE_NAME_PATTERN = re.compile(
        r"^[a-zA-Z0-9\s\-'.,()]+(?:\s+&\s+[a-zA-Z0-9\s\-'.,()]+)*$"
    )
    # Maximum allowed length for practice names
    MAX_NAME_LENGTH = 100

    # More comprehensive dangerous patterns
    DANGEROUS_PATTERNS = re.compile(
        r"javascript:|data:|on\w+\s*=|&amp;[#a-zA-Z0-9]+;",
        re.IGNORECASE,
    )

    # Allowed HTML entities that can be decoded
    ALLOWED_ENTITIES = {
        "&#39;": "'",  # Numeric apostrophe
        "&apos;": "'",  # Named apostrophe
        "&#x27;": "'",  # Hex apostrophe
        "&amp;": "&",  # Ampersand
    }

    def validate(self, data: Service) -> ValidationResult[Service]:
        result = super().validate(data)

        if name_result := self.validate_name(data.publicname):
            result.sanitised.publicname = name_result.sanitised
            result.issues.extend(name_result.issues)

        if location_result := self.validate_location(
            data.address, data.town, data.postcode
        ):
            result.issues.extend(location_result.issues)

        return result

    def validate_name(self, name: str | None) -> FieldValidationResult[str]:
        """
        Validate and sanitize GP practice name.

        Security measures:
        - Length validation to prevent DoS
        - Applies hyphen-splitting business rule before validation
        - Validates BEFORE decoding to catch encoding attacks
        - Rejects ANY nested encoding (not just double encoding)
        - Only allows specific safe HTML entities
        - Rejects (error) instead of warning for suspicious content
        - Sanitizes error messages to prevent log injection
        - Restricts ampersand usage to require surrounding spaces

        Args:
            name: The practice name to validate

        Returns:
            FieldValidationResult containing sanitised name and any validation issues
        """
        # Store full original for audit trail
        full_original = name

        # Early validation checks
        if error := self._validate_basic_checks(name):
            return error

        # Remove GP prefix variations from the start of the name
        gp_prefixes = ["GP - ", "GP -", "GP- ", "GP-"]
        for prefix in gp_prefixes:
            if name.startswith(prefix):
                name = name[len(prefix) :].strip()
                break

        # Apply hyphen-splitting business rule BEFORE validation
        # This ensures we only validate the part we'll actually use
        name = name.split(" - ", maxsplit=1)[0].strip()

        # Log when suffix is discarded for monitoring/security purposes
        if " - " in full_original:
            self.logger.info(
                "Practice name suffix discarded",
                extra={
                    "validation_code": "publicname_suffix_removed",
                    "original_length": len(full_original),
                    "sanitized_length": len(name),
                },
            )

        # Check if empty after splitting
        if not name:
            return self._error(
                "publicname_empty_after_sanitization",
                "Name is empty after removing suffix",
            )

        # Decode and validate characters
        try:
            decoded_name = self._decode_allowed_entities(name)
        except ValueError:
            self.logger.warning(
                "Disallowed HTML entities detected",
                extra={
                    "validation_code": "publicname_suspicious_encoding",
                    "name_length": len(name),
                },
            )
            return self._error(
                "publicname_suspicious_encoding",
                "Name contains disallowed HTML entities",
            )

        # Check for suspicious characters AFTER safe decoding
        if not self.SAFE_NAME_PATTERN.match(decoded_name):
            char_types = self._categorize_characters(decoded_name)
            self.logger.warning(
                "Suspicious characters detected in practice name",
                extra={
                    "validation_code": "publicname_suspicious_characters",
                    "character_types": char_types,
                    "name_length": len(decoded_name),
                },
            )
            return self._error(
                "publicname_suspicious_characters",
                f"Name contains unexpected character types: {char_types}",
            )

        # Sanitize whitespace only (hyphen-splitting already done)
        cleaned_name = self._sanitize(decoded_name)
        if not cleaned_name:
            return self._error(
                "publicname_empty_after_sanitization",
                "Name is empty after sanitization",
            )

        return FieldValidationResult(
            original=full_original,
            sanitised=cleaned_name,
            issues=[],
        )

    def _validate_basic_checks(
        self, name: str | None
    ) -> FieldValidationResult[str] | None:
        """
        Perform basic validation checks on the name.

        Returns:
            Error result if validation fails, None if all checks pass
        """
        if not name:
            return self._error(
                "publicname_required", "Public name is required for GP practices"
            )

        # Length validation (before any processing)
        if len(name) > self.MAX_NAME_LENGTH:
            self.logger.warning(
                "Practice name exceeds maximum length",
                extra={
                    "validation_code": "publicname_too_long",
                    "name_length": len(name),
                    "max_length": self.MAX_NAME_LENGTH,
                },
            )
            return self._error(
                "publicname_too_long",
                f"Name exceeds maximum length of {self.MAX_NAME_LENGTH} characters",
            )

        # Check for dangerous patterns BEFORE decoding (catch encoding attacks)
        if self.DANGEROUS_PATTERNS.search(name):
            self.logger.warning(
                "Suspicious encoding or dangerous patterns detected",
                extra={
                    "validation_code": "publicname_suspicious_encoding",
                    "name_length": len(name),
                },
            )
            return self._error(
                "publicname_suspicious_encoding",
                "Name contains suspicious or disallowed HTML entities",
            )

        return None

    def _error(self, code: str, message: str) -> FieldValidationResult[str]:
        """Create error result with consistent structure."""
        return FieldValidationResult(
            original=None,
            sanitised=None,
            issues=[
                ValidationIssue(
                    severity="error",
                    code=code,
                    diagnostics=message,
                    expression=["publicname"],
                )
            ],
        )

    def validate_location(
        self, address: str, town: str, postcode: str
    ) -> FieldValidationResult[str]:
        """
        Validate location using address, town, and postcode.

        Returns formatted address if at least town or postcode is available,
        even if address field is missing or invalid.
        """
        result = FieldValidationResult(
            original=address,
            sanitised=None,
            issues=[],
        )

        # Check 1: Early validation - all fields empty
        if not address and not town and not postcode:
            result.issues.append(
                ValidationIssue(
                    severity="fatal",
                    code="address_required",
                    diagnostics="Address is required for GP practices to create a location",
                    expression=["address"],
                )
            )
            return result

        # Check 2: Attempt to format address
        formatted_address = format_address(address, town, postcode)

        # Check 3: Format result validation Address invalid or incomplete
        if not formatted_address:
            result.issues.append(
                ValidationIssue(
                    severity="fatal",
                    code="invalid_address",
                    diagnostics="Address was invalid or incomplete, could not be formatted for GP practices to create a location",
                    expression=["address"],
                )
            )
            return result

        result.sanitised = formatted_address
        return result

    def _decode_allowed_entities(self, name: str) -> str:
        """
        Decode only explicitly allowed HTML entities.
        This prevents decoding of potentially malicious content.

        Raises:
            ValueError: If disallowed entities are found
        """
        # Check for disallowed entities first
        entity_pattern = re.compile(r"&[#a-zA-Z0-9]+;")
        found_entities = entity_pattern.findall(name)

        if disallowed := [e for e in found_entities if e not in self.ALLOWED_ENTITIES]:
            raise ValueError(f"Disallowed entities: {disallowed}")

        # Decode allowed entities
        decoded = name
        for entity, replacement in self.ALLOWED_ENTITIES.items():
            decoded = decoded.replace(entity, replacement)
        return decoded

    def _sanitize(self, name: str) -> str:
        """
        Normalize whitespace only.

        - Converts newlines/tabs to spaces
        - Collapses multiple spaces to single space
        - Strips leading/trailing whitespace

        Note: Hyphen-splitting is now done before validation in validate_name()
        """
        # Normalize newlines and tabs to spaces
        name = re.sub(r"[\n\r\t]+", " ", name)
        # Collapse multiple spaces to single space
        name = re.sub(r"\s+", " ", name)
        return name.strip()

    def _categorize_characters(self, text: str) -> str:
        """
        Categorize unexpected characters without exposing actual content.
        Safe for use in error messages to prevent log injection.
        """
        checks = {
            "angle_brackets": "<>",
            "brackets": "[]{}",
            "special_punctuation": ";:",
            "control_characters": "|\\/$",
            "special_symbols": "@#%*+=~`^_",
            "quotes": '"',
        }

        categories = [
            name for name, chars in checks.items() if any(c in text for c in chars)
        ]

        if re.search(r"[^\x20-\x7E]", text):
            categories.append("non_printable")

        # Catch-all for characters not in SAFE_NAME_PATTERN
        if not categories and re.search(r"[^a-zA-Z0-9\s\-'&.,()]", text):
            categories.append("disallowed_characters")

        return ", ".join(categories) if categories else "unknown"
