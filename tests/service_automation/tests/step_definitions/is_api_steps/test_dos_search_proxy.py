from loguru import logger
import pytest
import requests
import json
from uuid import uuid4

@pytest.fixture(scope="module")
def r53_name() -> str:
    r53_name = os.getenv("R53_NAME", "different")
    logger.info(f"r53_name : {r53_name}")
    return r53_name

def test_ping_endpoint(nhsd_apim_proxy_url):
    """
    Send a request to an open access endpoint.
    """

    # The nhsd_apim_proxy_url will return the URL of the proxy under test.
    # The ping endpoint should have no authentication on it.

    resp = requests.get(nhsd_apim_proxy_url + "/_ping")
    assert resp.status_code == 200
    ping_data = json.loads(resp.text)
    assert "version" in ping_data


def test_status_endpoint(nhsd_apim_proxy_url, status_endpoint_auth_headers):
    """
    Send a request to the _status endpoint, protected by a platform-wide.
    """
    # The status_endpoint_auth_headers fixture returns a dict like
    # {"apikey": "thesecretvalue"} Use it to access your proxy's
    # _status endpoint.

    resp = requests.get(nhsd_apim_proxy_url + "/_status", headers=status_endpoint_auth_headers)
    status_json = resp.json()
    assert resp.status_code == 200
    assert status_json["status"] == "pass"

# You can provide arguments as a dict (as above) or keyword-args.
# With these arguments, you get a public/private key pair, the public
# key is "hosted" on our mock-jwks proxy, and the
# nhsd_apim_auth_headers fixture does the signed JWT flow for you.
@pytest.mark.nhsd_apim_authorization(access="application", level="level3")
def test_app_level3_access(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    resp = requests.get(
        nhsd_apim_proxy_url + "/Organization?_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M81046", headers=nhsd_apim_auth_headers
    )
    assert resp.status_code == 200 # authorized

    resp = requests.get(
    nhsd_apim_proxy_url + "/Organization?_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M81046"
    )
    assert resp.status_code == 401 # unauthorized



@pytest.mark.nhsd_apim_authorization(access="application", level="level3")
def test_trace(nhsd_apim_proxy_url, nhsd_apim_auth_headers, trace):
    session_name = str(uuid4())
    header_filters = {"trace_id": session_name}
    trace.post_debugsession(session=session_name, header_filters=header_filters)

    resp = requests.get(
        nhsd_apim_proxy_url + "/Organization?_revinclude=Endpoint:organization&identifier=odsOrganisationCode|M81046",
        headers={**header_filters, **nhsd_apim_auth_headers},
    )
    assert resp.status_code == 200

    trace_ids = trace.get_transaction_data(session_name=session_name)

    trace_data = trace.get_transaction_data_by_id(session_name=session_name, transaction_id=trace_ids[0])
    status_code_from_trace = trace.get_apigee_variable_from_trace(name="message.status.code", data=trace_data)

    trace.delete_debugsession_by_name(session_name)

    assert status_code_from_trace == "200"
