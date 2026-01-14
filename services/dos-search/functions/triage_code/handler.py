"""Triage code endpoint Lambda.

This is a placeholder implementation until the endpoint contract is finalised.
It returns 501 Not Implemented.

Once the contract is agreed, replace this with real handler logic and (optionally)
move any shared code into `functions.libraries`.
"""

from __future__ import annotations

from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    _ = context
    return {
        "statusCode": 501,
        "headers": {"Content-Type": "application/json"},
        "body": '{"message":"triage_code endpoint not implemented"}',
    }
