from service_migration.transformer.base import (
    LinkedPharmacyTransformer,
    ServiceTransformer,
    ServiceTransformOutput,
)
from service_migration.transformer.base_pharmacy import BasePharmacyTransformer
from service_migration.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from service_migration.transformer.gp_practice import GPPracticeTransformer
from service_migration.transformer.pharmacy_blood_pressure_check import (
    PharmacyBPCheckTransformer,
    PharmacyDSPBPCheckTransformer,
)

SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [
    GPPracticeTransformer,
    GPEnhancedAccessTransformer,
    PharmacyBPCheckTransformer,
    PharmacyDSPBPCheckTransformer,
    BasePharmacyTransformer,
]

__all__ = [
    "LinkedPharmacyTransformer",
    "ServiceTransformer",
    "ServiceTransformOutput",
    "GPPracticeTransformer",
    "GPEnhancedAccessTransformer",
    "BasePharmacyTransformer",
    "PharmacyBPCheckTransformer",
    "PharmacyDSPBPCheckTransformer",
    "SUPPORTED_TRANSFORMERS",
]
