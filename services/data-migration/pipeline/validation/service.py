from ftrs_data_layer.domain.legacy import Service

from pipeline.validation.base import (
    FieldValidationResult,
    ValidationIssue,
    ValidationResult,
    Validator,
)


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

        if nonpublicphone_result := self.validate_phone_number(data.nonpublicphone):
            data.nonpublicphone = nonpublicphone_result.sanitised
            validation_result.issues.extend(nonpublicphone_result.issues)

        return validation_result


class GPPracticeValidator(ServiceValidator):
    def validate(self, data: Service) -> ValidationResult[Service]:
        result = super().validate(data)

        if name_result := self.validate_name(data.publicname):
            data.publicname = name_result.sanitised
            result.issues.extend(name_result.issues)

        return result

    def validate_name(self, name: str) -> FieldValidationResult[str]:
        result = FieldValidationResult(
            original=name,
            sanitised=None,
            issues=[],
        )

        if not name:
            result.issues.append(
                ValidationIssue(
                    severity="error",
                    code="publicname_required",
                    diagnostics="Public name is required for GP practices",
                    expression=["publicname"],
                )
            )
            return result

        cleaned_name = name.split("-", maxsplit=1)[0].rstrip()
        result.sanitised = cleaned_name
        return result
