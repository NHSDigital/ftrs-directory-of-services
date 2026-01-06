import json

from common.auth import get_jwt_authenticator
from common.http_client import build_headers, make_request


def make_apim_request(
    url: str,
    method: str = "GET",
    params: dict | None = None,
    jwt_required: bool = True,
    **kwargs: dict,
) -> dict:
    """Make a request to the APIM API."""
    json_data = kwargs.get("json")
    json_string = json.dumps(json_data) if json_data is not None else None

    auth_headers = None
    if jwt_required:
        jwt_auth = get_jwt_authenticator()
        auth_headers = jwt_auth.get_auth_headers()

    headers = build_headers(
        json_data=json_data,
        json_string=json_string,
        auth_headers=auth_headers,
    )

    return make_request(
        url=url,
        method=method,
        params=params,
        headers=headers,
        **kwargs,
    )
