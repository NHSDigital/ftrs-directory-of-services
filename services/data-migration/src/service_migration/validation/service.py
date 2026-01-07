from ftrs_data_layer.domain.legacy.data_models import ServiceData

from common.logbase import ServiceMigrationLogBase
from service_migration.formatting.address_formatter import format_address
from service_migration.validation.base import (
    FieldValidationResult,
    ValidationResult,
    Validator,
)
from service_migration.validation.types import ValidationIssue


class ServiceValidator(Validator[ServiceData]):
    """
    Generic service validator for all service records
    Should be expanded/subclassed if required for specific service types
    """

    def validate(self, data: ServiceData) -> ValidationResult[ServiceData]:
        """
        Run validation over the service.

        Runs:
        - Email validation
        - Phone number validation (publicphone)
        """
        self.deps.logger.log(
            ServiceMigrationLogBase.SM_VAL_001,
            validator_name=self.__class__.__name__,
        )

        validation_result = ValidationResult[ServiceData](
            origin_record_id=data.id,
            issues=[],
            sanitised=data.model_copy(deep=True),
        )

        if email_result := self.validate_email(data.email):
            validation_result.sanitised.email = email_result.sanitised
            self.add_issues(validation_result, email_result.issues)

        if publicphone_result := self.validate_phone_number(data.publicphone):
            validation_result.sanitised.publicphone = publicphone_result.sanitised
            self.add_issues(validation_result, publicphone_result.issues)

        if nonpublicphone_result := self.validate_phone_number(
            data.nonpublicphone,
            expression="nonpublicphone",
        ):
            validation_result.sanitised.nonpublicphone = nonpublicphone_result.sanitised
            self.add_issues(validation_result, nonpublicphone_result.issues)

        return validation_result

    def add_issues(
        self,
        validation_result: ValidationResult[ServiceData],
        issues: list[ValidationIssue],
    ) -> None:
        """
        Add issues to a validation result
        """
        for issue in issues:
            self.deps.logger.log(
                ServiceMigrationLogBase.SM_VAL_002,
                **issue.model_dump(mode="json"),
            )
            validation_result.issues.append(issue)


class GPPracticeValidator(ServiceValidator):
    def validate(self, data: ServiceData) -> ValidationResult[ServiceData]:
        result = super().validate(data)

        if name_result := self.validate_name(data.publicname):
            result.sanitised.publicname = name_result.sanitised
            self.add_issues(result, name_result.issues)

        if location_result := self.validate_location(
            data.address, data.town, data.postcode
        ):
            self.add_issues(result, location_result.issues)

        return result

    def validate_name(self, name: str) -> FieldValidationResult[str]:
        result = FieldValidationResult(
            original=name,
            sanitised=None,
            issues=[],
        )

        if not name or not name.strip():
            result.issues.append(
                ValidationIssue(
                    value=name,
                    severity="fatal",
                    code="publicname_required",
                    diagnostics="Public name is required for GP practices",
                    expression=["publicname"],
                )
            )
            return result

        cleaned_name = name.split("-", maxsplit=1)[0].rstrip()
        result.sanitised = cleaned_name
        return result

    def validate_location(
        self, address: str, town: str, postcode: str
    ) -> FieldValidationResult[str]:
        """
        Validate location using address, town, and postcode.

        Returns formatted address if at least town or postcode is available,
        even if address field is missing or invalid.
        """
        result = FieldValidationResult(
            original=(address, town, postcode),
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

        return result
