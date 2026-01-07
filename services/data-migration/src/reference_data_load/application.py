from ftrs_common.logger import Logger
from sqlalchemy import create_engine

from common.events import ReferenceDataLoadEvent
from common.logbase import ReferenceDataLoadLogBase
from reference_data_load.config import ReferenceDataLoadConfig
from reference_data_load.handlers.triage_code_handler import TriageCodeHandler


class ReferenceDataLoadApplication:
    def __init__(self, config: ReferenceDataLoadConfig | None = None) -> None:
        self.logger = Logger.get(service="reference-data-load")
        self.logger.log(ReferenceDataLoadLogBase.RD_APP_001, config=config)

        self.config = config or ReferenceDataLoadConfig()
        self.engine = create_engine(self.config.db_config.connection_string, echo=False)

        self.logger.log(ReferenceDataLoadLogBase.RD_APP_002, config=self.config)

    def handle(self, event: ReferenceDataLoadEvent) -> None:
        self.logger.log(ReferenceDataLoadLogBase.RD_APP_003, event_type=event.type)

        try:
            match event.type:
                case "triagecode":
                    return self._load_triage_codes()

            raise ValueError(f"Unknown event type: {event.type}")  # noqa: TRY301

        except Exception as exc:
            self.logger.log(
                ReferenceDataLoadLogBase.RD_APP_004,
                event_type=event.type,
                error=str(exc),
            )
            raise

    def _load_triage_codes(self) -> None:
        handler = TriageCodeHandler(config=self.config, logger=self.logger)
        return handler.load_triage_codes()
