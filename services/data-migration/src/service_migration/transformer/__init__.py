from service_migration.transformer.base import (
    ServiceTransformer,
    ServiceTransformOutput,
)
from service_migration.transformer.base_pharmacy import (
    BasePharmacyTransformer,
    LinkedPharmacyTransformer,
)
from service_migration.transformer.contraception_pharmacy import (
    ContraceptionPharmacyTransformer,
)
from service_migration.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from service_migration.transformer.gp_practice import GPPracticeTransformer
from service_migration.transformer.pharmacy_blood_pressure_check import (
    PharmacyBPCheckTransformer,
)

SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [
    GPPracticeTransformer,
    GPEnhancedAccessTransformer,
    PharmacyBPCheckTransformer,
    BasePharmacyTransformer,
    ContraceptionPharmacyTransformer,
]

__all__ = [
    "LinkedPharmacyTransformer",
    "ServiceTransformer",
    "ServiceTransformOutput",
    "GPPracticeTransformer",
    "GPEnhancedAccessTransformer",
    "BasePharmacyTransformer",
    "PharmacyBPCheckTransformer",
    "ContraceptionPharmacyTransformer",
    "SUPPORTED_TRANSFORMERS",
]
