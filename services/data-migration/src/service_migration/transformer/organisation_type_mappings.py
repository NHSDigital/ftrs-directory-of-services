from ftrs_data_layer.domain.enums import OrganisationType

SERVICE_TYPE_TO_ORGANISATION_TYPE: dict[int, OrganisationType] = {
    100: OrganisationType.GP_PRACTICE,
    13: OrganisationType.COMMUNITY_PHARMACY,
    134: OrganisationType.DISTANCE_SELLING_PHARMACY,
}
