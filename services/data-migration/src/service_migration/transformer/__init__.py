from service_migration.transformer.base import ServiceTransformer
from service_migration.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from service_migration.transformer.gp_practice import GPPracticeTransformer

SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [
    GPPracticeTransformer,
    GPEnhancedAccessTransformer,
]

__all__ = [
    "ServiceTransformer",
    "GPPracticeTransformer",
    "GPEnhancedAccessTransformer",
    "SUPPORTED_TRANSFORMERS",
]
