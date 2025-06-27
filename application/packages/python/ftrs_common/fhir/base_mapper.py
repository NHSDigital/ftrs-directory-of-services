from abc import ABC, abstractmethod


class FhirMapper(ABC):
    @abstractmethod
    def to_fhir(self, model_obj):
        """Convert internal model to FHIR resource dict."""
        pass

    @abstractmethod
    def from_fhir(self, fhir_resource):
        """Convert FHIR resource dict to internal model."""
        pass
