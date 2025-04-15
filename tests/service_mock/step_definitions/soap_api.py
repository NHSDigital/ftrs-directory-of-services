import requests
from pytest_bdd import given, when, then, scenarios

scenarios('../soap_api.feature')

SOAP_BODY = """<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <SayHello xmlns="http://example.com/soap">
            <name>SOAP User</name>
        </SayHello>
    </soap:Body>
</soap:Envelope>
"""

@given("the SOAP API is running")
def soap_api_running():
    pass

@when("I send a SOAP request")
def send_soap_request(context):
    headers = {"Content-Type": "text/xml"}
    context.response = requests.post("http://localhost:8080/soap/sayHello", data=SOAP_BODY, headers=headers)

@then('the response should contain "Hello SOAP User"')
def check_soap_response(context):
    assert "Hello SOAP User" in context.response.text
