from service_migration.transformer.base import (
    ServiceTransformer,
    ServiceTransformOutput,
)
from service_migration.transformer.community_pharmacy import (
    CommunityPharmacyTransformer,
)
from service_migration.transformer.distance_selling_pharmacy import (
    DistanceSellingPharmacyTransformer,
)
from service_migration.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from service_migration.transformer.gp_practice import GPPracticeTransformer

SUPPORTED_TRANSFORMERS: list[ServiceTransformer] = [
    GPPracticeTransformer,
    GPEnhancedAccessTransformer,
    CommunityPharmacyTransformer,
    DistanceSellingPharmacyTransformer,
]

__all__ = [
    "ServiceTransformer",
    "ServiceTransformOutput",
    "GPPracticeTransformer",
    "GPEnhancedAccessTransformer",
    "CommunityPharmacyTransformer",
    "DistanceSellingPharmacyTransformer",
    "SUPPORTED_TRANSFORMERS",
]
