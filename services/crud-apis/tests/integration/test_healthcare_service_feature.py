import pathlib

from pytest_bdd import scenarios

HEALTHCARE_SERVICE_FEATURES_PATH = (
    pathlib.Path(__file__).parent / "features/healthcare-service/"
)
scenarios(*HEALTHCARE_SERVICE_FEATURES_PATH.glob("*.feature"))
