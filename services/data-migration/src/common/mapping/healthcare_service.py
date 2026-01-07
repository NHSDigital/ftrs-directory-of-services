from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain import (
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    Disposition,
    HealthcareService,
    HealthcareServiceCategory,
    HealthcareServiceTelecom,
    HealthcareServiceType,
    NotAvailable,
    OpeningTime,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.enums import TimeUnit
from ftrs_data_layer.domain.legacy.data_models import (
    ServiceData,
    ServiceDayOpeningData,
    ServiceDispositionData,
    ServiceSGSDData,
    ServiceSpecifiedOpeningDateData,
)

from common.logbase import ServiceMigrationLogBase
from common.mapping.base import BaseMapper
from common.uuid_utils import generate_uuid
from service_migration.constants import SERVICE_MIGRATION_USER
from service_migration.formatting.number_formatter import clean_decimal


class HealthcareServiceMapper(BaseMapper[ServiceData, HealthcareService]):
    def map(
        self,
        service: ServiceData,
        organisation_id: UUID,
        location_id: UUID,
        category: HealthcareServiceCategory | None = None,
        type: HealthcareServiceType | None = None,
    ) -> HealthcareService:
        return HealthcareService(
            id=generate_uuid(service.id, "healthcare_service"),
            identifier_oldDoS_uid=service.uid,
            active=True,
            category=category,
            type=type,
            providedBy=organisation_id,
            location=location_id,
            name=service.name,
            telecom=HealthcareServiceTelecom(
                phone_public=service.publicphone,
                phone_private=service.nonpublicphone,
                email=service.email,
                web=service.web,
            ),
            createdBy=SERVICE_MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=SERVICE_MIGRATION_USER,
            modifiedDateTime=self.start_time,
            openingTime=self.map_opening_times(service),
            symptomGroupSymptomDiscriminators=self.map_sgsds(service),
            dispositions=self.map_dispositions(service),
            ageEligibilityCriteria=self.map_age_eligibility_criteria(service),
        )

    def map_opening_times(self, service: ServiceData) -> list[dict]:
        """
        Build opening times from the service's scheduled opening times.
        """
        scheduled_times = self.map_scheduled_opening_times(
            service.scheduled_opening_times
        )
        specified_times = self.map_specified_opening_times(
            service.specified_opening_times
        )
        return scheduled_times + specified_times

    def map_scheduled_opening_times(
        self, service_day_openings: list[ServiceDayOpeningData]
    ) -> list[OpeningTime]:
        """
        Build scheduled opening times from the service's scheduled opening times.
        """
        items = []
        for day_opening in service_day_openings:
            availability_cls = AvailableTime
            day = self.metadata.opening_time_days.get(day_opening.dayid)
            day_of_week = day.name.lower()[:3]

            if day.name == "BankHoliday":
                availability_cls = AvailableTimePublicHolidays
                day_of_week = None

            items.extend(
                [
                    availability_cls(
                        dayOfWeek=day_of_week,
                        startTime=opening_time.starttime,
                        endTime=opening_time.endtime,
                        allDay=False,
                    )
                    for opening_time in day_opening.times
                ]
            )

        return items

    def map_specified_opening_times(
        self,
        service_specified_opening_dates: list[ServiceSpecifiedOpeningDateData],
    ) -> list[OpeningTime]:
        """
        Build specified opening times from the service's specified opening times.
        """
        items = []
        for specified_date in service_specified_opening_dates:
            for specified_time in specified_date.times:
                availability_cls = AvailableTimeVariation
                if specified_time.isclosed:
                    availability_cls = NotAvailable

                items.append(
                    availability_cls(
                        startTime=datetime.combine(
                            specified_date.date, specified_time.starttime
                        ),
                        endTime=datetime.combine(
                            specified_date.date, specified_time.endtime
                        ),
                    )
                )

        return items

    def map_sgsds(
        self, service: ServiceData
    ) -> list[SymptomGroupSymptomDiscriminatorPair]:
        return [self.map_sgsd_pair(code) for code in service.sgsds]

    def map_sgsd_pair(
        self, code: ServiceSGSDData
    ) -> SymptomGroupSymptomDiscriminatorPair:
        """
        Build a single SymptomGroupSymptomDiscriminatorPair from a ServiceSGSD code.
        """
        return SymptomGroupSymptomDiscriminatorPair(
            sg=code.sgid,
            sd=code.sdid,
        )

    def map_dispositions(self, service: ServiceData) -> list[Disposition]:
        """
        Build dispositions from the service's dispositions.
        """
        dispositions = []
        for code in service.dispositions:
            disposition = self.map_disposition(code, service.id)
            if disposition is not None:
                dispositions.append(disposition)
        return dispositions

    def map_disposition(
        self, code: ServiceDispositionData, service_id: int
    ) -> str | None:
        """
        Build a single Disposition from a ServiceDisposition code.
        Returns None if the disposition is not found in metadata.
        """
        disposition = self.metadata.dispositions.get(code.dispositionid)
        if disposition is None:
            self.logger.log(
                ServiceMigrationLogBase.DM_ETL_018,
                service_id=service_id,
                disposition_id=code.dispositionid,
            )
            return None
        return disposition.dxcode

    def map_age_eligibility_criteria(self, service: ServiceData) -> list | None:
        """
        Build age eligibility criteria from the service's age ranges, in days.
        * Where there are multiple consecutive age ranges, these should be combined to a single range.
        * Where there are multiple non consecutive age ranges, these should each be an item in the list.

        It handles standard DoS age groups (in days):
        * 0-364.25, 365.25-1825.25, 1826.25-5843, 5844-47481.5
        * Two ranges are consecutive if the end of one is very close to the start of the next.
        * Tolerance of 1 day is used to determine if ranges are consecutive.
        """
        if not service.age_range:
            self.logger.log(ServiceMigrationLogBase.DM_ETL_017, service_id=service.id)
            return None

        TOLERANCE = Decimal(1)

        sorted_ranges = sorted(service.age_range, key=lambda x: x.daysfrom)

        result = []
        current_range = {
            "rangeFrom": clean_decimal(sorted_ranges[0].daysfrom),
            "rangeTo": clean_decimal(sorted_ranges[0].daysto),
            "type": TimeUnit.DAYS,
        }

        for age_range in sorted_ranges[1:]:
            current_end = current_range["rangeTo"]
            next_start = age_range.daysfrom
            next_end = age_range.daysto
            # Check if ranges are consecutive
            if abs(next_start - current_end) <= TOLERANCE:
                # Extend the current range to include this range
                current_range["rangeTo"] = clean_decimal(next_end)
            # Check if ranges overlap
            elif next_start <= current_end:
                # If the next range starts before the current one ends,
                # extend the current range if needed
                if next_end > current_end:
                    current_range["rangeTo"] = clean_decimal(next_end)
            else:
                # Non-consecutive range - add the current range to the result
                # and start a new one
                result.append(current_range)
                current_range = {
                    "rangeFrom": clean_decimal(next_start),
                    "rangeTo": clean_decimal(next_end),
                    "type": TimeUnit.DAYS,
                }

        result.append(current_range)

        return result
