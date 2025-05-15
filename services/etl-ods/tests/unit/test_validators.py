import pytest
from pydantic import ValidationError

from pipeline.validators import (
    ContactItem,
    ContactList,
    ContactTypeEnum,
    OrganisationValidator,
    RoleItem,
    RoleList,
    RolesValidator,
    StatusEnum,
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


def test_contact_list_valid() -> None:
    contacts = ContactList(
        Contact=[
            ContactItem(type=ContactTypeEnum.tel, value="123456789"),
            ContactItem(type=ContactTypeEnum.tel, value="987654321"),
        ]
    )
    assert str(len(contacts.Contact)) == "2"
    assert contacts.Contact[0].value == "123456789"
    assert contacts.Contact[1].value == "987654321"


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
        Contacts=ContactList(
            Contact=[
                ContactItem(type=ContactTypeEnum.tel, value="123456789"),
                ContactItem(type=ContactTypeEnum.tel, value="987654321"),
            ]
        ),
    )
    assert organisation.Name == "Test Organisation"
    assert organisation.Status == StatusEnum.active
    assert str(len(organisation.Roles.Role)) == "2"
    assert str(len(organisation.Contacts.Contact)) == "2"


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
        Contacts=None,
    )
    assert organisation.Contacts is None


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
        Contacts=None,
    )
    assert str(len(organisation.Roles.Role)) == "2"
    assert not organisation.Roles.Role[1].primaryRole


def test_roles_validator_valid() -> None:
    role = RolesValidator(displayName="Primary Role")
    assert role.displayName == "Primary Role"


def test_roles_validator_invalid_display_name_max_length() -> None:  # check min
    with pytest.raises(ValidationError):
        RolesValidator(displayName="A" * 101)
