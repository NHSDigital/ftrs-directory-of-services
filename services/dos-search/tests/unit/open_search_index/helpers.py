import json
from typing import Any, Optional


def make_resp(
    status_code: int = 200,
    text: str = "",
    headers: Optional[dict] = None,
    json_value: Optional[object] = None,
    raise_json: bool = False,
):
    class Resp:
        def __init__(self):
            self.status_code = status_code
            self._text = text
            self.headers = headers or {}
            self.reason = ""

        @property
        def text(self):
            return self._text

        def json(self):
            if raise_json:
                raise ValueError("bad")
            if json_value is not None:
                return json_value
            if not self._text:
                return {}
            return json.loads(self._text)

    return Resp()


def make_session_with_resp(resp_obj: object):
    class Session:
        @staticmethod
        def request(*_args, **_kwargs):
            return resp_obj

    return Session()


def make_failing_session():
    class Session:
        @staticmethod
        def request(*_args, **_kwargs):
            raise AssertionError("fail")

    return Session()


def make_raising_session(exc: Exception):
    class Session:
        @staticmethod
        def request(*_args, **_kwargs):
            raise exc

    return Session()


def make_text_response(text: str = "ok", raise_on_access: bool = False) -> object:
    if raise_on_access:

        class BadTextResp:
            @property
            def text(self) -> str:
                raise AttributeError("bad")

        return BadTextResp()
    return type("TextResp", (), {"text": text})()


def make_headers_response(headers: dict) -> object:
    return type("R", (), {"headers": headers})()


def index_single_with_session(mod, session_obj, record: Optional[dict] = None):
    rec = record or {"primary_key": "p"}
    return mod.index_single_record(session_obj, "https://ep", "idx", rec)


def index_bulk_with_resp(mod, resp_obj, records):
    return mod.index_bulk(
        make_session_with_resp(resp_obj), "https://ep", "idx", records
    )


def make_add_auth(
    authorization_value: str = "AWS4-HMAC-SHA256 SignedHeaders=host;x-amz-date,Signature=fake",
):
    def _add_auth(_self, aws_request: Any) -> None:
        # ensure headers dict exists and set the Authorization header
        hdrs = getattr(aws_request, "headers", None)
        if hdrs is None:
            setattr(aws_request, "headers", {"Authorization": authorization_value})
        else:
            hdrs["Authorization"] = authorization_value

    return _add_auth


def make_paginator(items_list):
    class Paginator:
        def __init__(self, items):
            self._items = items

        def paginate(self, **kwargs):
            # consume kwargs to avoid unused-parameter warnings from linters
            _ = kwargs
            for page in self._items:
                yield page

    class Client:
        @staticmethod
        def get_paginator(_name):
            return Paginator(items_list)

    return Client()


def make_fake_bulk(delta: int = 0):
    def _fake_bulk(_session, _endpoint, _index_name, chunk):
        total = len(chunk)
        ok = max(total - delta, 0)
        return ok, total

    return _fake_bulk
