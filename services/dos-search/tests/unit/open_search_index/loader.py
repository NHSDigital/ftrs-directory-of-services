import importlib.util
from pathlib import Path

_helpers_path = Path(__file__).parent / "helpers.py"
_spec = importlib.util.spec_from_file_location(
    "open_search_helpers", str(_helpers_path)
)
_helpers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_helpers)

make_resp = _helpers.make_resp
make_session_with_resp = _helpers.make_session_with_resp
make_failing_session = _helpers.make_failing_session
make_raising_session = _helpers.make_raising_session
make_text_response = _helpers.make_text_response
make_headers_response = _helpers.make_headers_response
index_single_with_session = _helpers.index_single_with_session
index_bulk_with_resp = _helpers.index_bulk_with_resp
make_add_auth = _helpers.make_add_auth
make_paginator = _helpers.make_paginator
make_fake_bulk = _helpers.make_fake_bulk

_helpers_module = _helpers
