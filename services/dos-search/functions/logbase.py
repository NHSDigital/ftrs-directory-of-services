from logging import ERROR, INFO, WARNING

from ftrs_common.logger import LogBase, LogReference


class DosSearchLogBase(LogBase):
    """
    LogBase for DoS Search service operations.
    """

    DOS_SEARCH_001 = LogReference(
        level=INFO,
        message="Logging one-time fields from Request",
    )
    DOS_SEARCH_002 = LogReference(
        level=INFO,
        message="Received request for odsCode",
    )
    DOS_SEARCH_003 = LogReference(
        level=INFO,
        message="Successfully processed request: Logging response time & size",
    )
    DOS_SEARCH_004 = LogReference(
        level=INFO,
        message="Creating response",
    )
    DOS_SEARCH_005 = LogReference(
        level=WARNING,
        message="Validation error occurred: Logging response time & size",
    )
    DOS_SEARCH_006 = LogReference(
        level=ERROR,
        message="Internal server error occurred: Logging response time & size",
        exc_info=True,
    )
    DOS_SEARCH_007 = LogReference(
        level=INFO,
        message="Retrieving organisation by ods_code",
    )
    DOS_SEARCH_008 = LogReference(
        level=INFO,
        message="Mapping organisation to fhir_bundle",
    )
    DOS_SEARCH_009 = LogReference(
        level=ERROR,
        message="Error occurred while retrieving or mapping organisation data",
        exc_info=True,
    )
    DOS_SEARCH_010 = LogReference(
        level=ERROR,
        message="Failed to calculate response size",
    )
    DOS_SEARCH_011 = LogReference(
        level=WARNING,
        message="Unknown business scenario value; endpoint business scenario extension omitted",
    )
    DOS_SEARCH_012 = LogReference(
        level=INFO,
        message="Received request for healthcare service",
    )
    DOS_SEARCH_013 = LogReference(
        level=WARNING,
        message="Service unavailable - Healthcare Service search endpoint is disabled via feature flag",
    )
    DOS_SEARCH_014 = LogReference(
        level=INFO,
        message="Healthcare Service search endpoint is enabled via feature flag",
    )
    DOS_SEARCH_015 = LogReference(
        level=INFO,
        message="Received request for triage code",
    )
    DOS_SEARCH_016 = LogReference(
        level=WARNING,
        message="Service unavailable - Triage code search endpoint is disabled via feature flag",
    )
    DOS_SEARCH_017 = LogReference(
        level=INFO,
        message="Triage code search endpoint is enabled via feature flag",
    )
    DOS_SEARCH_018 = LogReference(
        level=WARNING,
        message="Triage code search endpoint is not yet implemented",
    )
