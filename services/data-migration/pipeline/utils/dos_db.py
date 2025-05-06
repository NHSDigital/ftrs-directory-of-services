import pandas as pd

WITH_GP_PRACTICE = """
gp_practice AS (
    SELECT
        "services"."id" AS "serviceid"
    FROM "pathwaysdos"."services"
    LEFT JOIN "pathwaysdos"."servicestatuses" ON "services"."statusid" = "servicestatuses"."id"
    WHERE
        "servicestatuses"."name" = 'active'
        AND "services"."typeid" = '100'
        AND "services"."odscode" ~ '^[A-Za-z][0-9]{5}$'
)
"""

QUERY_GP_PRACTICE = f"""
WITH {WITH_GP_PRACTICE}
    SELECT
        "services"."name",
        "servicetypes"."name" AS "type",
        "services"."odscode",
        "services"."uid",
        "services"."id" AS "serviceid",
        "services"."publicphone",
        "services"."nonpublicphone",
        "services"."email",
        "services"."web",
        "services"."address",
        "services"."town",
        "services"."postcode",
        "services"."latitude",
        "services"."longitude"
    FROM "pathwaysdos"."services"
    LEFT JOIN "pathwaysdos"."servicestatuses" ON "services"."statusid" = "servicestatuses"."id"
    LEFT JOIN "pathwaysdos"."servicetypes" ON "services"."typeid" = "servicetypes"."id"
    WHERE
        "servicestatuses"."name" = 'active'
        AND "services"."typeid" = '100'
        AND "services"."odscode" ~ '^[A-Za-z][0-9]{5}$';
"""

QUERY_GP_ENDPOINTS = f"""
WITH {WITH_GP_PRACTICE}
SELECT
    "serviceendpoints".*
FROM "gp_practice"
LEFT JOIN "pathwaysdos"."serviceendpoints" ON "gp_practice"."serviceid" = "serviceendpoints"."serviceid"
"""

QUERY_GP_SERVICEDAYOPENINGTIMES = f"""
WITH {WITH_GP_PRACTICE}
SELECT
    "gp_practice"."serviceid",
    "servicedayopenings"."dayid",
    "servicedayopeningtimes"."starttime" as "availableStartTime",
    "servicedayopeningtimes"."endtime" as "availableEndTime",
    "openingtimedays"."name" as "dayOfWeek"
FROM "gp_practice"
INNER JOIN "pathwaysdos"."servicedayopenings"
    ON "gp_practice"."serviceid" = "servicedayopenings"."serviceid"
LEFT JOIN "pathwaysdos"."servicedayopeningtimes"
    ON "servicedayopenings"."id" = "servicedayopeningtimes"."servicedayopeningid"
LEFT JOIN "pathwaysdos"."openingtimedays"
    ON "servicedayopenings"."dayid" = "openingtimedays"."id"
"""

QUERY_GP_SERVICESPECIFIEDOPENINGTIMES = f"""
WITH {WITH_GP_PRACTICE}
SELECT
    "gp_practice"."serviceid",
    "servicespecifiedopeningdates"."date",
    "servicespecifiedopeningtimes"."starttime",
    "servicespecifiedopeningtimes"."endtime",
    "servicespecifiedopeningtimes"."isclosed"
FROM "gp_practice"
INNER JOIN "pathwaysdos"."servicespecifiedopeningdates"
    ON "gp_practice"."serviceid" = "servicespecifiedopeningdates"."serviceid"
LEFT JOIN "pathwaysdos"."servicespecifiedopeningtimes"
    ON "servicespecifiedopeningdates"."id" = "servicespecifiedopeningtimes"."servicespecifiedopeningdateid"
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


def get_gp_day_opening_times(db_uri: str) -> pd.DataFrame:
    return pd.read_sql(QUERY_GP_SERVICEDAYOPENINGTIMES, db_uri)


def get_gp_specified_opening_times(db_uri: str) -> pd.DataFrame:
    return pd.read_sql(QUERY_GP_SERVICESPECIFIEDOPENINGTIMES, db_uri)


def get_services_size(db_uri: str) -> int:
    return pd.read_sql(QUERY_SERVICES_SIZE, db_uri)["count"][0]


def get_services_columns_count(db_uri: str) -> int:
    return pd.read_sql(QUERY_SERVICES_COLUMNS, db_uri)["count"][0]


def get_serviceendpoints_columns_count(db_uri: str) -> int:
    return pd.read_sql(QUERY_SERVICEENDPOINTS_COLUMNS, db_uri)["count"][0]
