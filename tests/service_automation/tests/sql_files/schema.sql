--
-- PostgreSQL database dump
--

-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.9 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pathwaysdos; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA pathwaysdos;


--
-- Name: assignservicesuid(); Type: FUNCTION; Schema: pathwaysdos; Owner: -
--

CREATE FUNCTION pathwaysdos.assignservicesuid() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
 BEGIN
  if ( new.uid is null ) then
   new.uid := nextval('pathwaysdos.services_uid_seq');
  end if;
  return new;
 END;
$$;


--
-- Name: deletecapacitygrid(); Type: FUNCTION; Schema: pathwaysdos; Owner: -
--

CREATE FUNCTION pathwaysdos.deletecapacitygrid() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            BEGIN
                DELETE FROM pathwaysdos.capacityGridSheets
                WHERE capacityGridSheetId = OLD.capacityGridSheetId;
            EXCEPTION
                WHEN foreign_key_violation THEN NULL;
            END;
            RETURN NULL;
        END; $$;


--
-- Name: deletedispositiongroup(); Type: FUNCTION; Schema: pathwaysdos; Owner: -
--

CREATE FUNCTION pathwaysdos.deletedispositiongroup() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            BEGIN
                DELETE FROM pathwaysdos.dispositionGroups
                WHERE id = OLD.dispositionGroupId;
            EXCEPTION
                WHEN OTHERS THEN NULL;
            END;
            RETURN NULL;
        END; $$;


--
-- Name: deletesymptomgroup(); Type: FUNCTION; Schema: pathwaysdos; Owner: -
--

CREATE FUNCTION pathwaysdos.deletesymptomgroup() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            BEGIN
                DELETE FROM pathwaysdos.symptomGroups
                WHERE id = OLD.symptomGroupId;
            EXCEPTION
                WHEN foreign_key_violation THEN NULL;
            END;
            RETURN NULL;
        END; $$;


--
-- Name: indentify_missing_records(); Type: FUNCTION; Schema: pathwaysdos; Owner: -
--

CREATE FUNCTION pathwaysdos.indentify_missing_records() RETURNS text
    LANGUAGE plpgsql
    AS $$

BEGIN

--identify services with no service capacity records and write them to a temporary table
drop table if exists missingscservices;
create table missingscservices as select s.id,s.uid from services as s
left outer join servicecapacities as sc
on s.id = sc.serviceid
where sc.serviceid is null;
RETURN 'successful';
END
$$;


--
-- Name: insertserviceattributevalues(); Type: FUNCTION; Schema: pathwaysdos; Owner: -
--

CREATE FUNCTION pathwaysdos.insertserviceattributevalues() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      BEGIN
        INSERT INTO pathwaysdos.serviceattributevalues
		 (serviceattributeid, value)
		VALUES
		 (NEW.id, 'TRUE')
		,(NEW.id, 'FALSE');
      EXCEPTION
        WHEN OTHERS THEN NULL;
	  END;
	  RETURN NEW;
    END;
  $$;


--
-- Name: update_servicecapacity_table(); Type: FUNCTION; Schema: pathwaysdos; Owner: -
--

CREATE FUNCTION pathwaysdos.update_servicecapacity_table() RETURNS text
    LANGUAGE plpgsql
    AS $$

DECLARE rec RECORD;
BEGIN

drop table if exists rollbackTable;
create table rollbackTable(
	serviceid integer not null,
	servicecapacitiesid integer not null,
	createdtime date
);
FOR rec IN SELECT * FROM missingScServices
	LOOP
	with rows as (insert into servicecapacities (notes, modifiedbyid, modifiedby, modifieddate, serviceid, capacitystatusid)
	values (null,null,null,now(),rec.id,1)
	returning servicecapacities.id)
	insert into rollbackTable (serviceid, servicecapacitiesid, createdtime)
	values (rec.id, (select id from rows), now());
	END LOOP;
RETURN 'successful';
END
$$;


SET default_table_access_method = heap;

--
-- Name: agegroups; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.agegroups (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    fromyears integer NOT NULL,
    toyears integer NOT NULL
);


--
-- Name: capacitystatuses; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitystatuses (
    capacitystatusid integer NOT NULL,
    color character varying(255) NOT NULL
);


--
-- Name: capacitystatuses_capacitystatusid_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitystatuses_capacitystatusid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitystatuses_capacitystatusid_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitystatuses_capacitystatusid_seq OWNED BY pathwaysdos.capacitystatuses.capacitystatusid;


--
-- Name: changes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.changes (
    id character varying(255) NOT NULL,
    approvestatus character varying(255) NOT NULL,
    type character varying(255) NOT NULL,
    initiatorname character varying(255) NOT NULL,
    servicename character varying(255) NOT NULL,
    servicetype character varying(255) DEFAULT NULL::character varying,
    value text NOT NULL,
    createdtimestamp timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    creatorsname character varying(255) DEFAULT NULL::character varying,
    modifiedtimestamp timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    modifiersname character varying(255) DEFAULT NULL::character varying,
    serviceid integer,
    externalsystem character varying(100) DEFAULT NULL::character varying,
    externalref character varying(100) DEFAULT NULL::character varying,
    message text
);


