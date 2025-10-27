from time import perf_counter

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.domain.triage_code import TriageCode
from ftrs_data_layer.logbase import DataMigrationLogBase
from sqlmodel import create_engine

from common.cache import DoSMetadataCache
from pipeline.processor import DataMigrationMetrics
from pipeline.transformer.triage_code import TriageCodeTransformer
from pipeline.utils.config import DataMigrationConfig
from pipeline.utils.dbutil import (
    get_all_symptom_groups,
    get_repository,
    get_symptom_discriminators_for_symptom_group,
    iter_records,
)


class TriageCodeProcessor:
    def __init__(
        self,
        config: DataMigrationConfig,
        logger: Logger,
    ) -> None:
        self.logger = logger
        self.config = config
        self.engine = create_engine(config.db_config.connection_string, echo=False)
        self.metrics = DataMigrationMetrics()
        self.metadata = DoSMetadataCache(self.engine)

    def sync_all_triage_codes(self) -> None:
        """
        Run the full sync process for triage codes.
        """
        for symptom_group in iter_records(self.engine, legacy.SymptomGroup):
            self._process_record(
                symptom_group,
                "SymptomGroup",
                TriageCodeTransformer.build_triage_code_from_symptom_group,
            )

        for disposition in iter_records(self.engine, legacy.Disposition):
            self._process_record(
                disposition,
                "Disposition",
                TriageCodeTransformer.build_triage_code_from_disposition,
            )

        for symptom_discriminator in iter_records(
            self.engine, legacy.SymptomDiscriminator
        ):
            self._process_record(
                symptom_discriminator,
                "SymptomDiscriminator",
                TriageCodeTransformer.build_triage_code_from_symptom_discriminator,
            )
        self._process_combinations()

    def _process_record(
        self, record: legacy, record_type: str, transformer_method: callable
    ) -> None:
        """
        Generic method to process a single record.

        Args:
            record: The record to process
            record_type: The type of record being processed
            transformer_method: Function to transform the record into a triage code
        """
        self.logger.append_keys(record_id=record.id)
        self.logger.log(
            DataMigrationLogBase.DM_ETL_001,
            record=record.model_dump(exclude_none=True, mode="json", warnings=False),
        )

        try:
            start_time = perf_counter()

            # Transform the record
            triageCode = transformer_method(record)
            self._save_to_dynamoDB(triageCode)

            self.logger.log(
                DataMigrationLogBase.DM_ETL_006,
                transformer_name=f"{record_type}Transformer",
                original_record=record.model_dump(
                    exclude_none=True, mode="json", warnings=False
                ),
                transformed_record=triageCode.model_dump(
                    exclude_none=True, mode="json", warnings=False
                ),
            )

            elapsed_time = perf_counter() - start_time
            self.logger.log(
                DataMigrationLogBase.DM_ETL_007,
                elapsed_time=elapsed_time,
                transformer_name=f"{record_type}Transformer",
                # Additional metrics...
            )

        except Exception as e:
            self.metrics.errors += 1
            self.logger.exception(
                f"Unexpected error encountered whilst processing {record_type.lower()} record"
            )
            self.logger.log(DataMigrationLogBase.DM_ETL_008, error=str(e))
            return

        finally:
            self.logger.remove_keys(["record_id"])

    def _process_combinations(self) -> None:
        """
        Process and save combinations of symptom groups and symptom discriminators.
        """

        start_time = perf_counter()
        try:
            symptom_groups = get_all_symptom_groups(self.engine)
            for sg_id in symptom_groups:
                try:
                    symptom_discriminators_symptom_group = (
                        get_symptom_discriminators_for_symptom_group(self.engine, sg_id)
                    )
                    if not symptom_discriminators_symptom_group:
                        self.logger.log(DataMigrationLogBase.DM_ETL_012, sg_id=sg_id)
                        continue

                    triage_code = TriageCodeTransformer.build_triage_code_combinations(
                        sg_id, symptom_discriminators_symptom_group
                    )
                    self._save_to_dynamoDB(triage_code)

                    self.logger.log(
                        DataMigrationLogBase.DM_ETL_006,
                        transformer_name="TriageCodeTransformer",
                        original_record={
                            "symptom_group_id": sg_id,
                            "symptom_discriminators": [
                                sd.model_dump(
                                    exclude_none=True, mode="json", warnings=False
                                )
                                for sd in symptom_discriminators_symptom_group
                            ],
                        },
                        transformed_record=triage_code.model_dump(
                            exclude_none=True, mode="json", warnings=False
                        ),
                    )
                    elapsed_time = perf_counter() - start_time
                    self.logger.log(
                        DataMigrationLogBase.DM_ETL_007,
                        process="combinations",
                        elapsed_time=elapsed_time,
                        # Additional metrics...
                    )
                except Exception as e:
                    self.metrics.errors += 1
                    self.logger.exception(
                        f"Unexpected error encountered whilst processing symptom group ID {sg_id}"
                    )
                    self.logger.log(DataMigrationLogBase.DM_ETL_008, error=str(e))
                    continue
        except Exception as e:
            self.metrics.errors += 1
            self.logger.exception(
                "Unexpected error encountered whilst fetching symptom groups"
            )
            self.logger.log(DataMigrationLogBase.DM_ETL_008, error=str(e))
            return

    def _save_to_dynamoDB(self, result: TriageCode) -> None:
        traige_code_repo = get_repository(
            self.config, "triage-code", TriageCode, self.logger
        )
        traige_code_repo.upsert(result)
