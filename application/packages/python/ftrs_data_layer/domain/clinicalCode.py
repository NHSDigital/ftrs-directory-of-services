import json
from enum import Enum
from typing import List, Optional, Union, Dict

from numpy import array
from pydantic import BaseModel
from sqlalchemy import false
import numpy as np

from ftrs_common.logger import Logger


class ClinicalCodeSource(str, Enum):
    PATHWAYS = "pathways"


class ClinicalCodeType(str, Enum):
    SYMPTOM_GROUP = "Symptom Group (SG)"
    SYMPTOM_DISCRIMINATOR = "Symptom Discriminator (SD)"
    DISPOSITION = "Disposition (Dx)"


class BaseClinicalCode(BaseModel):
    id: str
    source: ClinicalCodeSource
    codeType: ClinicalCodeType
    codeID: Union[int, str]
    codeValue: str | None


class SymptomGroup(BaseClinicalCode):
    zCodeExists: bool | None = false


class SymptomDiscriminator(BaseClinicalCode):
    synonyms: Optional[List[str]] = None


class Disposition(BaseClinicalCode):
    time: int | None = 0


class SymptomGroupSymptomDiscriminatorPair(BaseModel):
    SG_SD: Optional[List[Dict[str, Union[SymptomGroup, SymptomDiscriminator]]]] = None


class ClinicalCodeConverter:
    @staticmethod
    def convert_dispositions(dispositions: str | np.ndarray) -> List[Disposition]:
        try:
            if isinstance(dispositions, np.ndarray):
                all_data = []
                for disp in dispositions:
                    data = json.loads(disp)
                    if isinstance(data, dict):
                        all_data.append(data)
                    elif isinstance(data, list):
                        all_data.extend(data)
                    else:
                        raise ValueError(
                            f"Invalid disposition data format: {type(data)}"
                        )
            else:
                data = json.loads(dispositions)
                all_data = data if isinstance(data, list) else [data]

            disposition_list: List[Disposition] = []
            for item in all_data:
                if not isinstance(item, dict):
                    raise ValueError("Each disposition item must be a JSON object")

                validated_disposition = Disposition(
                    id=item.get("id"),
                    source=item.get("source"),
                    codeType=item.get("codeType"),
                    codeID=item.get("codeID"),
                    codeValue=item.get("codeValue"),
                    time=item.get("time", 0),
                )
                disposition_list.append(validated_disposition)

            return disposition_list

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}") from e

    @staticmethod
    def convert_sg_sd_pair(
        sg_sd_pair: str | np.ndarray,
    ) -> SymptomGroupSymptomDiscriminatorPair:
        try:
            all_sg_sd_list = []

            data_items = (
                (json.loads(item) for item in sg_sd_pair)
                if isinstance(sg_sd_pair, np.ndarray)
                else [json.loads(sg_sd_pair)]
            )

            for pair in data_items:
                sg_data = pair.get("sg")
                sd_data = pair.get("sd")

                if not sg_data or not sd_data:
                    raise ValueError("Both 'sg' and 'sd' components are required")

                if sg_data["codeType"] != ClinicalCodeType.SYMPTOM_GROUP:
                    raise ValueError(
                        f"Invalid codeType for symptom group: {sg_data['codeType']}"
                    )
                if sd_data["codeType"] != ClinicalCodeType.SYMPTOM_DISCRIMINATOR:
                    raise ValueError(
                        f"Invalid codeType for symptom discriminator: {sd_data['codeType']}"
                    )

                all_sg_sd_list.append(
                    {
                        "sg": SymptomGroup(**sg_data),
                        "sd": SymptomDiscriminator(**sd_data),
                    }
                )

            return SymptomGroupSymptomDiscriminatorPair(SG_SD=all_sg_sd_list)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Validation error: {str(e)}") from e
