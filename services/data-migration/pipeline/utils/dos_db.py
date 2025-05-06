import pandas as pd

QUERY_GP_PRACTICE = """
    SELECT
        "services"."name",
        "servicetypes"."name" AS "type",
        "services"."odscode",
        "services"."uid",
        "services"."id" AS "serviceid",
        "services"."publicphone",
        "services"."nonpublicphone",
        "services"."email",
        "services"."web"
    FROM "pathwaysdos"."services"
    LEFT JOIN "pathwaysdos"."servicestatuses" ON "services"."statusid" = "servicestatuses"."id"
    LEFT JOIN "pathwaysdos"."servicetypes" ON "services"."typeid" = "servicetypes"."id"
    WHERE
        "servicestatuses"."name" = 'active'
        AND "services"."typeid" = '100'
        AND "services"."odscode" ~ '^[A-Za-z][0-9]{5}$';
"""

QUERY_GP_ENDPOINTS = """
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
"""

QUERY_SERVICES_SIZE = """
SELECT COUNT(*) FROM "pathwaysdos"."services";
"""

QUERY_SERVICES_COLUMNS = """
SELECT COUNT(*)
FROM information_schema.columns
WHERE table_schema = 'pathwaysdos'
AND table_name = 'services';
"""

QUERY_SERVICEENDPOINTS_COLUMNS = """
SELECT COUNT(*)
FROM information_schema.columns
WHERE table_schema = 'pathwaysdos'
AND table_name = 'serviceendpoints';
"""


def get_gp_practices(db_uri: str) -> pd.DataFrame:
    return pd.read_sql(QUERY_GP_PRACTICE, db_uri)


def get_gp_endpoints(db_uri: str) -> pd.DataFrame:
    return pd.read_sql(QUERY_GP_ENDPOINTS, db_uri)


def get_services_size(db_uri: str) -> int:
    return pd.read_sql(QUERY_SERVICES_SIZE, db_uri)["count"][0]


def get_services_columns_count(db_uri: str) -> int:
    return pd.read_sql(QUERY_SERVICES_COLUMNS, db_uri)["count"][0]


def get_serviceendpoints_columns_count(db_uri: str) -> int:
    return pd.read_sql(QUERY_SERVICEENDPOINTS_COLUMNS, db_uri)["count"][0]
