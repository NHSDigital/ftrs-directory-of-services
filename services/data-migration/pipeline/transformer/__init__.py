from pipeline.transformer.base import ServiceTransformer, ServiceTransformOutput
from pipeline.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from pipeline.transformer.gp_practice import GPPracticeTransformer
from pipeline.transformer.gp_protected_learning_time import (
    GPProtectedLearningTimeTransformer,
)

# Note: ordered in most common case for efficiency
SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [
    GPPracticeTransformer,
    GPEnhancedAccessTransformer,
    GPProtectedLearningTimeTransformer,
]

__all__ = [
    "ServiceTransformer",
    "ServiceTransformOutput",
    "GPPracticeTransformer",
    "GPEnhancedAccessTransformer",
    "GPProtectedLearningTimeTransformer",
    "SUPPORTED_TRANSFORMERS",
]
