from pipeline.transformer.base import ServiceTransformer, ServiceTransformOutput
from pipeline.transformer.gp_practice import GPPracticeTransformer

SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [GPPracticeTransformer]

__all__ = [
    "ServiceTransformer",
    "ServiceTransformOutput",
    "GPPracticeTransformer",
    "SUPPORTED_TRANSFORMERS",
]