--
-- Name: dispositiongroupdispositions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.dispositiongroupdispositions (
    id integer NOT NULL,
    dispositionid integer NOT NULL,
    dispositiongroupid integer NOT NULL
);


--
-- Name: dispositiongroupdispositions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.dispositiongroupdispositions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dispositiongroupdispositions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.dispositiongroupdispositions_id_seq OWNED BY pathwaysdos.dispositiongroupdispositions.id;


--
-- Name: dispositiongroups; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.dispositiongroups (
    id integer NOT NULL,
    uid integer NOT NULL,
    dispositiontime integer,
    defaultdos character varying(255) DEFAULT NULL::character varying,
    name character varying(255) NOT NULL
);


--
-- Name: dispositiongroups_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.dispositiongroups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dispositiongroups_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.dispositiongroups_id_seq OWNED BY pathwaysdos.dispositiongroups.id;


--
-- Name: dispositiongroupservicetypes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.dispositiongroupservicetypes (
    id integer NOT NULL,
    dispositiongroupid integer NOT NULL,
    servicetypeid integer NOT NULL
);


--
-- Name: dispositiongroupservicetypes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.dispositiongroupservicetypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dispositiongroupservicetypes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.dispositiongroupservicetypes_id_seq OWNED BY pathwaysdos.dispositiongroupservicetypes.id;


--
-- Name: dispositions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.dispositions (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    dxcode character varying(255) DEFAULT NULL::character varying,
    dispositiontime integer
);


--
-- Name: dispositions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.dispositions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dispositions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.dispositions_id_seq OWNED BY pathwaysdos.dispositions.id;


--
-- Name: dispositionservicetypes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.dispositionservicetypes (
    id integer NOT NULL,
    dispositionid integer NOT NULL,
    servicetypeid integer NOT NULL
);


--
-- Name: dispositionservicetypes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.dispositionservicetypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dispositionservicetypes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.dispositionservicetypes_id_seq OWNED BY pathwaysdos.dispositionservicetypes.id;


--
-- Name: genders; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.genders (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    letter character varying(1) NOT NULL
);


--
-- Name: genders_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.genders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: genders_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.genders_id_seq OWNED BY pathwaysdos.genders.id;


--
-- Name: groupserviceimports; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.groupserviceimports (
    id bigint NOT NULL,
    uid character varying(255),
    name character varying(255),
    status character varying(255),
    username character varying(255)
);


--
-- Name: groupserviceimports_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.groupserviceimports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: groupserviceimports_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.groupserviceimports_id_seq OWNED BY pathwaysdos.groupserviceimports.id;


--
-- Name: jobqueue; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.jobqueue (
    id integer NOT NULL,
    bashcommand text NOT NULL,
    completedstatus character varying(255) DEFAULT NULL::character varying,
    completedtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    completedresult character varying(255) DEFAULT NULL::character varying,
    scheduledtime timestamp(0) with time zone NOT NULL,
    startedtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone
);


--
-- Name: jobqueue_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.jobqueue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: jobqueue_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.jobqueue_id_seq OWNED BY pathwaysdos.jobqueue.id;


--
-- Name: ldaimports; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.ldaimports (
    id bigint NOT NULL,
    organisationtypeid integer,
    orgcode character varying(10) NOT NULL,
    area character varying(100) NOT NULL,
    postcode character varying(10) NOT NULL
);


--
-- Name: ldaimports_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.ldaimports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ldaimports_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.ldaimports_id_seq OWNED BY pathwaysdos.ldaimports.id;


--
-- Name: legacycollisions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.legacycollisions (
    id integer NOT NULL,
    legacyid integer NOT NULL,
    serviceagerangeid integer NOT NULL
);


--
-- Name: legacycollisions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.legacycollisions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: legacycollisions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.legacycollisions_id_seq OWNED BY pathwaysdos.legacycollisions.id;


--
-- Name: locations; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.locations (
    id integer NOT NULL,
    postcode character varying(255) DEFAULT NULL::character varying,
    easting integer,
    northing integer,
    postaltown character varying(255) DEFAULT NULL::character varying,
    postaladdress character varying(255) DEFAULT NULL::character varying,
    latitude double precision,
    longitude double precision
);


--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.locations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.locations_id_seq OWNED BY pathwaysdos.locations.id;


--
-- Name: news; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.news (
    id integer NOT NULL,
    uid character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    detail text NOT NULL,
    creatorname character varying(255) NOT NULL,
    createtimestamp timestamp(0) with time zone DEFAULT NULL::timestamp with time zone
);


--
-- Name: news_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.news_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: news_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.news_id_seq OWNED BY pathwaysdos.news.id;


--
-- Name: newsacknowledgedbyusers; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.newsacknowledgedbyusers (
    id integer NOT NULL,
    newsid integer,
    userid integer
);


--
-- Name: newsacknowledgedbyusers_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.newsacknowledgedbyusers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: newsacknowledgedbyusers_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.newsacknowledgedbyusers_id_seq OWNED BY pathwaysdos.newsacknowledgedbyusers.id;


--
-- Name: newsforpermissions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.newsforpermissions (
    id integer NOT NULL,
    newsid integer,
    permissionid integer
);


--
-- Name: newsforpermissions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.newsforpermissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: newsforpermissions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.newsforpermissions_id_seq OWNED BY pathwaysdos.newsforpermissions.id;


