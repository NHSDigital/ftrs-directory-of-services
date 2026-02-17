import pathlib

from pytest_bdd import scenarios

ORGANISATION_FEATURES_PATH = pathlib.Path(__file__).parent / "features/organisation/"
scenarios(*ORGANISATION_FEATURES_PATH.glob("*.feature"))
