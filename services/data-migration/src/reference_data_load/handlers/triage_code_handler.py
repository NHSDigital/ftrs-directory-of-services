from typing import Generator

from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.domain.legacy import (
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminator,
)
from ftrs_data_layer.domain.triage_code import TriageCode
from sqlmodel import Session, create_engine, select

from common.cache import DoSMetadataCache
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
        self._load_symptom_groups()
        self._load_symptom_discriminators()
        self._load_dispositions()
        self._load_sgsd_combinations()

    def _load_symptom_groups(self) -> None:
        mapper = SymptomGroupMapper()
        for symptom_group in self._iter_records(SymptomGroup):
            triage_code = mapper.map(symptom_group)
            self._save_to_dynamodb(triage_code)

    def _load_symptom_discriminators(self) -> None:
        mapper = SymptomDiscriminatorMapper()
        for symptom_discriminator in self._iter_records(SymptomDiscriminator):
            triage_code = mapper.map(symptom_discriminator)
            self._save_to_dynamodb(triage_code)

    def _load_dispositions(self) -> None:
        mapper = DispositionMapper()
        for disposition in self._iter_records(legacy.Disposition):
            triage_code = mapper.map(disposition)
            self._save_to_dynamodb(triage_code)

    def _load_sgsd_combinations(self) -> None:
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

        mapper = SGSDCombinationMapper()
        for combo in combinations.values():
            triage_code = mapper.map(
                symptom_group=combo["symptom_group"],
                symptom_discriminators=combo["symptom_discriminators"],
            )
            self._save_to_dynamodb(triage_code)

    def _iter_records(
        self, model: type[legacy.LegacyDoSModel]
    ) -> Generator[legacy.LegacyDoSModel, None, None]:
        with Session(self.engine) as session:
            statement = select(model)
            results = session.exec(statement)
            for record in results:
                yield record

    def _save_to_dynamodb(self, result: TriageCode) -> None:
        self.repository.upsert(result)