--
-- Name: odsimports; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.odsimports (
    id bigint NOT NULL,
    pcd2 character varying(10) NOT NULL,
    pcds character varying(10) NOT NULL,
    dointr integer,
    doterm integer,
    oseast100m numeric,
    osnrth100m numeric,
    oscty character varying(10),
    odslaua character varying(5),
    oslaua character varying(10),
    osward character varying(10),
    usertype smallint,
    osgrdind smallint,
    ctry character varying(10),
    oshlthau character varying(3),
    rgn character varying(10),
    oldha character varying(3),
    nhser character varying(3),
    ccg character varying(10) NOT NULL,
    psed character varying(10),
    cened character varying(6),
    edind character varying(1),
    ward98 character varying(6),
    oa01 character varying(10),
    nhsrlo character varying(3),
    hro character varying(3),
    lsoa01 character varying(10),
    ur01ind character varying(1),
    msoa01 character varying(10),
    cannet character varying(3),
    scn character varying(3),
    oshaprev character varying(3),
    oldpct character varying(3),
    oldhro character varying(3),
    pcon character varying(10),
    canreg character varying(5),
    pct character varying(3),
    oseast1m numeric,
    osnrth1m numeric,
    oa11 character varying(10),
    lsoa11 character varying(10),
    msoa11 character varying(10),
    calncv character varying(10),
    stp character varying(10)
);


--
-- Name: COLUMN odsimports.calncv; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.odsimports.calncv IS 'Cancer Alliance or National Cancer Vanguard identifier.';


--
-- Name: COLUMN odsimports.stp; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.odsimports.stp IS 'Sustainability and Transformation Partnership identifier.';


--
-- Name: odsimports_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.odsimports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: odsimports_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.odsimports_id_seq OWNED BY pathwaysdos.odsimports.id;


--
-- Name: odspostcodes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.odspostcodes (
    id bigint NOT NULL,
    postcode character varying(10) NOT NULL,
    orgcode character varying(10) NOT NULL,
    createdtime timestamp(0) with time zone NOT NULL,
    mappedtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    deletedtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone
);


--
-- Name: odspostcodes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.odspostcodes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: odspostcodes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.odspostcodes_id_seq OWNED BY pathwaysdos.odspostcodes.id;


