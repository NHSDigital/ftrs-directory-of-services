"""Seed database with GP organisation test data."""
from ftrs_data_layer.domain import legacy

gp_service = [
    legacy.Service(
        id=1,
        uid="service-1",  # Add the required uid field
        name="Greenway Medical Centre",
        typeid=1,  # Add required typeid field
        openallhours=False,
        restricttoreferrals=False,
        postcode="SW1A 1AA",
        address="123 Medical Street",
        town="London",
        web="https://greenwaymedical.nhs.uk",
        email="enquiries@greenwaymedical.nhs.uk",
        publicphone="020 7946 0958",
    ),
    legacy.Service(
        id=2,
        uid="service-2",  # Add the required uid field
        name="Riverside Health Centre",
        typeid=1,  # Add required typeid field
        openallhours=False,
        restricttoreferrals=False,
        postcode="M1 1AA",
        address="456 River Road",
        town="Manchester",
        web="https://riversidehealth.nhs.uk",
        email="reception@riversidehealth.nhs.uk",
        publicphone="0161 496 0123",
    ),
    legacy.Service(
        id=3,
        uid="service-3",  # Add the required uid field
        name="Hillside Surgery",
        typeid=1,  # Add required typeid field
        openallhours=False,
        restricttoreferrals=False,
        postcode="B1 1AA",
        address="789 Hill Avenue",
        town="Birmingham",
        web="https://hillsidesurgery.nhs.uk",
        email="admin@hillsidesurgery.nhs.uk",
        publicphone="0121 496 0789",
    )
]
