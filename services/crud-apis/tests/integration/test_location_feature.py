import pathlib

from pytest_bdd import scenarios

LOCATION_FEATURES_PATH = pathlib.Path(__file__).parent / "features/location/"
scenarios(*LOCATION_FEATURES_PATH.glob("*.feature"))
