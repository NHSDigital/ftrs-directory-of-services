from pipeline.transform import transfrom_into_payload
from pipeline.validators import (
    ContactItem,
    ContactList,
    ContactTypeEnum,
    OrganisationValidator,
    RoleItem,
    RoleList,
    RolesValidator,
)


def setup_organisation_data(
    status: str, contacts: ContactItem, roles: RoleItem
) -> OrganisationValidator:
    test_contacts = ContactList(Contact=contacts)
    test_roles = RoleList(Role=roles)

    return OrganisationValidator(
        Name="Test Organisation",
        Status=status,
        Contacts=test_contacts,
        Roles=test_roles,
    )


def setup_role_data(display_name: str) -> RolesValidator:
    return RolesValidator(displayName=display_name)


def test_transfrom_into_payload_activity_active() -> None:
    contact_items = [
        ContactItem(type=ContactTypeEnum.tel, value="123456789"),
        ContactItem(type="http", value="http://example.com"),
    ]
    role_items = [
        RoleItem(id="1", primaryRole=True),
    ]

    organisation_data = setup_organisation_data("Active", contact_items, role_items)
    role_data = setup_role_data("Primary Role")

    expected_payload = {
        "active": True,
        "name": "Test Organisation",
        "telecom": "123456789",
        "type": "Primary Role",
        "modified_by": "ODS_ETL_PIPELINE",
    }

    result = transfrom_into_payload(organisation_data, role_data)
    assert result == expected_payload


def test_transfrom_into_payload_activity_inactive() -> None:
    contact_items = [
        ContactItem(type=ContactTypeEnum.tel, value="123456789"),
    ]
    role_items = [
        RoleItem(id="RO123", primaryRole=True),
    ]

    organisation_data = setup_organisation_data("Inactive", contact_items, role_items)
    role_data = setup_role_data("Primary Role")

    expected_payload = {
        "active": False,
        "name": "Test Organisation",
        "telecom": "123456789",
        "type": "Primary Role",
        "modified_by": "ODS_ETL_PIPELINE",
    }

    result = transfrom_into_payload(organisation_data, role_data)
    assert result == expected_payload


def test_transfrom_into_payload_no_tel() -> None:
    contact_items = [
        ContactItem(type=ContactTypeEnum.http, value="http://example.com"),
    ]
    role_items = [
        RoleItem(id="RO123", primaryRole=True),
    ]

    organisation_data = setup_organisation_data("Active", contact_items, role_items)
    role_data = setup_role_data("Primary Role")

    expected_payload = {
        "active": True,
        "name": "Test Organisation",
        "telecom": None,
        "type": "Primary Role",
        "modified_by": "ODS_ETL_PIPELINE",
    }

    result = transfrom_into_payload(organisation_data, role_data)
    assert result == expected_payload


def test_transfrom_into_payload_no_contacts() -> None:
    contact_items = []
    role_items = [
        RoleItem(id="RO123", primaryRole=True),
    ]

    organisation_data = setup_organisation_data("Active", contact_items, role_items)
    role_data = setup_role_data("Primary Role")

    expected_payload = {
        "active": True,
        "name": "Test Organisation",
        "telecom": None,
        "type": "Primary Role",
        "modified_by": "ODS_ETL_PIPELINE",
    }

    result = transfrom_into_payload(organisation_data, role_data)
    assert result == expected_payload
