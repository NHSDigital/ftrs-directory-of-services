from pipeline.transformer.base import ServiceTransformer, ServiceTransformOutput
from pipeline.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from pipeline.transformer.gp_practice import GPPracticeTransformer
from pipeline.transformer.gp_special_allocation_scheme import (
    GPSpecialAllocationSchemeTransformer,
)

SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [
    GPPracticeTransformer,
    GPEnhancedAccessTransformer,
    GPSpecialAllocationSchemeTransformer,
]

__all__ = [
    "ServiceTransformer",
    "ServiceTransformOutput",
    "GPPracticeTransformer",
    "GPEnhancedAccessTransformer",
    "SUPPORTED_TRANSFORMERS",
]
