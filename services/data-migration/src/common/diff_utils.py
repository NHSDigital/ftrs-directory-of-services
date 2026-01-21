import deepdiff
from ftrs_data_layer.domain import HealthcareService, Location, Organisation


def get_organisation_diff(
    previous: Organisation, current: Organisation
) -> deepdiff.DeepDiff:
    """
    Get the differences between two Organisation records.
    """
    diff = deepdiff.DeepDiff(
        previous.model_dump(),
        current.model_dump(),
        ignore_order=True,
        exclude_paths=["root['createdDateTime']", "root['modifiedDateTime']"],
        exclude_regex_paths=[
            r"root\['endpoints'\]\[\d+\]\['createdDateTime'\]",
            r"root\['endpoints'\]\[\d+\]\['modifiedDateTime'\]",
        ],
        view="tree",
        threshold_to_diff_deeper=0,
    )
    return diff


def get_location_diff(previous: Location, current: Location) -> deepdiff.DeepDiff:
    """
    Get the differences between two Location records.
    """
    diff = deepdiff.DeepDiff(
        previous.model_dump(),
        current.model_dump(),
        ignore_order=True,
        exclude_paths=["root['createdDateTime']", "root['modifiedDateTime']"],
        view="tree",
        threshold_to_diff_deeper=0,
    )
    return diff


def get_healthcare_service_diff(
    previous: HealthcareService,
    current: HealthcareService,
) -> deepdiff.DeepDiff:
    """
    Get the differences between two HealthcareService records.
    """
    diff = deepdiff.DeepDiff(
        previous.model_dump(),
        current.model_dump(),
        ignore_order=True,
        exclude_paths=["root['createdDateTime']", "root['modifiedDateTime']"],
        view="tree",
        threshold_to_diff_deeper=0,
    )
    return diff
