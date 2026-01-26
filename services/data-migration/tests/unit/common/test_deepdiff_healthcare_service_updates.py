"""Tests for HealthcareService update expressions in DeepDiffToDynamoDBConverter."""

from datetime import time
from uuid import UUID

import pytest
from ftrs_data_layer.domain import (
    HealthcareService,
    HealthcareServiceTelecom,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.availability import AvailableTime
from ftrs_data_layer.domain.enums import DayOfWeek, HealthcareServiceType

from common.diff_utils import (
    deepdiff_to_dynamodb_expressions,
    get_healthcare_service_diff,
)


class TestHealthcareServiceUpdates:
    def test_name_change(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        modified = base_healthcare_service.model_copy(
            update={"name": "New Service Name"}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_name = :val_0"
        assert result.expression_attribute_names == {"#attr_name": "name"}
        assert result.expression_attribute_values == {
            ":val_0": {"S": "New Service Name"}
        }

    def test_category_change(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        modified = base_healthcare_service.model_copy(
            update={"category": "Other Category"}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #category = :val_0"
        assert result.expression_attribute_names == {"#category": "category"}
        assert result.expression_attribute_values == {":val_0": {"S": "Other Category"}}

    def test_type_change(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        modified = base_healthcare_service.model_copy(
            update={"type": HealthcareServiceType.PCN_SERVICE}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_type = :val_0"
        assert result.expression_attribute_names == {"#attr_type": "type"}
        assert result.expression_attribute_values == {
            ":val_0": {"S": HealthcareServiceType.PCN_SERVICE.value}
        }

    def test_telecom_field_change(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        new_telecom = HealthcareServiceTelecom(
            phone_public="9999999999",
            phone_private="8888888888",
            email="new@example.com",
            web="https://new.example.com",
        )
        modified = base_healthcare_service.model_copy(update={"telecom": new_telecom})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert len(result.expression_attribute_values) == 4  # noqa: PLR2004

        assert "telecom" in result.expression_attribute_names.values()

        mapped_fields = set(result.expression_attribute_names.values())
        expected_fields = {"telecom", "phone_public", "phone_private", "email", "web"}
        assert expected_fields == mapped_fields

        values_list = list(result.expression_attribute_values.values())
        assert {"S": "9999999999"} in values_list
        assert {"S": "8888888888"} in values_list
        assert {"S": "new@example.com"} in values_list
        assert {"S": "https://new.example.com"} in values_list

    def test_single_telecom_field_change(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        new_telecom = base_healthcare_service.telecom.model_copy(
            update={"phone_public": "5555555555"}
        )
        modified = base_healthcare_service.model_copy(update={"telecom": new_telecom})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #telecom.#phone_public = :val_0"
        assert result.expression_attribute_names == {
            "#telecom": "telecom",
            "#phone_public": "phone_public",
        }
        assert result.expression_attribute_values == {":val_0": {"S": "5555555555"}}

    def test_add_dispositions(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        modified = base_healthcare_service.model_copy(
            update={"dispositions": ["DX1", "DX2", "DX3"]}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #dispositions = :val_0"
        assert result.expression_attribute_names == {"#dispositions": "dispositions"}
        assert result.expression_attribute_values == {
            ":val_0": {"L": [{"S": "DX1"}, {"S": "DX2"}, {"S": "DX3"}]}
        }

    def test_remove_dispositions(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        service_with_dispositions = base_healthcare_service.model_copy(
            update={"dispositions": ["DX1", "DX2", "DX3"]}
        )
        modified = service_with_dispositions.model_copy(
            update={"dispositions": ["DX1"]}
        )
        diff = get_healthcare_service_diff(service_with_dispositions, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #dispositions = :val_0"
        assert result.expression_attribute_names == {"#dispositions": "dispositions"}
        assert result.expression_attribute_values == {":val_0": {"L": [{"S": "DX1"}]}}

    def test_modify_dispositions(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        service_with_dispositions = base_healthcare_service.model_copy(
            update={"dispositions": ["DX1", "DX2"]}
        )
        modified = service_with_dispositions.model_copy(
            update={"dispositions": ["DX1", "DX999"]}
        )
        diff = get_healthcare_service_diff(service_with_dispositions, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #dispositions[1] = :val_0"
        assert result.expression_attribute_names == {"#dispositions": "dispositions"}
        assert result.expression_attribute_values == {":val_0": {"S": "DX999"}}

    def test_add_symptom_group_discriminators(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        sgsd = SymptomGroupSymptomDiscriminatorPair(sg=1000, sd=4003)
        modified = base_healthcare_service.model_copy(
            update={"symptomGroupSymptomDiscriminators": [sgsd]}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert (
            result.update_expression
            == "SET #symptomGroupSymptomDiscriminators = :val_0"
        )
        assert result.expression_attribute_names == {
            "#symptomGroupSymptomDiscriminators": "symptomGroupSymptomDiscriminators"
        }

        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 1

        expected_sgsd = {"M": {"sg": {"N": "1000"}, "sd": {"N": "4003"}}}
        assert val["L"][0] == expected_sgsd

    def test_modify_symptom_group_discriminators(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        sgsd1 = SymptomGroupSymptomDiscriminatorPair(sg=1000, sd=4003)
        sgsd2 = SymptomGroupSymptomDiscriminatorPair(sg=2000, sd=5003)
        service_with_sgsd = base_healthcare_service.model_copy(
            update={"symptomGroupSymptomDiscriminators": [sgsd1]}
        )
        modified = service_with_sgsd.model_copy(
            update={"symptomGroupSymptomDiscriminators": [sgsd2]}
        )
        diff = get_healthcare_service_diff(service_with_sgsd, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert "#symptomGroupSymptomDiscriminators" in result.update_expression
        assert len(result.expression_attribute_values) == 2  # noqa: PLR2004
        values_list = list(result.expression_attribute_values.values())
        assert {"N": "2000"} in values_list
        assert {"N": "5003"} in values_list

    def test_add_opening_times(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        opening_time = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time(9, 0),
            endTime=time(17, 0),
        )
        modified = base_healthcare_service.model_copy(
            update={"openingTime": [opening_time]}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #openingTime = :val_0"
        assert result.expression_attribute_names == {"#openingTime": "openingTime"}

        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 1

        opening_map = val["L"][0]["M"]
        assert "dayOfWeek" in opening_map
        assert "startTime" in opening_map
        assert "endTime" in opening_map

        assert opening_map["dayOfWeek"] == {"S": DayOfWeek.MONDAY.value}
        assert opening_map["startTime"] == {"S": "09:00:00"}
        assert opening_map["endTime"] == {"S": "17:00:00"}

    def test_modify_opening_times(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        opening_time1 = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time(9, 0),
            endTime=time(17, 0),
        )
        opening_time2 = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time(8, 0),
            endTime=time(18, 0),
        )
        service_with_times = base_healthcare_service.model_copy(
            update={"openingTime": [opening_time1]}
        )
        modified = service_with_times.model_copy(
            update={"openingTime": [opening_time2]}
        )
        diff = get_healthcare_service_diff(service_with_times, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert "#openingTime" in result.update_expression
        assert len(result.expression_attribute_values) == 2  # noqa: PLR2004
        values_list = list(result.expression_attribute_values.values())
        assert {"S": "08:00:00"} in values_list
        assert {"S": "18:00:00"} in values_list

    def test_provided_by_change(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        new_org = UUID("88888888-8888-8888-8888-888888888888")
        modified = base_healthcare_service.model_copy(update={"providedBy": new_org})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #providedBy = :val_0"
        assert result.expression_attribute_names == {"#providedBy": "providedBy"}
        assert result.expression_attribute_values == {
            ":val_0": {"S": "88888888-8888-8888-8888-888888888888"}
        }

    def test_location_reference_change(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        new_loc = UUID("77777777-7777-7777-7777-777777777777")
        modified = base_healthcare_service.model_copy(update={"location": new_loc})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_location = :val_0"
        assert result.expression_attribute_names == {"#attr_location": "location"}
        assert result.expression_attribute_values == {
            ":val_0": {"S": "77777777-7777-7777-7777-777777777777"}
        }

    def test_midnight_opening_time(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        midnight_opening = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time(0, 0, 0),
            endTime=time(23, 59, 59),
        )
        modified = base_healthcare_service.model_copy(
            update={"openingTime": [midnight_opening]}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        val = result.expression_attribute_values[":val_0"]
        opening_map = val["L"][0]["M"]
        assert opening_map["startTime"] == {"S": "00:00:00"}
        assert opening_map["endTime"] == {"S": "23:59:59"}

    @pytest.mark.parametrize(
        ("day_enum", "expected_value"),
        [
            (DayOfWeek.MONDAY, "mon"),
            (DayOfWeek.TUESDAY, "tue"),
            (DayOfWeek.WEDNESDAY, "wed"),
            (DayOfWeek.THURSDAY, "thu"),
            (DayOfWeek.FRIDAY, "fri"),
            (DayOfWeek.SATURDAY, "sat"),
            (DayOfWeek.SUNDAY, "sun"),
        ],
    )
    def test_day_of_week_serialization(
        self,
        base_healthcare_service: HealthcareService,
        day_enum: DayOfWeek,
        expected_value: str,
    ) -> None:
        opening = AvailableTime(
            dayOfWeek=day_enum, startTime=time(9, 0), endTime=time(17, 0)
        )
        modified = base_healthcare_service.model_copy(update={"openingTime": [opening]})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        actual_day = result.expression_attribute_values[":val_0"]["L"][0]["M"][
            "dayOfWeek"
        ]["S"]
        assert actual_day == expected_value

    def test_large_sgsd_values(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        large_sgsd = SymptomGroupSymptomDiscriminatorPair(sg=99999, sd=99999)
        modified = base_healthcare_service.model_copy(
            update={"symptomGroupSymptomDiscriminators": [large_sgsd]}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        val = result.expression_attribute_values[":val_0"]
        expected = {"M": {"sg": {"N": "99999"}, "sd": {"N": "99999"}}}
        assert val["L"][0] == expected

    def test_multiple_opening_times_same_day(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        morning = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time(9, 0),
            endTime=time(12, 0),
        )
        afternoon = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time(14, 0),
            endTime=time(17, 0),
        )
        modified = base_healthcare_service.model_copy(
            update={"openingTime": [morning, afternoon]}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        val = result.expression_attribute_values[":val_0"]
        assert len(val["L"]) == 2  # noqa: PLR2004
        assert val["L"][0]["M"]["dayOfWeek"] == val["L"][1]["M"]["dayOfWeek"]
        assert val["L"][0]["M"]["startTime"] != val["L"][1]["M"]["startTime"]

    def test_url_with_special_characters(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        complex_url = "https://example.com/path?param1=value1&param2=value%202"
        new_telecom = base_healthcare_service.telecom.model_copy(
            update={"web": complex_url}
        )
        modified = base_healthcare_service.model_copy(update={"telecom": new_telecom})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        values_list = list(result.expression_attribute_values.values())
        assert {"S": complex_url} in values_list

    def test_email_with_plus_sign(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        email_with_plus = "contact+urgent@nhs.net"
        new_telecom = base_healthcare_service.telecom.model_copy(
            update={"email": email_with_plus}
        )
        modified = base_healthcare_service.model_copy(update={"telecom": new_telecom})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        values_list = list(result.expression_attribute_values.values())
        assert {"S": email_with_plus} in values_list

    def test_empty_list_value(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        service_with_dispositions = base_healthcare_service.model_copy(
            update={"dispositions": ["DX1"]}
        )
        modified = service_with_dispositions.model_copy(update={"dispositions": []})

        diff = get_healthcare_service_diff(service_with_dispositions, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #dispositions = :val_0"
        assert result.expression_attribute_values == {":val_0": {"L": []}}
