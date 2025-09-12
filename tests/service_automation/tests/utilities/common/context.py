from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Self
from ftrs_data_layer.domain import Organisation # Or your appropriate model class


@dataclass(init=True)
class Context:
    """Test context object for storing data between BDD steps."""

    correlation_id: Optional[str] = None
    ods_codes: List[str] = field(default_factory=list)
    organisation_details: List[Dict[str, Any]] = field(default_factory=list)
    extraction_date: Optional[str] = None
    saved_models: Dict[str, Organisation] = field(default_factory=dict)
    other: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self: Self) -> str:
        """Return a readable string representation of the Context."""
        return (
            f"Context(correlation_id={self.correlation_id}, "
            f"ods_codes={self.ods_codes}, "
            f"organisation_details={self.organisation_details}, "
            f"saved_models_keys={list(self.saved_models.keys())}, "
            f"extraction_date={self.extraction_date}, "
            f"other_keys={list(self.other.keys())})"
        )
