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
WITH{WITH_GP_PRACTICE}
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
    FROM "gp_practice"
    LEFT JOIN "pathwaysdos"."services"  ON "gp_practice"."serviceid" = "services"."id"
    LEFT JOIN "pathwaysdos"."servicetypes" ON "services"."typeid" = "servicetypes"."id"
"""

QUERY_GP_ENDPOINTS = f"""
WITH{WITH_GP_PRACTICE}
SELECT
    "serviceendpoints".*
FROM "gp_practice"
LEFT JOIN "pathwaysdos"."serviceendpoints" ON "gp_practice"."serviceid" = "serviceendpoints"."serviceid"
"""

QUERY_GP_SERVICEDAYOPENINGTIMES = f"""
WITH{WITH_GP_PRACTICE}
SELECT
    "gp_practice"."serviceid",
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
WITH{WITH_GP_PRACTICE}
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


QUERY_CLINICAL_CODES = f"""
-- Define the WITH clause for GP practice
WITH{WITH_GP_PRACTICE},

-- Create a CTE for synonyms
synonyms AS (
SELECT
    symptomdiscriminatorid,
    ARRAY_AGG(name) as synonym_value
FROM pathwaysdos.symptomdiscriminatorsynonyms
GROUP BY symptomdiscriminatorid ),

-- Create a CTE for symptom group and symptom discriminator pairs
sg_sd_pairs AS (
SELECT
    sgsds.serviceid,
    json_build_object(
    'sg', json_build_object(
    'id', 'SG' || sg.id,
    'source', 'pathways',
    'codeType', 'Symptom Group (SG)',
    'codeID', sg.id,
    'codeValue', sg.name,
    'zCodeExists', COALESCE(sg.zcodeexists, false)
    ),
    'sd', json_build_object(
    'id', 'SD' || sd.id,
    'source', 'pathways',
    'codeType', 'Symptom Discriminator (SD)',
    'codeID', sd.id,
    'codeValue', sd.description,
    'synonyms', syn.synonym_value ) )::text AS sg_sd_pair
FROM pathwaysdos.servicesgsds sgsds
    LEFT JOIN pathwaysdos.symptomgroups sg ON sgsds.sgid = sg.id
    LEFT JOIN pathwaysdos.symptomdiscriminators sd ON sgsds.sdid = sd.id
    LEFT JOIN synonyms syn ON sd.id = syn.symptomdiscriminatorid
WHERE sgsds.sgid IS NOT NULL AND sgsds.sdid IS NOT NULL ),

-- Aggregate symptom group and symptom discriminator pairs by service ID
sg_sd_aggregated AS (
SELECT
    serviceid,
    ARRAY_AGG(DISTINCT sg_sd_pair) AS sg_sd_array
FROM sg_sd_pairs
GROUP BY serviceid ),

-- Create a CTE for dispositions
dispositions AS (
SELECT
    sd_join.serviceid,
    ARRAY_AGG(DISTINCT
    json_build_object(
    'id', d.dxcode,
    'source', 'pathways',
    'codeType', 'Disposition (Dx)',
    'codeID', d.dxcode,
    'codeValue', d.name,
    'dispositiontime', d.dispositiontime )::text ) AS dx_array
FROM pathwaysdos.servicedispositions sd_join
    JOIN pathwaysdos.dispositions d ON sd_join.dispositionid = d.id
WHERE d.dxcode IS NOT NULL
GROUP BY sd_join.serviceid )

-- Final query to join everything together
SELECT
    gp.serviceid,
    COALESCE(sg_sd.sg_sd_array, ARRAY[]::text[]) AS sg_sd_pairs,
    COALESCE(dx.dx_array, ARRAY[]::text[]) AS dispositions
FROM gp_practice gp
    LEFT JOIN sg_sd_aggregated sg_sd ON gp.serviceid = sg_sd.serviceid
    LEFT JOIN dispositions dx ON gp.serviceid = dx.serviceid
ORDER BY gp.serviceid;
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


def get_clinical_codes(db_uri: str) -> pd.DataFrame:
    return pd.read_sql(QUERY_CLINICAL_CODES, db_uri)
