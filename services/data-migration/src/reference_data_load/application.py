from ftrs_common.logger import Logger
from sqlmodel import create_engine

from common.events import ReferenceDataLoadEvent
from reference_data_load.config import ReferenceDataLoadConfig
from reference_data_load.handlers.triage_code_handler import TriageCodeHandler


class ReferenceDataLoadApplication:
    def __init__(self, config: ReferenceDataLoadConfig | None) -> None:
        self.logger = Logger.get(service="reference-data-load")
        self.config = config or ReferenceDataLoadConfig()
        self.engine = create_engine(self.config.db_config.connection_string, echo=False)

    def handle(self, event: ReferenceDataLoadEvent) -> None:
        match event.type:
            case "triagecode":
                return self._load_triage_codes()

        raise ValueError(f"Unknown event type: {event.type}")

    def _load_triage_codes(self) -> None:
        handler = TriageCodeHandler(config=self.config, logger=self.logger)
        return handler.load_triage_codes()
