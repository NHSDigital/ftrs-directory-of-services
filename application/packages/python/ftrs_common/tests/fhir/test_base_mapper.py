import pytest
from ftrs_common.fhir.base_mapper import FhirMapper


def test_fhir_mapper_is_abstract():
    with pytest.raises(TypeError):
        FhirMapper()


def test_fhir_mapper_methods_are_abstract():
    class DummyMapper(FhirMapper):
        pass

    with pytest.raises(TypeError):
        DummyMapper()


def test_fhir_mapper_subclass_implements_methods():
    class DummyMapper(FhirMapper):
        def to_fhir(self, model_obj):
            return {"resourceType": "Test"}

        def from_fhir(self, fhir_resource):
            return "internal"

    mapper = DummyMapper()
    assert mapper.to_fhir("obj") == {"resourceType": "Test"}
    assert mapper.from_fhir({"resourceType": "Test"}) == "internal"
