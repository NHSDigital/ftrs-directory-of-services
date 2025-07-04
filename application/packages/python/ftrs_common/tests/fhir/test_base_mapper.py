import pytest
from ftrs_common.fhir.base_mapper import FhirMapper


def test_fhir_mapper_is_abstract() -> None:
    with pytest.raises(TypeError):
        FhirMapper()


def test_fhir_mapper_methods_are_abstract() -> None:
    class DummyMapper(FhirMapper):
        pass

    with pytest.raises(TypeError):
        DummyMapper()


def test_fhir_mapper_subclass_implements_methods() -> None:
    class DummyMapper(FhirMapper):
        def to_fhir(self, model_obj: object) -> dict:
            return {"resourceType": "Test"}

        def from_fhir(self, fhir_resource: dict) -> str:
            return "internal"

    mapper = DummyMapper()
    assert mapper.to_fhir("obj") == {"resourceType": "Test"}
    assert mapper.from_fhir({"resourceType": "Test"}) == "internal"
