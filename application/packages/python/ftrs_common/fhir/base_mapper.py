from abc import ABC, abstractmethod

from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel


class FhirMapper(ABC):
    @abstractmethod
    def to_fhir(self, model_obj: object) -> object:
        """Convert internal model to FHIR resource dict."""
        pass

    @abstractmethod
    def from_fhir(self, fhir_resource: FHIRResourceModel) -> object:
        """Convert FHIR resource dict to internal model."""
        pass
