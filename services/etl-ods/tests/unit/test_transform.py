from pipeline.transform import transfrom_into_payload
from pipeline.validators import (
    ContactItem,
    ContactTypeEnum,
    OrganisationValidator,
    RoleItem,
    RoleList,
    RolesValidator,
)


def setup_organisation_data(
    status: str, contact: ContactItem, roles: RoleItem
) -> OrganisationValidator:
    test_contacts = contact
    test_roles = RoleList(Role=roles)

    return OrganisationValidator(
        Name="Test Organisation",
        Status=status,
        Contact=test_contacts,
        Roles=test_roles,
    )


def setup_role_data(display_name: str) -> RolesValidator:
    return RolesValidator(displayName=display_name)


def test_transfrom_into_payload_activity_active() -> None:
    contact = ContactItem(type=ContactTypeEnum.tel, value="123456789")

    role_items = [
        RoleItem(id="1", primaryRole=True),
    ]

    organisation_data = setup_organisation_data("Active", contact, role_items)
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
    contact = ContactItem(type=ContactTypeEnum.tel, value="123456789")
    role_items = [
        RoleItem(id="RO123", primaryRole=True),
    ]

    organisation_data = setup_organisation_data("Inactive", contact, role_items)
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


def test_transfrom_into_payload_no_contacts() -> None:
    contact = None
    role_items = [
        RoleItem(id="RO123", primaryRole=True),
    ]

    organisation_data = setup_organisation_data("Active", contact, role_items)
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
