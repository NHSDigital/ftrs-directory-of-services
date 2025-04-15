import pytest
from wiremock_manager import WireMockManager

@pytest.fixture(scope="session", autouse=True)
def wiremock_server():
    wm = WireMockManager()
    wm.start()
    yield
    wm.stop()

@pytest.fixture(scope="function")
def context():
    return type("Context", (), {})()
