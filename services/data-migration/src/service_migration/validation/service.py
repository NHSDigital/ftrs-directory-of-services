import html
import re

from ftrs_data_layer.domain.legacy.service import Service
from ftrs_data_layer.logbase import UtilsLogBase

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
    # Maximum allowed length for practice names
    MAX_NAME_LENGTH = 100

    # Dangerous patterns for injection attacks (checked before decoding for defense in depth)
    # Catches: script injection, event handlers, protocol handlers, HTML tags, comments
    DANGEROUS_PATTERNS = re.compile(
        r"javascript:|data:|vbscript:|file:|about:"
        r"|on\w+\s*="
        r"|<\s*script|</\s*script|<\s*iframe|<\s*object|<\s*embed"
        r"|<!--|-->"
        r"|<!\[CDATA\[",
        re.IGNORECASE,
    )

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
        - Validates BEFORE decoding to catch injection attacks (dangerous patterns)
        - Decodes all HTML entities using Python's html.unescape()
        - Rejects ANY nested encoding after decoding
        - Rejects (error) instead of warning for suspicious content

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

        # Remove GP prefix variations
        name = self._remove_gp_prefix(name)

        # Apply hyphen-splitting business rule with logging
        name = self._apply_hyphen_splitting(name, full_original)
        if not name:
            return self._error(
                "publicname_empty_after_sanitization",
                "Name is empty after removing suffix",
            )

        # Decode HTML entities
        try:
            decoded_name = self._decode_html_entities(name)
        except ValueError:
            self.logger.log(UtilsLogBase.UTILS_GP_PRACTICE_VALIDATOR_002)
            return self._error(
                "publicname_suspicious_encoding",
                "Name contains disallowed HTML entities",
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

    def _remove_gp_prefix(self, name: str) -> str:
        """
        Remove GP prefix variations from the start of the name.

        Args:
            name: The practice name

        Returns:
            Name with GP prefix removed if present
        """
        gp_prefixes = ["GP - ", "GP -", "GP- ", "GP-"]
        for prefix in gp_prefixes:
            if name.startswith(prefix):
                return name[len(prefix) :].strip()
        return name

    def _apply_hyphen_splitting(self, name: str, full_original: str) -> str:
        """
        Apply hyphen-splitting business rule.

        Splits on ' - ' and keeps only the first part.
        Logs when suffix is discarded for monitoring/security purposes.

        Args:
            name: The name to split
            full_original: The original name before any processing (for logging)

        Returns:
            First part of the name after splitting
        """
        split_name = name.split(" - ", maxsplit=1)[0].strip()

        # Log when suffix is discarded for monitoring/security purposes
        if " - " in full_original:
            self.logger.log(
                UtilsLogBase.UTILS_GP_PRACTICE_VALIDATOR_001,
                original_length=len(full_original),
                sanitized_length=len(split_name),
            )

        return split_name

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
            self.logger.log(
                UtilsLogBase.UTILS_GP_PRACTICE_VALIDATOR_004,
                max_chars=self.MAX_NAME_LENGTH,
            )
            return self._error(
                "publicname_too_long",
                f"Name exceeds maximum length of {self.MAX_NAME_LENGTH} characters",
            )

        # Check for dangerous patterns BEFORE decoding (catch injection attacks)
        if self.DANGEROUS_PATTERNS.search(name):
            self.logger.log(UtilsLogBase.UTILS_GP_PRACTICE_VALIDATOR_005)
            return self._error(
                "publicname_dangerous_pattern",
                "Name contains dangerous patterns that could lead to injection attacks",
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

    def _decode_html_entities(self, name: str) -> str:
        """
        Decode all HTML entities using Python's html.unescape().

        Security measures:
        - Decodes all standard HTML entities (named and numeric)
        - Detects nested encoding after decoding

        Args:
            name: String potentially containing HTML entities

        Returns:
            String with all HTML entities decoded

        Raises:
            ValueError: If nested encoding is detected after decoding
        """
        # Decode all HTML entities using Python's built-in decoder
        decoded = html.unescape(name)

        # Check for nested encoding by looking for entity patterns in decoded output
        # This catches cases like &amp;#39; which would decode to &#39;
        entity_pattern = re.compile(r"&(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);")
        if entity_pattern.search(decoded):
            raise ValueError("Nested HTML entity encoding detected")

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
