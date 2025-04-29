import pandas as pd
from pytest_mock import MockerFixture

from pipeline.utils.dos_db import (
    get_gp_endpoints,
    get_gp_practices,
    get_serviceendpoints_columns_count,
    get_services_columns_count,
    get_services_size,
)

# Mock database URI
db_uri = "postgresql://user:password@localhost:5432/test_db"

# Mock data
mock_gp_practices_df = pd.DataFrame(
    {
        "name": ["Practice A"],
        "type": ["GP"],
        "odscode": ["A12345"],
        "uid": ["uid123"],
        "serviceid": [1],
    }
)

mock_gp_endpoints_df = pd.DataFrame(
    {
        "id": [1],
        "endpointorder": [1],
        "transport": ["email"],
        "format": ["PDF"],
        "interaction": ["interaction1"],
        "businessscenario": ["scenario1"],
        "address": ["address1"],
        "comment": ["comment1"],
        "iscompressionenabled": ["false"],
        "serviceid": [1],
    }
)

mock_services_size_df = pd.DataFrame({"count": [100]})
expected_services_size = 100

mock_services_columns_count_df = pd.DataFrame({"count": [10]})
expected_services_columns_count = 10

mock_serviceendpoints_columns_count_df = pd.DataFrame({"count": [5]})
expected_serviceendpoints_columns_count = 5


def test_get_gp_practices(mocker: MockerFixture) -> None:
    mock_read_sql = mocker.patch("pandas.read_sql", return_value=mock_gp_practices_df)
    result = get_gp_practices(db_uri)
    mock_read_sql.assert_called_once_with(
        """
SELECT
    "services"."name",
    "servicetypes"."name" AS "type",
    "services"."odscode",
    "services"."uid",
    "services"."id" AS "serviceid"
FROM "pathwaysdos"."services"
LEFT JOIN "pathwaysdos"."servicestatuses" ON "services"."statusid" = "servicestatuses"."id"
LEFT JOIN "pathwaysdos"."servicetypes" ON "services"."typeid" = "servicetypes"."id"
WHERE
    "servicestatuses"."name" = 'active'
    AND "services"."typeid" = '100'
    AND "services"."odscode" ~ '^[A-Za-z][0-9]{5}$';
""",
        db_uri,
    )
    pd.testing.assert_frame_equal(result, mock_gp_practices_df)


def test_get_gp_endpoints(mocker: MockerFixture) -> None:
    mock_read_sql = mocker.patch("pandas.read_sql", return_value=mock_gp_endpoints_df)
    result = get_gp_endpoints(db_uri)
    mock_read_sql.assert_called_once_with(
        """
WITH gp_practice AS (
    SELECT
        "services"."id" AS "serviceid"
    FROM "pathwaysdos"."services"
    LEFT JOIN "pathwaysdos"."servicetypes" ON "services"."typeid" = "servicetypes"."id"
    LEFT JOIN "pathwaysdos"."servicestatuses" ON "services"."statusid" = "servicestatuses"."id"
    WHERE
        "servicestatuses"."name" = 'active'
        AND "services"."typeid" = '100'
        AND "services"."odscode" ~ '^[A-Za-z][0-9]{5}$'
)
SELECT
    "serviceendpoints".*
FROM "gp_practice"
LEFT JOIN "pathwaysdos"."serviceendpoints" ON "gp_practice"."serviceid" = "serviceendpoints"."serviceid"
""",
        db_uri,
    )
    pd.testing.assert_frame_equal(result, mock_gp_endpoints_df)


def test_get_services_size(mocker: MockerFixture) -> None:
    mock_read_sql = mocker.patch("pandas.read_sql", return_value=mock_services_size_df)
    result = get_services_size(db_uri)
    mock_read_sql.assert_called_once_with(
        """
SELECT COUNT(*) FROM "pathwaysdos"."services";
""",
        db_uri,
    )
    assert result == expected_services_size


def test_get_services_columns_count(mocker: MockerFixture) -> None:
    mock_read_sql = mocker.patch(
        "pandas.read_sql", return_value=mock_services_columns_count_df
    )
    result = get_services_columns_count(db_uri)
    mock_read_sql.assert_called_once_with(
        """
SELECT COUNT(*)
FROM information_schema.columns
WHERE table_schema = 'pathwaysdos'
AND table_name = 'services';
""",
        db_uri,
    )
    assert result == expected_services_columns_count


def test_get_serviceendpoints_columns_count(mocker: MockerFixture) -> None:
    mock_read_sql = mocker.patch(
        "pandas.read_sql", return_value=mock_serviceendpoints_columns_count_df
    )
    result = get_serviceendpoints_columns_count(db_uri)
    mock_read_sql.assert_called_once_with(
        """
SELECT COUNT(*)
FROM information_schema.columns
WHERE table_schema = 'pathwaysdos'
AND table_name = 'serviceendpoints';
""",
        db_uri,
    )
    assert result == expected_serviceendpoints_columns_count
