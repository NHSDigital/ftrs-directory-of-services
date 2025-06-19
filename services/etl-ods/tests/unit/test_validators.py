import pytest
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pydantic import ValidationError

from pipeline.validators import (
    ContactItem,
    ContactTypeEnum,
    OrganisationValidator,
    RoleItem,
    RoleList,
    RolesValidator,
    StatusEnum,
    validate_payload,
)


def test_contact_item_valid() -> None:
    contact = ContactItem(type=ContactTypeEnum.tel, value="123456789")
    assert contact.type == ContactTypeEnum.tel
    assert contact.value == "123456789"


def test_contact_item_strip_whitespace() -> None:
    contact = ContactItem(type=ContactTypeEnum.tel, value=" 123 456 789 ")
    assert contact.value == "123456789"


def test_contact_item_invalid_length() -> None:
    with pytest.raises(ValidationError, match="20"):
        ContactItem(type=ContactTypeEnum.tel, value="1" * 21)


def test_role_item_valid() -> None:
    role = RoleItem(id="123", primaryRole=True)
    assert role.id == "123"
    assert role.primaryRole is True


def test_role_item_invalid_id_length() -> None:
    with pytest.raises(ValidationError):
        RoleItem(id="12345678901", primaryRole=True)


def test_role_list_valid() -> None:
    roles = RoleList(
        Role=[
            RoleItem(id="123", primaryRole=True),
            RoleItem(id="456", primaryRole=False),
        ]
    )
    assert str(len(roles.Role)) == "2"
    assert roles.Role[0].id == "123"
    assert roles.Role[0].primaryRole is True
    assert roles.Role[1].id == "456"
    assert roles.Role[1].primaryRole is False


def test_organisation_validator_valid() -> None:
    organisation = OrganisationValidator(
        Name="Test Organisation",
        Status=StatusEnum.active,
        Roles=RoleList(
            Role=[
                RoleItem(id="123", primaryRole=True),
                RoleItem(id="456", primaryRole=False),
            ]
        ),
        Contact=ContactItem(type=ContactTypeEnum.tel, value="123456789"),
    )
    assert organisation.Name == "Test Organisation"
    assert organisation.Status == StatusEnum.active
    assert str(len(organisation.Roles.Role)) == "2"
    assert organisation.Contact.type == ContactTypeEnum.tel
    assert organisation.Contact.value == "123456789"


def test_organisation_validator_valid_no_contacts() -> None:
    organisation = OrganisationValidator(
        Name="Test Organisation",
        Status=StatusEnum.active,
        Roles=RoleList(
            Role=[
                RoleItem(id="123", primaryRole=True),
                RoleItem(id="456", primaryRole=False),
            ]
        ),
        Contact=None,
    )
    assert organisation.Contact is None


def test_organisation_validator_valid_non_primary_role_default() -> None:
    organisation = OrganisationValidator(
        Name="Test Organisation",
        Status=StatusEnum.active,
        Roles=RoleList(
            Role=[
                RoleItem(id="123", primaryRole=True),
                RoleItem(id="456"),
            ]
        ),
        Contact=None,
    )
    assert str(len(organisation.Roles.Role)) == "2"
    assert not organisation.Roles.Role[1].primaryRole


def test_roles_validator_valid() -> None:
    role = RolesValidator(displayName="Primary Role")
    assert role.displayName == "Primary Role"


def test_roles_validator_invalid_display_name_max_length() -> None:  # check min
    with pytest.raises(ValidationError):
        RolesValidator(displayName="A" * 101)


def test_validate_payload_missing_required_field() -> None:
    payload = {
        "Status": "Active",
        "Roles": {"Role": [{"id": "RO123", "primaryRole": True}]},
        "Contact": {"type": "tel", "value": "1234567890"},
    }

    with pytest.raises(ValidationError) as e:
        validate_payload(payload, OrganisationValidator)

    assert "Field required" in str(e.value)
    assert "Name" in str(e.value)


def test_validate_payload_logs_error(caplog: pytest.LogCaptureFixture) -> None:
    payload = {
        "Name": "Test Organisation",
        "Status": "Active",
        "Roles": {"Role": [{"id": "RO123", "primaryRole": True}]},
        "Contact": {"type": "tel", "value": "1" * 21},
    }

    with pytest.raises(ValidationError):
        validate_payload(payload, OrganisationValidator)

    expected_failed_log = OdsETLPipelineLogBase.ETL_PROCESSOR_019.value.message.split(
        "{error_message}"
    )[0]
    assert expected_failed_log in caplog.text
