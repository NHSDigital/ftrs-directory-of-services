from service_migration.transformer.base import (
    ServiceTransformer,
    ServiceTransformOutput,
)
from service_migration.transformer.base_pharmacy import BasePharmacyTransformer
from service_migration.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from service_migration.transformer.gp_practice import GPPracticeTransformer

SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [
    GPPracticeTransformer,
    GPEnhancedAccessTransformer,
    BasePharmacyTransformer,
]

__all__ = [
    "ServiceTransformer",
    "ServiceTransformOutput",
    "GPPracticeTransformer",
    "GPEnhancedAccessTransformer",
    "BasePharmacyTransformer",
    "SUPPORTED_TRANSFORMERS",
]
