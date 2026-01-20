"""Organization endpoint Lambda.

This is the endpoint Lambda deployed for `GET /Organization`.

It currently delegates to the existing shared implementation.
"""

from __future__ import annotations

from aws_lambda_powertools.utilities.typing import LambdaContext

from functions.libraries.dos_search_ods_code_function import (
    lambda_handler as _lambda_handler,
)


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return _lambda_handler(event, context)
