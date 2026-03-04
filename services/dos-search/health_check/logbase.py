from logging import WARNING

from ftrs_common.logger import LogBase, LogReference


class DosSearchHealthLogBase(LogBase):
    """
    LogBase for DoS Search health check operations.
    """

    DOS_SEARCH_HEALTH_001 = LogReference(
        level=WARNING,
        message="Health check failed",
        exc_info=True,
    )