--
-- Name: openingtimedays; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.openingtimedays (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


--
-- Name: openingtimedays_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.openingtimedays_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: openingtimedays_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.openingtimedays_id_seq OWNED BY pathwaysdos.openingtimedays.id;


--
-- Name: organisationpostcodes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.organisationpostcodes (
    id integer NOT NULL,
    locationid integer NOT NULL,
    organisationid integer NOT NULL
);


--
-- Name: organisationpostcodes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.organisationpostcodes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organisationpostcodes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.organisationpostcodes_id_seq OWNED BY pathwaysdos.organisationpostcodes.id;


--
-- Name: organisationrankingstrategies; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.organisationrankingstrategies (
    id integer NOT NULL,
    servicetypeid integer,
    localranking integer,
    organisationid integer NOT NULL
);


--
-- Name: organisationrankingstrategies_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.organisationrankingstrategies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organisationrankingstrategies_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.organisationrankingstrategies_id_seq OWNED BY pathwaysdos.organisationrankingstrategies.id;


--
-- Name: organisations; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.organisations (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(10) NOT NULL,
    startdate timestamp(0) with time zone NOT NULL,
    enddate timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    organisationtypeid integer NOT NULL,
    islocalrankingused boolean DEFAULT true NOT NULL,
    subregionid integer,
    lastareaupdate timestamp with time zone
);


--
-- Name: organisations_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.organisations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organisations_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.organisations_id_seq OWNED BY pathwaysdos.organisations.id;


--
-- Name: organisationtypes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.organisationtypes (
    id integer NOT NULL,
    name text
);


--
-- Name: organisationtypes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.organisationtypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: organisationtypes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.organisationtypes_id_seq OWNED BY pathwaysdos.organisationtypes.id;


--
-- Name: permissionattributedict; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.permissionattributedict (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


--
-- Name: permissionattributedict_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.permissionattributedict_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permissionattributedict_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.permissionattributedict_id_seq OWNED BY pathwaysdos.permissionattributedict.id;


--
-- Name: permissionattributes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.permissionattributes (
    id integer NOT NULL,
    permissionid integer,
    permissionattributedictid integer
);


--
-- Name: permissionattributes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.permissionattributes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permissionattributes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.permissionattributes_id_seq OWNED BY pathwaysdos.permissionattributes.id;


--
-- Name: permissions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.permissions (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(255) DEFAULT NULL::character varying,
    functionalarea character varying(255) DEFAULT NULL::character varying
);


--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.permissions_id_seq OWNED BY pathwaysdos.permissions.id;


--
-- Name: publicholidays; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.publicholidays (
    id integer NOT NULL,
    holidaydate timestamp with time zone,
    description character varying(100) DEFAULT NULL::character varying
);


--
-- Name: TABLE publicholidays; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON TABLE pathwaysdos.publicholidays IS 'Public holidays in England.';


--
-- Name: COLUMN publicholidays.id; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.publicholidays.id IS 'Identifier for public holidays.';


--
-- Name: COLUMN publicholidays.holidaydate; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.publicholidays.holidaydate IS 'Date of public holiday.';


--
-- Name: COLUMN publicholidays.description; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.publicholidays.description IS 'Narrative for public holiday, e.g. Spring Bank Holiday.';


--
-- Name: publicholidays_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.publicholidays_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: publicholidays_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.publicholidays_id_seq OWNED BY pathwaysdos.publicholidays.id;


--
-- Name: purgedusers; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.purgedusers (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    firstname character varying(255) NOT NULL,
    lastname character varying(255) NOT NULL,
    email character varying(255) DEFAULT NULL::character varying,
    password character varying(255) DEFAULT NULL::character varying,
    badpasswordcount integer,
    badpasswordtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    phone character varying(255) DEFAULT NULL::character varying,
    status character varying(255) DEFAULT NULL::character varying,
    createdtime timestamp(0) with time zone NOT NULL,
    lastlogintime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    homeorganisation character varying(255) DEFAULT NULL::character varying,
    accessreason text,
    approvedby character varying(255) DEFAULT NULL::character varying,
    approveddate timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    validationtoken character varying(255) DEFAULT NULL::character varying,
    purgeddate timestamp(0) with time zone NOT NULL
);


--
-- Name: referralroles; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.referralroles (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


--
-- Name: savedsearches; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.savedsearches (
    id integer NOT NULL,
    params text NOT NULL,
    isshared boolean DEFAULT false NOT NULL
);


--
-- Name: savedsearches_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.savedsearches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: savedsearches_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.savedsearches_id_seq OWNED BY pathwaysdos.savedsearches.id;


--
-- Name: scenariobundles; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.scenariobundles (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    createdtime timestamp without time zone NOT NULL
);


--
-- Name: scenariobundles_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.scenariobundles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scenariobundles_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.scenariobundles_id_seq OWNED BY pathwaysdos.scenariobundles.id;


--
-- Name: scenarios; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.scenarios (
    id integer NOT NULL,
    scenariobundleid integer NOT NULL,
    scenarioid integer NOT NULL,
    symptomgroupid integer NOT NULL,
    dispositionid integer NOT NULL,
    dispositiongroupid integer NOT NULL,
    symptomdiscriminatorid integer NOT NULL,
    ageid integer NOT NULL,
    genderid integer NOT NULL,
    triagereport character varying,
    createdtime timestamp with time zone NOT NULL,
    retiredtime timestamp with time zone
);


--
-- Name: scenarios_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.scenarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scenarios_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.scenarios_id_seq OWNED BY pathwaysdos.scenarios.id;


--
-- Name: searchdistances; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.searchdistances (
    id bigint NOT NULL,
    code character varying(10) NOT NULL,
    radius numeric(3,1) NOT NULL
);


--
-- Name: TABLE searchdistances; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON TABLE pathwaysdos.searchdistances IS 'Search radius distances used by search algorithms.';


--
-- Name: COLUMN searchdistances.id; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.searchdistances.id IS 'Identifier for search distances.';


--
-- Name: COLUMN searchdistances.code; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.searchdistances.code IS 'Full postcode, sector code, or outcode assigned a search radius.';


--
-- Name: COLUMN searchdistances.radius; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.searchdistances.radius IS 'Radius in kilometres used by search algorithms.';


--
-- Name: searchdistances_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.searchdistances_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: searchdistances_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.searchdistances_id_seq OWNED BY pathwaysdos.searchdistances.id;


--
-- Name: searchimports; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.searchimports (
    id bigint NOT NULL,
    code character varying(10) NOT NULL,
    radius numeric(3,1) NOT NULL
);


--
-- Name: TABLE searchimports; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON TABLE pathwaysdos.searchimports IS 'Staging table used to import search distances.  Always truncated prior to import.';


--
-- Name: COLUMN searchimports.id; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.searchimports.id IS 'Identifier for search imports.';


--
-- Name: COLUMN searchimports.code; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.searchimports.code IS 'Full postcode, sector code, or outcode assigned a search radius.';


--
-- Name: COLUMN searchimports.radius; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.searchimports.radius IS 'Radius in kilometres used by search algorithm.';


--
-- Name: searchimports_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.searchimports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: searchimports_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.searchimports_id_seq OWNED BY pathwaysdos.searchimports.id;


--
-- Name: serviceagegroups; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.serviceagegroups (
    id integer NOT NULL,
    serviceid integer NOT NULL,
    agegroupid integer NOT NULL
);


--
-- Name: serviceagegroups_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.serviceagegroups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: serviceagegroups_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.serviceagegroups_id_seq OWNED BY pathwaysdos.serviceagegroups.id;


--
-- Name: serviceagerange; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.serviceagerange (
    id integer NOT NULL,
    daysfrom double precision NOT NULL,
    daysto double precision NOT NULL,
    serviceid integer NOT NULL
);


--
-- Name: serviceagerange_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.serviceagerange_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: serviceagerange_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.serviceagerange_id_seq OWNED BY pathwaysdos.serviceagerange.id;


--
-- Name: servicealignments; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicealignments (
    id bigint NOT NULL,
    serviceid integer NOT NULL,
    commissioningorganisationid integer NOT NULL,
    islimited boolean,
    CONSTRAINT servicealignments_chk1 CHECK (((serviceid <> commissioningorganisationid) OR (serviceid IS NULL) OR (commissioningorganisationid IS NULL)))
);


--
-- Name: servicealignments_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicealignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicealignments_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicealignments_id_seq OWNED BY pathwaysdos.servicealignments.id;


--
-- Name: serviceattributes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.serviceattributes (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(255) NOT NULL,
    serviceattributetypeid integer NOT NULL,
    status boolean NOT NULL,
    createddatetime timestamp with time zone NOT NULL,
    createduserid integer NOT NULL,
    modifieddatetime timestamp with time zone NOT NULL,
    modifieduserid integer NOT NULL
);


--
-- Name: serviceattributes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.serviceattributes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: serviceattributes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.serviceattributes_id_seq OWNED BY pathwaysdos.serviceattributes.id;


--
-- Name: serviceattributetypes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.serviceattributetypes (
    id integer NOT NULL,
    type character varying(50) NOT NULL,
    description character varying(255),
    typevaluesjson character varying(255)
);


--
-- Name: serviceattributetypes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.serviceattributetypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: serviceattributetypes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.serviceattributetypes_id_seq OWNED BY pathwaysdos.serviceattributetypes.id;


--
-- Name: serviceattributevalues; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.serviceattributevalues (
    id integer NOT NULL,
    serviceattributeid integer NOT NULL,
    value character varying(255) NOT NULL
);


--
-- Name: serviceattributevalues_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.serviceattributevalues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: serviceattributevalues_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.serviceattributevalues_id_seq OWNED BY pathwaysdos.serviceattributevalues.id;


--
-- Name: servicecapacities; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicecapacities (
    id integer NOT NULL,
    notes text,
    modifiedbyid integer,
    modifiedby text,
    modifieddate timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    serviceid integer,
    capacitystatusid integer,
    resetdatetime timestamp with time zone
);


--
-- Name: COLUMN servicecapacities.resetdatetime; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.servicecapacities.resetdatetime IS 'Date and time after which the capacity status will be reset to Green.';


--
-- Name: servicecapacities_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicecapacities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicecapacities_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicecapacities_id_seq OWNED BY pathwaysdos.servicecapacities.id;


--
-- Name: servicecapacitygrids_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicecapacitygrids_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicedayopenings; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicedayopenings (
    id integer NOT NULL,
    serviceid integer NOT NULL,
    dayid integer
);


--
-- Name: servicedayopenings_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicedayopenings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicedayopenings_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicedayopenings_id_seq OWNED BY pathwaysdos.servicedayopenings.id;


--
-- Name: servicedayopeningtimes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicedayopeningtimes (
    id integer NOT NULL,
    starttime time(0) without time zone NOT NULL,
    endtime time(0) without time zone NOT NULL,
    servicedayopeningid integer
);


--
-- Name: servicedayopeningtimes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicedayopeningtimes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicedayopeningtimes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicedayopeningtimes_id_seq OWNED BY pathwaysdos.servicedayopeningtimes.id;


--
-- Name: servicedispositions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicedispositions (
    id integer NOT NULL,
    serviceid integer NOT NULL,
    dispositionid integer NOT NULL
);


--
-- Name: servicedispositions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicedispositions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicedispositions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicedispositions_id_seq OWNED BY pathwaysdos.servicedispositions.id;


--
-- Name: serviceendpoints; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.serviceendpoints (
    id integer NOT NULL,
    endpointorder integer,
    transport character varying(255) DEFAULT NULL::character varying,
    format character varying(255) DEFAULT NULL::character varying,
    interaction character varying(255) DEFAULT NULL::character varying,
    businessscenario character varying(255) DEFAULT NULL::character varying,
    address character varying(255) DEFAULT NULL::character varying,
    comment text,
    iscompressionenabled character varying(255) DEFAULT NULL::character varying,
    serviceid integer NOT NULL
);


--
-- Name: serviceendpoints_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.serviceendpoints_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: serviceendpoints_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.serviceendpoints_id_seq OWNED BY pathwaysdos.serviceendpoints.id;


--
-- Name: servicegenders; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicegenders (
    id integer NOT NULL,
    serviceid integer,
    genderid integer
);


--
-- Name: servicegenders_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicegenders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicegenders_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicegenders_id_seq OWNED BY pathwaysdos.servicegenders.id;


--
-- Name: servicehistories; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicehistories (
    serviceid integer NOT NULL,
    history text NOT NULL
);


--
-- Name: servicenotes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicenotes (
    id integer NOT NULL,
    note character varying(255) NOT NULL,
    createdby integer,
    serviceid integer NOT NULL,
    createddate timestamp(0) with time zone NOT NULL
);


--
-- Name: servicenotes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicenotes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicenotes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicenotes_id_seq OWNED BY pathwaysdos.servicenotes.id;


--
-- Name: servicephonenumbers; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicephonenumbers (
    id integer NOT NULL,
    serviceid integer NOT NULL,
    phonenumber character varying(20) NOT NULL,
    ispublic boolean NOT NULL,
    phonedescription character varying(255) NOT NULL
);


--
-- Name: servicephonenumbers_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicephonenumbers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicephonenumbers_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicephonenumbers_id_seq OWNED BY pathwaysdos.servicephonenumbers.id;


--
-- Name: servicerankingstrategies; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicerankingstrategies (
    id integer NOT NULL,
    servicetype integer,
    localranking integer,
    serviceid integer NOT NULL
);


--
-- Name: servicerankingstrategies_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicerankingstrategies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicerankingstrategies_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicerankingstrategies_id_seq OWNED BY pathwaysdos.servicerankingstrategies.id;


--
-- Name: servicereferralroles; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicereferralroles (
    id integer NOT NULL,
    serviceid integer,
    referralroleid integer
);


--
-- Name: servicereferralroles_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicereferralroles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicereferralroles_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicereferralroles_id_seq OWNED BY pathwaysdos.servicereferralroles.id;


--
-- Name: servicereferrals; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicereferrals (
    id integer NOT NULL,
    referralserviceid integer NOT NULL,
    referredserviceid integer NOT NULL
);


--
-- Name: servicereferrals_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicereferrals_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicereferrals_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicereferrals_id_seq OWNED BY pathwaysdos.servicereferrals.id;


--
-- Name: services; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.services (
    id integer NOT NULL,
    uid character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    odscode character varying(255) DEFAULT NULL::character varying,
    isnational character varying(255) DEFAULT NULL::character varying,
    openallhours boolean DEFAULT false NOT NULL,
    publicreferralinstructions text,
    telephonetriagereferralinstructions text,
    restricttoreferrals boolean DEFAULT false NOT NULL,
    address character varying(512) DEFAULT NULL::character varying,
    town character varying(255) DEFAULT NULL::character varying,
    postcode character varying(255) DEFAULT NULL::character varying,
    easting integer,
    northing integer,
    publicphone character varying(255) DEFAULT NULL::character varying,
    nonpublicphone character varying(255) DEFAULT NULL::character varying,
    fax character varying(255) DEFAULT NULL::character varying,
    email character varying(255) DEFAULT NULL::character varying,
    web character varying(512) DEFAULT NULL::character varying,
    createdby character varying(255) DEFAULT NULL::character varying,
    createdtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    modifiedby character varying(255) DEFAULT NULL::character varying,
    modifiedtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    lasttemplatename text,
    lasttemplateid integer,
    typeid integer,
    parentid integer,
    subregionid integer,
    statusid integer,
    organisationid integer,
    returnifopenminutes integer,
    publicname character varying(255),
    latitude double precision,
    longitude double precision,
    professionalreferralinfo text,
    lastverified timestamp with time zone,
    nextverificationdue timestamp with time zone
);


--
-- Name: COLUMN services.returnifopenminutes; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.services.returnifopenminutes IS 'The service will only return from a search if currently open or due to open within the timeframe.';


--
-- Name: COLUMN services.publicname; Type: COMMENT; Schema: pathwaysdos; Owner: -
--

COMMENT ON COLUMN pathwaysdos.services.publicname IS 'The service name as it is known publically.';


--
-- Name: services_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.services_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.services_id_seq OWNED BY pathwaysdos.services.id;


--
-- Name: services_uid_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.services_uid_seq
    START WITH 2000000000
    INCREMENT BY 1
    MINVALUE 2000000000
    MAXVALUE 2147483647
    CACHE 1;


--
-- Name: serviceserviceattributes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.serviceserviceattributes (
    id integer NOT NULL,
    serviceattributeid integer NOT NULL,
    serviceattributevalueid integer,
    serviceid integer NOT NULL,
    priority integer,
    servicevalue character varying(255),
    dateassignedtoservice timestamp with time zone,
    associatinguserid integer
);


--
-- Name: serviceserviceattributes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.serviceserviceattributes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: serviceserviceattributes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.serviceserviceattributes_id_seq OWNED BY pathwaysdos.serviceserviceattributes.id;


--
-- Name: servicesgsds; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicesgsds (
    id integer NOT NULL,
    serviceid integer NOT NULL,
    sdid integer NOT NULL,
    sgid integer NOT NULL
);


--
-- Name: servicesgsds_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicesgsds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicesgsds_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicesgsds_id_seq OWNED BY pathwaysdos.servicesgsds.id;


--
-- Name: servicespecifiedopeningdates; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicespecifiedopeningdates (
    id integer NOT NULL,
    date date NOT NULL,
    serviceid integer
);


--
-- Name: servicespecifiedopeningdates_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicespecifiedopeningdates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicespecifiedopeningdates_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicespecifiedopeningdates_id_seq OWNED BY pathwaysdos.servicespecifiedopeningdates.id;


--
-- Name: servicespecifiedopeningtimes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicespecifiedopeningtimes (
    id integer NOT NULL,
    starttime time(0) without time zone NOT NULL,
    endtime time(0) without time zone NOT NULL,
    isclosed boolean NOT NULL,
    servicespecifiedopeningdateid integer
);


--
-- Name: servicespecifiedopeningtimes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicespecifiedopeningtimes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicespecifiedopeningtimes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicespecifiedopeningtimes_id_seq OWNED BY pathwaysdos.servicespecifiedopeningtimes.id;


--
-- Name: servicestatuses; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicestatuses (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


--
-- Name: servicestatuses_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.servicestatuses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: servicestatuses_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicestatuses_id_seq OWNED BY pathwaysdos.servicestatuses.id;


--
-- Name: servicetypes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicetypes (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    nationalranking character varying(255) DEFAULT NULL::character varying,
    searchcapacitystatus boolean,
    capacitymodel character varying(255) DEFAULT NULL::character varying,
    capacityreset character varying(255) DEFAULT NULL::character varying
);


--
-- Name: srsbackup; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.srsbackup (
    id integer,
    servicetype integer,
    localranking integer,
    serviceid integer
);


--
-- Name: symptomdiscriminators; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.symptomdiscriminators (
    id integer NOT NULL,
    description character varying(255) NOT NULL
);


--
-- Name: symptomdiscriminatorsynonyms; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.symptomdiscriminatorsynonyms (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    symptomdiscriminatorid integer NOT NULL
);


--
-- Name: symptomdiscriminatorsynonyms_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.symptomdiscriminatorsynonyms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: symptomdiscriminatorsynonyms_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.symptomdiscriminatorsynonyms_id_seq OWNED BY pathwaysdos.symptomdiscriminatorsynonyms.id;


--
-- Name: symptomgroups; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.symptomgroups (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    zcodeexists boolean
);


--
-- Name: symptomgroupsymptomdiscriminators; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.symptomgroupsymptomdiscriminators (
    id integer NOT NULL,
    symptomgroupid integer NOT NULL,
    symptomdiscriminatorid integer NOT NULL
);


--
-- Name: symptomgroupsymptomdiscriminators_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.symptomgroupsymptomdiscriminators_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: symptomgroupsymptomdiscriminators_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.symptomgroupsymptomdiscriminators_id_seq OWNED BY pathwaysdos.symptomgroupsymptomdiscriminators.id;


--
-- Name: userpermissions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.userpermissions (
    id integer NOT NULL,
    userid integer,
    permissionid integer
);


--
-- Name: userpermissions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.userpermissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: userpermissions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.userpermissions_id_seq OWNED BY pathwaysdos.userpermissions.id;


--
-- Name: userreferralroles; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.userreferralroles (
    id integer NOT NULL,
    userid integer,
    referralroleid integer
);


--
-- Name: userreferralroles_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.userreferralroles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: userreferralroles_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.userreferralroles_id_seq OWNED BY pathwaysdos.userreferralroles.id;


--
-- Name: userregions; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.userregions (
    id integer NOT NULL,
    userid integer,
    regionid integer
);


--
-- Name: userregions_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.userregions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: userregions_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.userregions_id_seq OWNED BY pathwaysdos.userregions.id;


--
-- Name: users; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.users (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    firstname character varying(255) NOT NULL,
    lastname character varying(255) NOT NULL,
    email character varying(255) DEFAULT NULL::character varying,
    badpasswordcount integer,
    badpasswordtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    phone character varying(255) DEFAULT NULL::character varying,
    status character varying(255) DEFAULT NULL::character varying,
    createdtime timestamp(0) with time zone NOT NULL,
    lastlogintime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    homeorganisation character varying(255) DEFAULT NULL::character varying,
    accessreason text,
    approvedby character varying(255) DEFAULT NULL::character varying,
    approveddate timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    validationtoken character varying(255) DEFAULT NULL::character varying,
    passsecure character varying(255),
    webserviceonly boolean DEFAULT false NOT NULL,
    passsecureupdatedat timestamp with time zone,
    passsecurehistory jsonb,
    careidentityid character varying(255) DEFAULT NULL::character varying
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.users_id_seq OWNED BY pathwaysdos.users.id;


--
-- Name: usersavedsearches; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.usersavedsearches (
    id integer NOT NULL,
    userid integer,
    savedsearchid integer
);


--
-- Name: usersavedsearches_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.usersavedsearches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usersavedsearches_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.usersavedsearches_id_seq OWNED BY pathwaysdos.usersavedsearches.id;


--
-- Name: userservices; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.userservices (
    id integer NOT NULL,
    userid integer,
    serviceid integer
);


--
-- Name: userservices_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.userservices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: userservices_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.userservices_id_seq OWNED BY pathwaysdos.userservices.id;


--
-- Name: capacitystatuses capacitystatusid; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitystatuses ALTER COLUMN capacitystatusid SET DEFAULT nextval('pathwaysdos.capacitystatuses_capacitystatusid_seq'::regclass);


--
-- Name: dispositiongroupdispositions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupdispositions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.dispositiongroupdispositions_id_seq'::regclass);


--
-- Name: dispositiongroups id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroups ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.dispositiongroups_id_seq'::regclass);


--
-- Name: dispositiongroupservicetypes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupservicetypes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.dispositiongroupservicetypes_id_seq'::regclass);


--
-- Name: dispositions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.dispositions_id_seq'::regclass);


--
-- Name: dispositionservicetypes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositionservicetypes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.dispositionservicetypes_id_seq'::regclass);


--
-- Name: genders id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.genders ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.genders_id_seq'::regclass);


--
-- Name: groupserviceimports id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.groupserviceimports ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.groupserviceimports_id_seq'::regclass);


--
-- Name: jobqueue id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.jobqueue ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.jobqueue_id_seq'::regclass);


--
-- Name: ldaimports id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.ldaimports ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.ldaimports_id_seq'::regclass);


--
-- Name: legacycollisions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.legacycollisions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.legacycollisions_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.locations ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.locations_id_seq'::regclass);


--
-- Name: news id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.news ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.news_id_seq'::regclass);


--
-- Name: newsacknowledgedbyusers id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsacknowledgedbyusers ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.newsacknowledgedbyusers_id_seq'::regclass);


--
-- Name: newsforpermissions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsforpermissions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.newsforpermissions_id_seq'::regclass);


--
-- Name: odsimports id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.odsimports ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.odsimports_id_seq'::regclass);


--
-- Name: odspostcodes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.odspostcodes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.odspostcodes_id_seq'::regclass);


--
-- Name: openingtimedays id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.openingtimedays ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.openingtimedays_id_seq'::regclass);


--
-- Name: organisationpostcodes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationpostcodes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.organisationpostcodes_id_seq'::regclass);


--
-- Name: organisationrankingstrategies id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationrankingstrategies ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.organisationrankingstrategies_id_seq'::regclass);


--
-- Name: organisations id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisations ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.organisations_id_seq'::regclass);


--
-- Name: organisationtypes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationtypes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.organisationtypes_id_seq'::regclass);


--
-- Name: permissionattributedict id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissionattributedict ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.permissionattributedict_id_seq'::regclass);


--
-- Name: permissionattributes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissionattributes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.permissionattributes_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.permissions_id_seq'::regclass);


--
-- Name: publicholidays id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.publicholidays ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.publicholidays_id_seq'::regclass);


--
-- Name: savedsearches id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.savedsearches ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.savedsearches_id_seq'::regclass);


--
-- Name: scenariobundles id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenariobundles ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.scenariobundles_id_seq'::regclass);


--
-- Name: scenarios id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenarios ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.scenarios_id_seq'::regclass);


--
-- Name: searchdistances id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.searchdistances ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.searchdistances_id_seq'::regclass);


--
-- Name: searchimports id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.searchimports ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.searchimports_id_seq'::regclass);


--
-- Name: serviceagegroups id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceagegroups ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.serviceagegroups_id_seq'::regclass);


--
-- Name: serviceagerange id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceagerange ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.serviceagerange_id_seq'::regclass);


--
-- Name: servicealignments id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicealignments ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicealignments_id_seq'::regclass);


--
-- Name: serviceattributes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.serviceattributes_id_seq'::regclass);


--
-- Name: serviceattributetypes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributetypes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.serviceattributetypes_id_seq'::regclass);


--
-- Name: serviceattributevalues id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributevalues ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.serviceattributevalues_id_seq'::regclass);


--
-- Name: servicecapacities id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacities ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicecapacities_id_seq'::regclass);


--
-- Name: servicedayopenings id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedayopenings ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicedayopenings_id_seq'::regclass);


--
-- Name: servicedayopeningtimes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedayopeningtimes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicedayopeningtimes_id_seq'::regclass);


--
-- Name: servicedispositions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedispositions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicedispositions_id_seq'::regclass);


--
-- Name: serviceendpoints id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceendpoints ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.serviceendpoints_id_seq'::regclass);


--
-- Name: servicegenders id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicegenders ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicegenders_id_seq'::regclass);


--
-- Name: servicenotes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicenotes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicenotes_id_seq'::regclass);


--
-- Name: servicephonenumbers id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicephonenumbers ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicephonenumbers_id_seq'::regclass);


--
-- Name: servicerankingstrategies id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicerankingstrategies ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicerankingstrategies_id_seq'::regclass);


--
-- Name: servicereferralroles id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferralroles ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicereferralroles_id_seq'::regclass);


--
-- Name: servicereferrals id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferrals ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicereferrals_id_seq'::regclass);


--
-- Name: services id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.services ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.services_id_seq'::regclass);


--
-- Name: serviceserviceattributes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceserviceattributes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.serviceserviceattributes_id_seq'::regclass);


--
-- Name: servicesgsds id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicesgsds ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicesgsds_id_seq'::regclass);


--
-- Name: servicespecifiedopeningdates id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicespecifiedopeningdates ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicespecifiedopeningdates_id_seq'::regclass);


--
-- Name: servicespecifiedopeningtimes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicespecifiedopeningtimes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicespecifiedopeningtimes_id_seq'::regclass);


--
-- Name: servicestatuses id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicestatuses ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicestatuses_id_seq'::regclass);


--
-- Name: symptomdiscriminatorsynonyms id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomdiscriminatorsynonyms ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.symptomdiscriminatorsynonyms_id_seq'::regclass);


--
-- Name: symptomgroupsymptomdiscriminators id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomgroupsymptomdiscriminators ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.symptomgroupsymptomdiscriminators_id_seq'::regclass);


--
-- Name: userpermissions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userpermissions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.userpermissions_id_seq'::regclass);


--
-- Name: userreferralroles id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userreferralroles ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.userreferralroles_id_seq'::regclass);


--
-- Name: userregions id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userregions ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.userregions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.users ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.users_id_seq'::regclass);


--
-- Name: usersavedsearches id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.usersavedsearches ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.usersavedsearches_id_seq'::regclass);


--
-- Name: userservices id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userservices ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.userservices_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

