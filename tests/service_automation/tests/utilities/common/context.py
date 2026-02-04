from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Self

from ftrs_data_layer.domain import Organisation


@dataclass(init=True)
class Context:
    """Test context object for storing data between BDD steps."""

    correlation_id: Optional[str] = None
    ods_codes: List[str] = field(default_factory=list)
    organisation_details: List[Dict[str, Any]] = field(default_factory=list)
    extraction_date: Optional[str] = None
    saved_models: Dict[str, Organisation] = field(default_factory=dict)
    other: Dict[str, Any] = field(default_factory=dict)

    # Lambda-specific fields
    lambda_name: Optional[str] = None
    lambda_response: Optional[Dict[str, Any]] = None
    lambda_invocation_time: Optional[Any] = None  # datetime object
    transform_lambda: Optional[str] = None
    crud_lambda: Optional[str] = None

    def __repr__(self: Self) -> str:
        """Return a readable string representation of the Context."""
        return (
            f"Context(correlation_id={self.correlation_id}, "
            f"ods_codes={self.ods_codes}, "
            f"organisation_details={self.organisation_details}, "
            f"saved_models_keys={list(self.saved_models.keys())}, "
            f"extraction_date={self.extraction_date}, "
            f"lambda_name={self.lambda_name}, "
            f"lambda_response={'present' if self.lambda_response else 'None'}, "
            f"lambda_invocation_time={self.lambda_invocation_time}, "
            f"transform_lambda={self.transform_lambda}, "
            f"crud_lambda={self.crud_lambda}, "
            f"other_keys={list(self.other.keys())})"
        )
