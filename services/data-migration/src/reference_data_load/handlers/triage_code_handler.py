from time import perf_counter
from typing import Generator

from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain.legacy.db_models import (
    Disposition,
    LegacyDoSModel,
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminator,
)
from ftrs_data_layer.domain.triage_code import TriageCode
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from common.cache import DoSMetadataCache
from common.logbase import ReferenceDataLoadLogBase
from reference_data_load.config import ReferenceDataLoadConfig
from reference_data_load.mapper.triage_code_mapper import (
    DispositionMapper,
    SGSDCombinationMapper,
    SymptomDiscriminatorMapper,
    SymptomGroupMapper,
)


class TriageCodeHandler:
    def __init__(
        self,
        config: ReferenceDataLoadConfig,
        logger: Logger,
    ) -> None:
        self.logger = logger
        self.config = config
        self.engine = create_engine(config.db_config.connection_string, echo=False)
        self.metadata = DoSMetadataCache(self.engine)
        self.repository = get_service_repository(
            model_cls=TriageCode,
            entity_name="triage-code",
            logger=self.logger,
            endpoint_url=self.config.dynamodb_endpoint,
        )

    def load_triage_codes(self) -> None:
        start_time = perf_counter()
        self.logger.log(ReferenceDataLoadLogBase.RD_TC_001, start_time=start_time)

        self._load_symptom_groups()
        self._load_symptom_discriminators()
        self._load_dispositions()
        self._load_sgsd_combinations()

        end_time = perf_counter()
        self.logger.log(
            ReferenceDataLoadLogBase.RD_TC_002,
            end_time=end_time,
            duration=end_time - start_time,
        )

    def _load_symptom_groups(self) -> None:
        start_time = perf_counter()
        self.logger.log(ReferenceDataLoadLogBase.RD_TC_003, start_time=start_time)

        mapper = SymptomGroupMapper()
        count = 0
        for symptom_group in self._iter_records(SymptomGroup):
            triage_code = mapper.map(symptom_group)
            self._save_to_dynamodb(triage_code)
            count += 1

        end_time = perf_counter()
        self.logger.log(
            ReferenceDataLoadLogBase.RD_TC_004,
            end_time=end_time,
            duration=end_time - start_time,
            record_count=count,
        )

    def _load_symptom_discriminators(self) -> None:
        start_time = perf_counter()
        self.logger.log(ReferenceDataLoadLogBase.RD_TC_005, start_time=start_time)

        mapper = SymptomDiscriminatorMapper()
        count = 0
        for symptom_discriminator in self._iter_records(SymptomDiscriminator):
            triage_code = mapper.map(symptom_discriminator)
            self._save_to_dynamodb(triage_code)
            count += 1

        end_time = perf_counter()
        self.logger.log(
            ReferenceDataLoadLogBase.RD_TC_006,
            end_time=end_time,
            duration=end_time - start_time,
            record_count=count,
        )

    def _load_dispositions(self) -> None:
        start_time = perf_counter()
        self.logger.log(ReferenceDataLoadLogBase.RD_TC_007, start_time=start_time)

        mapper = DispositionMapper()
        count = 0

        for disposition in self._iter_records(Disposition):
            triage_code = mapper.map(disposition)
            self._save_to_dynamodb(triage_code)
            count += 1

        end_time = perf_counter()
        self.logger.log(
            ReferenceDataLoadLogBase.RD_TC_008,
            end_time=end_time,
            duration=end_time - start_time,
            record_count=count,
        )

    def _load_sgsd_combinations(self) -> None:
        start_time = perf_counter()
        self.logger.log(ReferenceDataLoadLogBase.RD_TC_009, start_time=start_time)

        combinations = {}

        for sg_sd in self._iter_records(SymptomGroupSymptomDiscriminator):
            symptom_group = self.metadata.symptom_groups.get(sg_sd.symptomgroupid)
            symptom_discriminator = self.metadata.symptom_discriminators.get(
                sg_sd.symptomdiscriminatorid
            )

            if symptom_group.id not in combinations:
                combinations[symptom_group.id] = {
                    "symptom_group": symptom_group,
                    "symptom_discriminators": [],
                }

            combinations[symptom_group.id]["symptom_discriminators"].append(
                symptom_discriminator
            )

        end_time = perf_counter()
        self.logger.log(
            ReferenceDataLoadLogBase.RD_TC_010,
            end_time=end_time,
            duration=end_time - start_time,
        )

        start_time = perf_counter()
        self.logger.log(ReferenceDataLoadLogBase.RD_TC_011, start_time=start_time)

        mapper = SGSDCombinationMapper()
        for combo in combinations.values():
            triage_code = mapper.map(
                symptom_group=combo["symptom_group"],
                symptom_discriminators=combo["symptom_discriminators"],
            )
            self._save_to_dynamodb(triage_code)

        end_time = perf_counter()
        self.logger.log(
            ReferenceDataLoadLogBase.RD_TC_012,
            end_time=end_time,
            duration=end_time - start_time,
            record_count=len(combinations),
        )

    def _iter_records(
        self, model: type[LegacyDoSModel]
    ) -> Generator[LegacyDoSModel, None, None]:
        with Session(self.engine) as session:
            statement = select(model)
            results = session.execute(statement).scalars()
            for record in results:
                yield record

    def _save_to_dynamodb(self, result: TriageCode) -> None:
        self.repository.upsert(result)
