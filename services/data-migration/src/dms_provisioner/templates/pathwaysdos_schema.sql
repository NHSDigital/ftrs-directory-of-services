--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: capacitygridconditionalstyles; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridconditionalstyles (
    id integer NOT NULL,
    conditionalstylename character varying(255) NOT NULL
);


--
-- Name: capacitygridconditionalstyles_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridconditionalstyles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridconditionalstyles_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridconditionalstyles_id_seq OWNED BY pathwaysdos.capacitygridconditionalstyles.id;


--
-- Name: capacitygridcustomformulas; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridcustomformulas (
    capacitygridcustomformulaid integer NOT NULL,
    capacitygridsheetid bigint NOT NULL,
    uid character varying(255) NOT NULL,
    modifiedtime timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    capacitygriddataid integer
);


--
-- Name: capacitygridcustomformulas_capacitygridcustomformulaid_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridcustomformulas_capacitygridcustomformulaid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridcustomformulas_capacitygridcustomformulaid_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridcustomformulas_capacitygridcustomformulaid_seq OWNED BY pathwaysdos.capacitygridcustomformulas.capacitygridcustomformulaid;


--
-- Name: capacitygridcustomformulastyles; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridcustomformulastyles (
    id integer NOT NULL,
    formulaid integer,
    styleid integer
);


--
-- Name: capacitygridcustomformulastyles_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridcustomformulastyles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridcustomformulastyles_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridcustomformulastyles_id_seq OWNED BY pathwaysdos.capacitygridcustomformulastyles.id;


--
-- Name: capacitygriddata; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygriddata (
    capacitygriddataid integer NOT NULL,
    columnid integer,
    rowid integer,
    data text,
    style character varying(255) DEFAULT NULL::character varying,
    parsed text,
    calc character varying(255) DEFAULT NULL::character varying,
    uid character varying(255) DEFAULT NULL::character varying,
    modifiedtimestamp timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    capacitygridsheetid bigint
);


--
-- Name: capacitygriddata_capacitygriddataid_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygriddata_capacitygriddataid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygriddata_capacitygriddataid_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygriddata_capacitygriddataid_seq OWNED BY pathwaysdos.capacitygriddata.capacitygriddataid;


--
-- Name: capacitygridheaders; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridheaders (
    capacitygridheaderid integer NOT NULL,
    uid character varying(255) DEFAULT NULL::character varying,
    columnid character varying(255) DEFAULT NULL::character varying,
    label character varying(255) DEFAULT NULL::character varying,
    width character varying(255) DEFAULT NULL::character varying,
    capacitygridsheetid bigint
);


--
-- Name: capacitygridheaders_capacitygridheaderid_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridheaders_capacitygridheaderid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridheaders_capacitygridheaderid_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridheaders_capacitygridheaderid_seq OWNED BY pathwaysdos.capacitygridheaders.capacitygridheaderid;


--
-- Name: capacitygridparentsheets; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridparentsheets (
    id integer NOT NULL,
    capacitygridparentid bigint,
    capacitygridsheetid bigint
);


--
-- Name: capacitygridparentsheets_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridparentsheets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridparentsheets_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridparentsheets_id_seq OWNED BY pathwaysdos.capacitygridparentsheets.id;


--
-- Name: capacitygridservicetypes; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridservicetypes (
    id integer NOT NULL,
    servicetypeid integer,
    capacitygridsheetid bigint
);


--
-- Name: capacitygridservicetypes_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridservicetypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridservicetypes_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridservicetypes_id_seq OWNED BY pathwaysdos.capacitygridservicetypes.id;


--
-- Name: capacitygridsheethistories; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridsheethistories (
    id integer NOT NULL,
    capacitygridsheetid bigint,
    uid character varying(255) DEFAULT NULL::character varying,
    changevalue jsonb,
    username character varying(255) DEFAULT NULL::character varying,
    gridcelllastupdated timestamp(0) with time zone DEFAULT NULL::timestamp with time zone,
    gridsnapshot jsonb,
    serviceid integer
);


--
-- Name: capacitygridsheethistories_id_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridsheethistories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridsheethistories_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridsheethistories_id_seq OWNED BY pathwaysdos.capacitygridsheethistories.id;


--
-- Name: capacitygridsheets; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridsheets (
    capacitygridsheetid bigint NOT NULL,
    name character varying(255) DEFAULT NULL::character varying,
    config character varying(255) DEFAULT NULL::character varying,
    notes character varying(255) DEFAULT NULL::character varying
);


--
-- Name: capacitygridsheets_capacitygridsheetid_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridsheets_capacitygridsheetid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridsheets_capacitygridsheetid_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridsheets_capacitygridsheetid_seq OWNED BY pathwaysdos.capacitygridsheets.capacitygridsheetid;


--
-- Name: capacitygridtriggers; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.capacitygridtriggers (
    capacitygridtriggerid integer NOT NULL,
    cmsgridid character varying(255) DEFAULT NULL::character varying,
    uid character varying(255) DEFAULT NULL::character varying,
    trigger character varying(255) DEFAULT NULL::character varying,
    source character varying(255) DEFAULT NULL::character varying,
    capacitygridsheetid bigint
);


--
-- Name: capacitygridtriggers_capacitygridtriggerid_seq; Type: SEQUENCE; Schema: pathwaysdos; Owner: -
--

CREATE SEQUENCE pathwaysdos.capacitygridtriggers_capacitygridtriggerid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: capacitygridtriggers_capacitygridtriggerid_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.capacitygridtriggers_capacitygridtriggerid_seq OWNED BY pathwaysdos.capacitygridtriggers.capacitygridtriggerid;


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
-- Name: servicecapacitygrids; Type: TABLE; Schema: pathwaysdos; Owner: -
--

CREATE TABLE pathwaysdos.servicecapacitygrids (
    id integer NOT NULL,
    capacitygridsheetid bigint,
    servicecapacityid integer
);


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
-- Name: servicecapacitygrids_id_seq; Type: SEQUENCE OWNED BY; Schema: pathwaysdos; Owner: -
--

ALTER SEQUENCE pathwaysdos.servicecapacitygrids_id_seq OWNED BY pathwaysdos.servicecapacitygrids.id;


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
-- Name: capacitygridconditionalstyles id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridconditionalstyles ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.capacitygridconditionalstyles_id_seq'::regclass);


--
-- Name: capacitygridcustomformulas capacitygridcustomformulaid; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridcustomformulas ALTER COLUMN capacitygridcustomformulaid SET DEFAULT nextval('pathwaysdos.capacitygridcustomformulas_capacitygridcustomformulaid_seq'::regclass);


--
-- Name: capacitygridcustomformulastyles id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridcustomformulastyles ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.capacitygridcustomformulastyles_id_seq'::regclass);


--
-- Name: capacitygriddata capacitygriddataid; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygriddata ALTER COLUMN capacitygriddataid SET DEFAULT nextval('pathwaysdos.capacitygriddata_capacitygriddataid_seq'::regclass);


--
-- Name: capacitygridheaders capacitygridheaderid; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridheaders ALTER COLUMN capacitygridheaderid SET DEFAULT nextval('pathwaysdos.capacitygridheaders_capacitygridheaderid_seq'::regclass);


--
-- Name: capacitygridparentsheets id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridparentsheets ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.capacitygridparentsheets_id_seq'::regclass);


--
-- Name: capacitygridservicetypes id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridservicetypes ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.capacitygridservicetypes_id_seq'::regclass);


--
-- Name: capacitygridsheethistories id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridsheethistories ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.capacitygridsheethistories_id_seq'::regclass);


--
-- Name: capacitygridsheets capacitygridsheetid; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridsheets ALTER COLUMN capacitygridsheetid SET DEFAULT nextval('pathwaysdos.capacitygridsheets_capacitygridsheetid_seq'::regclass);


--
-- Name: capacitygridtriggers capacitygridtriggerid; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridtriggers ALTER COLUMN capacitygridtriggerid SET DEFAULT nextval('pathwaysdos.capacitygridtriggers_capacitygridtriggerid_seq'::regclass);


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
-- Name: servicecapacitygrids id; Type: DEFAULT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacitygrids ALTER COLUMN id SET DEFAULT nextval('pathwaysdos.servicecapacitygrids_id_seq'::regclass);


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
-- Name: agegroups agegroups_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.agegroups
    ADD CONSTRAINT agegroups_pkey PRIMARY KEY (id);


--
-- Name: scenariobundles bundlename_unique; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenariobundles
    ADD CONSTRAINT bundlename_unique UNIQUE (name);


--
-- Name: capacitygridconditionalstyles capacitygridconditionalstyles_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridconditionalstyles
    ADD CONSTRAINT capacitygridconditionalstyles_pkey PRIMARY KEY (id);


--
-- Name: capacitygridcustomformulas capacitygridcustomformulas_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridcustomformulas
    ADD CONSTRAINT capacitygridcustomformulas_pkey PRIMARY KEY (capacitygridcustomformulaid);


--
-- Name: capacitygridcustomformulastyles capacitygridcustomformulastyles_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridcustomformulastyles
    ADD CONSTRAINT capacitygridcustomformulastyles_pkey PRIMARY KEY (id);


--
-- Name: capacitygriddata capacitygriddata_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygriddata
    ADD CONSTRAINT capacitygriddata_pkey PRIMARY KEY (capacitygriddataid);


--
-- Name: capacitygridheaders capacitygridheaders_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridheaders
    ADD CONSTRAINT capacitygridheaders_pkey PRIMARY KEY (capacitygridheaderid);


--
-- Name: capacitygridparentsheets capacitygridparentsheets_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridparentsheets
    ADD CONSTRAINT capacitygridparentsheets_pkey PRIMARY KEY (id);


--
-- Name: capacitygridservicetypes capacitygridservicetypes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridservicetypes
    ADD CONSTRAINT capacitygridservicetypes_pkey PRIMARY KEY (id);


--
-- Name: capacitygridsheethistories capacitygridsheethistories_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridsheethistories
    ADD CONSTRAINT capacitygridsheethistories_pkey PRIMARY KEY (id);


--
-- Name: capacitygridsheets capacitygridsheets_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridsheets
    ADD CONSTRAINT capacitygridsheets_pkey PRIMARY KEY (capacitygridsheetid);


--
-- Name: capacitygridtriggers capacitygridtriggers_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridtriggers
    ADD CONSTRAINT capacitygridtriggers_pkey PRIMARY KEY (capacitygridtriggerid);


--
-- Name: capacitystatuses capacitystatuses_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitystatuses
    ADD CONSTRAINT capacitystatuses_pkey PRIMARY KEY (capacitystatusid);


--
-- Name: changes changes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.changes
    ADD CONSTRAINT changes_pkey PRIMARY KEY (id);


--
-- Name: dispositiongroupdispositions dispositiongroupdispositions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupdispositions
    ADD CONSTRAINT dispositiongroupdispositions_pkey PRIMARY KEY (id);


--
-- Name: dispositiongroups dispositiongroups_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroups
    ADD CONSTRAINT dispositiongroups_pkey PRIMARY KEY (id);


--
-- Name: dispositiongroupservicetypes dispositiongroupservicetypes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupservicetypes
    ADD CONSTRAINT dispositiongroupservicetypes_pkey PRIMARY KEY (id);


--
-- Name: dispositions dispositions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositions
    ADD CONSTRAINT dispositions_pkey PRIMARY KEY (id);


--
-- Name: dispositionservicetypes dispositionservicetypes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositionservicetypes
    ADD CONSTRAINT dispositionservicetypes_pkey PRIMARY KEY (id);


--
-- Name: genders genders_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.genders
    ADD CONSTRAINT genders_pkey PRIMARY KEY (id);


--
-- Name: groupserviceimports groupserviceimports_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.groupserviceimports
    ADD CONSTRAINT groupserviceimports_pkey PRIMARY KEY (id);


--
-- Name: jobqueue jobqueue_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.jobqueue
    ADD CONSTRAINT jobqueue_pkey PRIMARY KEY (id);


--
-- Name: ldaimports ldaimports_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.ldaimports
    ADD CONSTRAINT ldaimports_pkey PRIMARY KEY (id);


--
-- Name: legacycollisions legacycollisions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.legacycollisions
    ADD CONSTRAINT legacycollisions_pkey PRIMARY KEY (id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: news news_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.news
    ADD CONSTRAINT news_pkey PRIMARY KEY (id);


--
-- Name: newsacknowledgedbyusers newsacknowledgedbyusers_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsacknowledgedbyusers
    ADD CONSTRAINT newsacknowledgedbyusers_pkey PRIMARY KEY (id);


--
-- Name: newsforpermissions newsforpermissions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsforpermissions
    ADD CONSTRAINT newsforpermissions_pkey PRIMARY KEY (id);


--
-- Name: odsimports odsimports_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.odsimports
    ADD CONSTRAINT odsimports_pkey PRIMARY KEY (id);


--
-- Name: odspostcodes odspostcodes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.odspostcodes
    ADD CONSTRAINT odspostcodes_pkey PRIMARY KEY (id);


--
-- Name: organisationpostcodes op_loc_org_unique; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationpostcodes
    ADD CONSTRAINT op_loc_org_unique UNIQUE (locationid, organisationid);


--
-- Name: openingtimedays openingtimedays_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.openingtimedays
    ADD CONSTRAINT openingtimedays_pkey PRIMARY KEY (id);


--
-- Name: organisations org_code_unique; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisations
    ADD CONSTRAINT org_code_unique UNIQUE (code);


--
-- Name: organisationpostcodes organisationpostcode_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationpostcodes
    ADD CONSTRAINT organisationpostcode_pkey PRIMARY KEY (id);


--
-- Name: organisationrankingstrategies organisationrankingstrategies_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationrankingstrategies
    ADD CONSTRAINT organisationrankingstrategies_pkey PRIMARY KEY (id);


--
-- Name: organisations organisations_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisations
    ADD CONSTRAINT organisations_pkey PRIMARY KEY (id);


--
-- Name: organisationtypes organisationtypes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationtypes
    ADD CONSTRAINT organisationtypes_pkey PRIMARY KEY (id);


--
-- Name: organisationrankingstrategies ors_st_org_unique; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationrankingstrategies
    ADD CONSTRAINT ors_st_org_unique UNIQUE (organisationid, servicetypeid);


--
-- Name: permissionattributedict permissionattributedict_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissionattributedict
    ADD CONSTRAINT permissionattributedict_pkey PRIMARY KEY (id);


--
-- Name: permissionattributes permissionattributes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissionattributes
    ADD CONSTRAINT permissionattributes_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: publicholidays publicholidays_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.publicholidays
    ADD CONSTRAINT publicholidays_pkey PRIMARY KEY (id);


--
-- Name: publicholidays publicholidays_uk1; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.publicholidays
    ADD CONSTRAINT publicholidays_uk1 UNIQUE (holidaydate);


--
-- Name: purgedusers purgedusers_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.purgedusers
    ADD CONSTRAINT purgedusers_pkey PRIMARY KEY (id);


--
-- Name: referralroles referralroles_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.referralroles
    ADD CONSTRAINT referralroles_pkey PRIMARY KEY (id);


--
-- Name: savedsearches savedsearches_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.savedsearches
    ADD CONSTRAINT savedsearches_pkey PRIMARY KEY (id);


--
-- Name: scenariobundles scenariobundles_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenariobundles
    ADD CONSTRAINT scenariobundles_pkey PRIMARY KEY (id);


--
-- Name: scenarios scenarios_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenarios
    ADD CONSTRAINT scenarios_pkey PRIMARY KEY (id);


--
-- Name: searchdistances searchdistances_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.searchdistances
    ADD CONSTRAINT searchdistances_pkey PRIMARY KEY (id);


--
-- Name: searchdistances searchdistances_uk1; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.searchdistances
    ADD CONSTRAINT searchdistances_uk1 UNIQUE (code);


--
-- Name: searchimports searchimports_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.searchimports
    ADD CONSTRAINT searchimports_pkey PRIMARY KEY (id);


--
-- Name: serviceagegroups serviceagegroups_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceagegroups
    ADD CONSTRAINT serviceagegroups_pkey PRIMARY KEY (id);


--
-- Name: serviceagerange serviceagerange_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceagerange
    ADD CONSTRAINT serviceagerange_pkey PRIMARY KEY (id);


--
-- Name: servicealignments servicealignments_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicealignments
    ADD CONSTRAINT servicealignments_pkey PRIMARY KEY (id);


--
-- Name: servicealignments servicealignments_uk1; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicealignments
    ADD CONSTRAINT servicealignments_uk1 UNIQUE (serviceid, commissioningorganisationid);


--
-- Name: serviceattributes serviceattributes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributes
    ADD CONSTRAINT serviceattributes_pkey PRIMARY KEY (id);


--
-- Name: serviceattributes serviceattributes_uk1; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributes
    ADD CONSTRAINT serviceattributes_uk1 UNIQUE (name, serviceattributetypeid);


--
-- Name: serviceattributetypes serviceattributetypes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributetypes
    ADD CONSTRAINT serviceattributetypes_pkey PRIMARY KEY (id);


--
-- Name: serviceattributevalues serviceattributevalues_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributevalues
    ADD CONSTRAINT serviceattributevalues_pkey PRIMARY KEY (id);


--
-- Name: servicecapacities servicecapacities_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacities
    ADD CONSTRAINT servicecapacities_pkey PRIMARY KEY (id);


--
-- Name: servicecapacities servicecapacities_uk1; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacities
    ADD CONSTRAINT servicecapacities_uk1 UNIQUE (serviceid);


--
-- Name: servicecapacitygrids servicecapacitygrids_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacitygrids
    ADD CONSTRAINT servicecapacitygrids_pkey PRIMARY KEY (id);


--
-- Name: servicedayopenings servicedayopenings_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedayopenings
    ADD CONSTRAINT servicedayopenings_pkey PRIMARY KEY (id);


--
-- Name: servicedayopeningtimes servicedayopeningtimes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedayopeningtimes
    ADD CONSTRAINT servicedayopeningtimes_pkey PRIMARY KEY (id);


--
-- Name: servicedispositions servicedispositions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedispositions
    ADD CONSTRAINT servicedispositions_pkey PRIMARY KEY (id);


--
-- Name: serviceendpoints serviceendpoints_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceendpoints
    ADD CONSTRAINT serviceendpoints_pkey PRIMARY KEY (id);


--
-- Name: servicegenders servicegenders_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicegenders
    ADD CONSTRAINT servicegenders_pkey PRIMARY KEY (id);


--
-- Name: servicehistories servicehistories_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicehistories
    ADD CONSTRAINT servicehistories_pkey PRIMARY KEY (serviceid);


--
-- Name: servicenotes servicenotes_pk; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicenotes
    ADD CONSTRAINT servicenotes_pk PRIMARY KEY (id);


--
-- Name: servicephonenumbers servicephonenumbers_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicephonenumbers
    ADD CONSTRAINT servicephonenumbers_pkey PRIMARY KEY (id);


--
-- Name: servicerankingstrategies servicerankingstrategies_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicerankingstrategies
    ADD CONSTRAINT servicerankingstrategies_pkey PRIMARY KEY (id);


--
-- Name: servicereferralroles servicereferralroles_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferralroles
    ADD CONSTRAINT servicereferralroles_pkey PRIMARY KEY (id);


--
-- Name: servicereferrals servicereferrals_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferrals
    ADD CONSTRAINT servicereferrals_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: serviceserviceattributes serviceserviceattributes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceserviceattributes
    ADD CONSTRAINT serviceserviceattributes_pkey PRIMARY KEY (id);


--
-- Name: servicesgsds servicesgsds_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicesgsds
    ADD CONSTRAINT servicesgsds_pkey PRIMARY KEY (id);


--
-- Name: servicespecifiedopeningdates servicespecifiedopeningdates_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicespecifiedopeningdates
    ADD CONSTRAINT servicespecifiedopeningdates_pkey PRIMARY KEY (id);


--
-- Name: servicespecifiedopeningtimes servicespecifiedopeningtimes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicespecifiedopeningtimes
    ADD CONSTRAINT servicespecifiedopeningtimes_pkey PRIMARY KEY (id);


--
-- Name: servicestatuses servicestatuses_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicestatuses
    ADD CONSTRAINT servicestatuses_pkey PRIMARY KEY (id);


--
-- Name: servicetypes servicetypes_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicetypes
    ADD CONSTRAINT servicetypes_pkey PRIMARY KEY (id);


--
-- Name: symptomdiscriminators symptomdiscriminators_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomdiscriminators
    ADD CONSTRAINT symptomdiscriminators_pkey PRIMARY KEY (id);


--
-- Name: symptomdiscriminatorsynonyms symptomdiscriminatorsynonyms_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomdiscriminatorsynonyms
    ADD CONSTRAINT symptomdiscriminatorsynonyms_pkey PRIMARY KEY (id);


--
-- Name: symptomgroups symptomgroups_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomgroups
    ADD CONSTRAINT symptomgroups_pkey PRIMARY KEY (id);


--
-- Name: symptomgroupsymptomdiscriminators symptomgroupsymptomdiscriminators_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomgroupsymptomdiscriminators
    ADD CONSTRAINT symptomgroupsymptomdiscriminators_pkey PRIMARY KEY (id);


--
-- Name: userpermissions userpermissions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userpermissions
    ADD CONSTRAINT userpermissions_pkey PRIMARY KEY (id);


--
-- Name: userreferralroles userreferralroles_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userreferralroles
    ADD CONSTRAINT userreferralroles_pkey PRIMARY KEY (id);


--
-- Name: userregions userregions_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userregions
    ADD CONSTRAINT userregions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_uk1; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.users
    ADD CONSTRAINT users_uk1 UNIQUE (careidentityid);


--
-- Name: usersavedsearches usersavedsearches_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.usersavedsearches
    ADD CONSTRAINT usersavedsearches_pkey PRIMARY KEY (id);


--
-- Name: userservices userservices_pkey; Type: CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userservices
    ADD CONSTRAINT userservices_pkey PRIMARY KEY (id);


--
-- Name: idx_13a6b93b5e237e06; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_13a6b93b5e237e06 ON pathwaysdos.servicetypes USING btree (name);


--
-- Name: idx_15fd08b85d98f5af; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_15fd08b85d98f5af ON pathwaysdos.servicereferralroles USING btree (referralroleid);


--
-- Name: idx_15fd08b889697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_15fd08b889697fa8 ON pathwaysdos.servicereferralroles USING btree (serviceid);


--
-- Name: idx_206d130164b64dcc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_206d130164b64dcc ON pathwaysdos.usersavedsearches USING btree (userid);


--
-- Name: idx_206d1301ddc59acc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_206d1301ddc59acc ON pathwaysdos.usersavedsearches USING btree (savedsearchid);


--
-- Name: idx_3150feb789697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_3150feb789697fa8 ON pathwaysdos.serviceagerange USING btree (serviceid);


--
-- Name: idx_32508c7f7c74e29f; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_32508c7f7c74e29f ON pathwaysdos.servicesgsds USING btree (sdid);


--
-- Name: idx_32508c7f7e325cc6; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_32508c7f7e325cc6 ON pathwaysdos.servicesgsds USING btree (sgid);


--
-- Name: idx_32508c7f89697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_32508c7f89697fa8 ON pathwaysdos.servicesgsds USING btree (serviceid);


--
-- Name: idx_3a1dd30f19d52895; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_3a1dd30f19d52895 ON pathwaysdos.newsacknowledgedbyusers USING btree (newsid);


--
-- Name: idx_42566457194eb424; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_42566457194eb424 ON pathwaysdos.servicedayopenings USING btree (dayid);


--
-- Name: idx_4256645789697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_4256645789697fa8 ON pathwaysdos.servicedayopenings USING btree (serviceid);


--
-- Name: idx_427a70a661325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_427a70a661325b4d ON pathwaysdos.capacitygridparentsheets USING btree (capacitygridsheetid);


--
-- Name: idx_427a70a6a628ae7e; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_427a70a6a628ae7e ON pathwaysdos.capacitygridparentsheets USING btree (capacitygridparentid);


--
-- Name: idx_46360b4c89697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_46360b4c89697fa8 ON pathwaysdos.servicegenders USING btree (serviceid);


--
-- Name: idx_49630122bacd168f; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_49630122bacd168f ON pathwaysdos.symptomgroupsymptomdiscriminators USING btree (symptomgroupid);


--
-- Name: idx_49630122d648d605; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_49630122d648d605 ON pathwaysdos.symptomgroupsymptomdiscriminators USING btree (symptomdiscriminatorid);


--
-- Name: idx_576ec73b149eca10; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_576ec73b149eca10 ON pathwaysdos.dispositiongroupdispositions USING btree (dispositionid);


--
-- Name: idx_576ec73b9bb73fe6; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_576ec73b9bb73fe6 ON pathwaysdos.dispositiongroupdispositions USING btree (dispositiongroupid);


--
-- Name: idx_59052f1554022ebc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_59052f1554022ebc ON pathwaysdos.servicereferrals USING btree (referredserviceid);


--
-- Name: idx_59052f15f70c1dca; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_59052f15f70c1dca ON pathwaysdos.servicereferrals USING btree (referralserviceid);


--
-- Name: idx_59e3a636539b0606; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_59e3a636539b0606 ON pathwaysdos.capacitygridcustomformulas USING btree (uid);


--
-- Name: idx_59e3a63685963223; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_59e3a63685963223 ON pathwaysdos.capacitygridcustomformulas USING btree (capacitygriddataid);


--
-- Name: idx_5dc51fa261325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5dc51fa261325b4d ON pathwaysdos.capacitygridservicetypes USING btree (capacitygridsheetid);


--
-- Name: idx_5dc51fa2bf1290dd; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5dc51fa2bf1290dd ON pathwaysdos.capacitygridservicetypes USING btree (servicetypeid);


--
-- Name: idx_5dc998c15e237e06; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5dc998c15e237e06 ON pathwaysdos.symptomdiscriminatorsynonyms USING btree (name);


--
-- Name: idx_5dc998c1d648d605; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5dc998c1d648d605 ON pathwaysdos.symptomdiscriminatorsynonyms USING btree (symptomdiscriminatorid);


--
-- Name: idx_5ea9331b28cf5be6; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5ea9331b28cf5be6 ON pathwaysdos.purgedusers USING btree (lastlogintime);


--
-- Name: idx_5ea9331b7b00651c; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5ea9331b7b00651c ON pathwaysdos.purgedusers USING btree (status);


--
-- Name: idx_5ea9331b870c850a; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5ea9331b870c850a ON pathwaysdos.purgedusers USING btree (approveddate);


--
-- Name: idx_5ea9331b91161a882392a156; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5ea9331b91161a882392a156 ON pathwaysdos.purgedusers USING btree (lastname, firstname);


--
-- Name: idx_5ea9331b98f62385; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5ea9331b98f62385 ON pathwaysdos.purgedusers USING btree (createdtime);


--
-- Name: idx_5ea9331bdd2bbc4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5ea9331bdd2bbc4d ON pathwaysdos.purgedusers USING btree (approvedby);


--
-- Name: idx_5ea9331be7927c74; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_5ea9331be7927c74 ON pathwaysdos.purgedusers USING btree (email);


--
-- Name: idx_67076541149eca10; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_67076541149eca10 ON pathwaysdos.dispositionservicetypes USING btree (dispositionid);


--
-- Name: idx_67076541bf1290dd; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_67076541bf1290dd ON pathwaysdos.dispositionservicetypes USING btree (servicetypeid);


--
-- Name: idx_6fd396b6939c32ff; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_6fd396b6939c32ff ON pathwaysdos.legacycollisions USING btree (legacyid);


--
-- Name: idx_6fd396b6f59fa73c; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_6fd396b6f59fa73c ON pathwaysdos.legacycollisions USING btree (serviceagerangeid);


--
-- Name: idx_714894ae539b0606; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_714894ae539b0606 ON pathwaysdos.capacitygridheaders USING btree (uid);


--
-- Name: idx_714894ae61325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_714894ae61325b4d ON pathwaysdos.capacitygridheaders USING btree (capacitygridsheetid);


--
-- Name: idx_7727330664b64dcc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_7727330664b64dcc ON pathwaysdos.userregions USING btree (userid);


--
-- Name: idx_772733069962506a; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_772733069962506a ON pathwaysdos.userregions USING btree (regionid);


--
-- Name: idx_7ec263ae5d98f5af; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_7ec263ae5d98f5af ON pathwaysdos.userreferralroles USING btree (referralroleid);


--
-- Name: idx_7ec263ae64b64dcc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_7ec263ae64b64dcc ON pathwaysdos.userreferralroles USING btree (userid);


--
-- Name: idx_84cebb71539b0606; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_84cebb71539b0606 ON pathwaysdos.capacitygridsheethistories USING btree (uid);


--
-- Name: idx_84cebb7189697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_84cebb7189697fa8 ON pathwaysdos.capacitygridsheethistories USING btree (serviceid);


--
-- Name: idx_8a44833f10ee4cee; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f10ee4cee ON pathwaysdos.services USING btree (parentid);


--
-- Name: idx_8a44833f3be6749b; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f3be6749b ON pathwaysdos.services USING btree (odscode);


--
-- Name: idx_8a44833f539b0606; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f539b0606 ON pathwaysdos.services USING btree (uid);


--
-- Name: idx_8a44833f5e237e06; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f5e237e06 ON pathwaysdos.services USING btree (name);


--
-- Name: idx_8a44833f62c39f2f; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f62c39f2f ON pathwaysdos.services USING btree (organisationid);


--
-- Name: idx_8a44833f6b848fb5; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f6b848fb5 ON pathwaysdos.services USING btree (subregionid);


--
-- Name: idx_8a44833f98f62385; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f98f62385 ON pathwaysdos.services USING btree (createdtime);


--
-- Name: idx_8a44833f9bf49490; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833f9bf49490 ON pathwaysdos.services USING btree (typeid);


--
-- Name: idx_8a44833fa2156f24; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833fa2156f24 ON pathwaysdos.services USING btree (lasttemplateid);


--
-- Name: idx_8a44833fb2cb8f6a63926b8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833fb2cb8f6a63926b8 ON pathwaysdos.services USING btree (easting, northing);


--
-- Name: idx_8a44833ff112f078; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833ff112f078 ON pathwaysdos.services USING btree (statusid);


--
-- Name: idx_8a44833ff40b5d8b; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_8a44833ff40b5d8b ON pathwaysdos.services USING btree (modifiedtime);


--
-- Name: idx_9e65c2333e0136f0; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_9e65c2333e0136f0 ON pathwaysdos.serviceendpoints USING btree (endpointorder);


--
-- Name: idx_9e65c23389697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_9e65c23389697fa8 ON pathwaysdos.serviceendpoints USING btree (serviceid);


--
-- Name: idx_a03561c643d7929a; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a03561c643d7929a ON pathwaysdos.servicerankingstrategies USING btree (servicetype);


--
-- Name: idx_a03561c689697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a03561c689697fa8 ON pathwaysdos.servicerankingstrategies USING btree (serviceid);


--
-- Name: idx_a03561c6b144c54a; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a03561c6b144c54a ON pathwaysdos.servicerankingstrategies USING btree (localranking);


--
-- Name: idx_a0953149bb73fe6; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a0953149bb73fe6 ON pathwaysdos.dispositiongroupservicetypes USING btree (dispositiongroupid);


--
-- Name: idx_a095314bf1290dd; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a095314bf1290dd ON pathwaysdos.dispositiongroupservicetypes USING btree (servicetypeid);


--
-- Name: idx_a2f43bd6539b0606; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a2f43bd6539b0606 ON pathwaysdos.capacitygridtriggers USING btree (uid);


--
-- Name: idx_a2f43bd661325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a2f43bd661325b4d ON pathwaysdos.capacitygridtriggers USING btree (capacitygridsheetid);


--
-- Name: idx_a2f43bd6e652d510; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_a2f43bd6e652d510 ON pathwaysdos.capacitygridtriggers USING btree (cmsgridid);


--
-- Name: idx_aaca31cf89697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_aaca31cf89697fa8 ON pathwaysdos.serviceagegroups USING btree (serviceid);


--
-- Name: idx_aaca31cfc2f62bd8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_aaca31cfc2f62bd8 ON pathwaysdos.serviceagegroups USING btree (agegroupid);


--
-- Name: idx_ab7143b88cde5729; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ab7143b88cde5729 ON pathwaysdos.permissions USING btree (type);


--
-- Name: idx_b5142da605405b0; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_b5142da605405b0 ON pathwaysdos.permissionattributes USING btree (permissionid);


--
-- Name: idx_b5142da968c3886; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_b5142da968c3886 ON pathwaysdos.permissionattributes USING btree (permissionattributedictid);


--
-- Name: idx_be30a7b064b64dcc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_be30a7b064b64dcc ON pathwaysdos.userservices USING btree (userid);


--
-- Name: idx_be30a7b089697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_be30a7b089697fa8 ON pathwaysdos.userservices USING btree (serviceid);


--
-- Name: idx_bundle_scenario; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX idx_bundle_scenario ON pathwaysdos.scenarios USING btree (scenariobundleid, scenarioid);


--
-- Name: idx_c0db61886de44026; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_c0db61886de44026 ON pathwaysdos.symptomdiscriminators USING btree (description);


--
-- Name: idx_c9566749539b0606; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_c9566749539b0606 ON pathwaysdos.capacitygriddata USING btree (uid);


--
-- Name: idx_c956674961325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_c956674961325b4d ON pathwaysdos.capacitygriddata USING btree (capacitygridsheetid);


--
-- Name: idx_capacitygridsheethistories_capacitygridsheetid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_capacitygridsheethistories_capacitygridsheetid ON pathwaysdos.capacitygridsheethistories USING btree (capacitygridsheetid);


--
-- Name: idx_cd1c55096d95540f; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_cd1c55096d95540f ON pathwaysdos.capacitygridcustomformulastyles USING btree (formulaid);


--
-- Name: idx_cd1c55097015c8dc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_cd1c55097015c8dc ON pathwaysdos.capacitygridcustomformulastyles USING btree (styleid);


--
-- Name: idx_commissioning_organisation; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_commissioning_organisation ON pathwaysdos.servicealignments USING btree (commissioningorganisationid);


--
-- Name: idx_d5428aed28cf5be6; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d5428aed28cf5be6 ON pathwaysdos.users USING btree (lastlogintime);


--
-- Name: idx_d5428aed7b00651c; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d5428aed7b00651c ON pathwaysdos.users USING btree (status);


--
-- Name: idx_d5428aed870c850a; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d5428aed870c850a ON pathwaysdos.users USING btree (approveddate);


--
-- Name: idx_d5428aed91161a882392a156; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d5428aed91161a882392a156 ON pathwaysdos.users USING btree (lastname, firstname);


--
-- Name: idx_d5428aed98f62385; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d5428aed98f62385 ON pathwaysdos.users USING btree (createdtime);


--
-- Name: idx_d5428aeddd2bbc4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d5428aeddd2bbc4d ON pathwaysdos.users USING btree (approvedby);


--
-- Name: idx_d5428aede7927c74; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d5428aede7927c74 ON pathwaysdos.users USING btree (email);


--
-- Name: idx_d9f6dd7e61325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d9f6dd7e61325b4d ON pathwaysdos.servicecapacitygrids USING btree (capacitygridsheetid);


--
-- Name: idx_d9f6dd7e87d85175; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_d9f6dd7e87d85175 ON pathwaysdos.servicecapacitygrids USING btree (servicecapacityid);


--
-- Name: idx_e7984bb2605405b0; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_e7984bb2605405b0 ON pathwaysdos.userpermissions USING btree (permissionid);


--
-- Name: idx_e7984bb264b64dcc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_e7984bb264b64dcc ON pathwaysdos.userpermissions USING btree (userid);


--
-- Name: idx_ee31b38c19d52895; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ee31b38c19d52895 ON pathwaysdos.newsforpermissions USING btree (newsid);


--
-- Name: idx_ef9d81a11ced5b0a9c0b752; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ef9d81a11ced5b0a9c0b752 ON pathwaysdos.changes USING btree (serviceid, approvestatus);


--
-- Name: idx_ef9d81a189697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ef9d81a189697fa8 ON pathwaysdos.changes USING btree (serviceid);


--
-- Name: idx_ef9d81a1961eaf4a; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ef9d81a1961eaf4a ON pathwaysdos.changes USING btree (createdtimestamp);


--
-- Name: idx_fa62cf52149eca10; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_fa62cf52149eca10 ON pathwaysdos.servicedispositions USING btree (dispositionid);


--
-- Name: idx_fa62cf5289697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_fa62cf5289697fa8 ON pathwaysdos.servicedispositions USING btree (serviceid);


--
-- Name: idx_fbf2e963101f2b4; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_fbf2e963101f2b4 ON pathwaysdos.servicecapacities USING btree (modifieddate);


--
-- Name: idx_fbf2e96844c57db; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_fbf2e96844c57db ON pathwaysdos.servicecapacities USING btree (capacitystatusid);


--
-- Name: idx_fbf2e96ecf9771d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_fbf2e96ecf9771d ON pathwaysdos.servicecapacities USING btree (modifiedby);


--
-- Name: idx_groupserviceimports_uid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_groupserviceimports_uid ON pathwaysdos.groupserviceimports USING btree (uid);


--
-- Name: idx_ldaimports_orgcode; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ldaimports_orgcode ON pathwaysdos.ldaimports USING btree (orgcode);


--
-- Name: idx_ldaimports_postcode; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ldaimports_postcode ON pathwaysdos.ldaimports USING btree (postcode);


--
-- Name: idx_locations_postaltown; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_locations_postaltown ON pathwaysdos.locations USING btree (postaltown);


--
-- Name: idx_locations_postcode; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_locations_postcode ON pathwaysdos.locations USING btree (postcode);


--
-- Name: idx_newsacknowledgedbyusers_userid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_newsacknowledgedbyusers_userid ON pathwaysdos.newsacknowledgedbyusers USING btree (userid);


--
-- Name: idx_newsforpermissions_permissionid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_newsforpermissions_permissionid ON pathwaysdos.newsforpermissions USING btree (permissionid);


--
-- Name: idx_odsimports_ccg; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_odsimports_ccg ON pathwaysdos.odsimports USING btree (ccg);


--
-- Name: idx_odsimports_pcds; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_odsimports_pcds ON pathwaysdos.odsimports USING btree (pcds);


--
-- Name: idx_odspostcodes_orgcode; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_odspostcodes_orgcode ON pathwaysdos.odspostcodes USING btree (orgcode);


--
-- Name: idx_odspostcodes_postcode; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_odspostcodes_postcode ON pathwaysdos.odspostcodes USING btree (postcode);


--
-- Name: idx_organisation_organisationtypeid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_organisation_organisationtypeid ON pathwaysdos.organisations USING btree (organisationtypeid);


--
-- Name: idx_organisations_subregionid_fkey; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_organisations_subregionid_fkey ON pathwaysdos.organisations USING btree (subregionid);


--
-- Name: idx_ors_organisation; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_ors_organisation ON pathwaysdos.organisationrankingstrategies USING btree (organisationid);


--
-- Name: idx_searchimports_code; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_searchimports_code ON pathwaysdos.searchimports USING btree (code);


--
-- Name: idx_servicedayopeningtimes_servicedayopeningid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_servicedayopeningtimes_servicedayopeningid ON pathwaysdos.servicedayopeningtimes USING btree (servicedayopeningid);


--
-- Name: idx_servicegenders_genderid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_servicegenders_genderid ON pathwaysdos.servicegenders USING btree (genderid);


--
-- Name: idx_servicephonenumbers_serviceid_fkey; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_servicephonenumbers_serviceid_fkey ON pathwaysdos.servicephonenumbers USING btree (serviceid);


--
-- Name: idx_servicespecifiedopeningdates_serviceid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_servicespecifiedopeningdates_serviceid ON pathwaysdos.servicespecifiedopeningdates USING btree (serviceid);


--
-- Name: idx_servicespecifiedopeningtimes_servicespecifiedopeningdateid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_servicespecifiedopeningtimes_servicespecifiedopeningdateid ON pathwaysdos.servicespecifiedopeningtimes USING btree (servicespecifiedopeningdateid);


--
-- Name: idx_users_username_lower; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX idx_users_username_lower ON pathwaysdos.users USING btree (lower((username)::text));


--
-- Name: newsacknowledgedbyusers_newsid_userid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX newsacknowledgedbyusers_newsid_userid ON pathwaysdos.newsacknowledgedbyusers USING btree (newsid, userid);


--
-- Name: serviceattributes_idx1; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX serviceattributes_idx1 ON pathwaysdos.serviceattributes USING btree (serviceattributetypeid);


--
-- Name: serviceattributes_idx2; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX serviceattributes_idx2 ON pathwaysdos.serviceattributes USING btree (createduserid);


--
-- Name: serviceattributes_idx3; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX serviceattributes_idx3 ON pathwaysdos.serviceattributes USING btree (modifieduserid);


--
-- Name: serviceattributevalues_idx1; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX serviceattributevalues_idx1 ON pathwaysdos.serviceattributevalues USING btree (serviceattributeid);


--
-- Name: servicenotes_serviceid_index; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX servicenotes_serviceid_index ON pathwaysdos.servicenotes USING btree (serviceid);


--
-- Name: serviceserviceattributes_idx1; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX serviceserviceattributes_idx1 ON pathwaysdos.serviceserviceattributes USING btree (serviceattributeid);


--
-- Name: serviceserviceattributes_idx2; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX serviceserviceattributes_idx2 ON pathwaysdos.serviceserviceattributes USING btree (serviceattributevalueid);


--
-- Name: serviceserviceattributes_idx3; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE INDEX serviceserviceattributes_idx3 ON pathwaysdos.serviceserviceattributes USING btree (serviceid);


--
-- Name: un_newsforpermissions_newsid_permissionid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX un_newsforpermissions_newsid_permissionid ON pathwaysdos.newsforpermissions USING btree (newsid, permissionid);


--
-- Name: un_servicegenders_serviceid_genderid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX un_servicegenders_serviceid_genderid ON pathwaysdos.servicegenders USING btree (serviceid, genderid);


--
-- Name: un_servicehistories_serviceid; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX un_servicehistories_serviceid ON pathwaysdos.servicehistories USING btree (serviceid);


--
-- Name: uniq_15fd08b889697fa85d98f5af; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_15fd08b889697fa85d98f5af ON pathwaysdos.servicereferralroles USING btree (serviceid, referralroleid);


--
-- Name: uniq_206d130164b64dccddc59acc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_206d130164b64dccddc59acc ON pathwaysdos.usersavedsearches USING btree (userid, savedsearchid);


--
-- Name: uniq_32508c7f89697fa87c74e29f7e325cc6; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_32508c7f89697fa87c74e29f7e325cc6 ON pathwaysdos.servicesgsds USING btree (serviceid, sdid, sgid);


--
-- Name: uniq_427a70a6a628ae7e61325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_427a70a6a628ae7e61325b4d ON pathwaysdos.capacitygridparentsheets USING btree (capacitygridparentid, capacitygridsheetid);


--
-- Name: uniq_49630122bacd168fd648d605; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_49630122bacd168fd648d605 ON pathwaysdos.symptomgroupsymptomdiscriminators USING btree (symptomgroupid, symptomdiscriminatorid);


--
-- Name: uniq_576ec73b149eca109bb73fe6; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_576ec73b149eca109bb73fe6 ON pathwaysdos.dispositiongroupdispositions USING btree (dispositionid, dispositiongroupid);


--
-- Name: uniq_59052f15f70c1dca54022ebc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_59052f15f70c1dca54022ebc ON pathwaysdos.servicereferrals USING btree (referralserviceid, referredserviceid);


--
-- Name: uniq_5dc51fa261325b4dbf1290dd; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_5dc51fa261325b4dbf1290dd ON pathwaysdos.capacitygridservicetypes USING btree (capacitygridsheetid, servicetypeid);


--
-- Name: uniq_5ea9331bf85e0677; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_5ea9331bf85e0677 ON pathwaysdos.purgedusers USING btree (username);


--
-- Name: uniq_67076541149eca10bf1290dd; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_67076541149eca10bf1290dd ON pathwaysdos.dispositionservicetypes USING btree (dispositionid, servicetypeid);


--
-- Name: uniq_673868f15e237e06; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_673868f15e237e06 ON pathwaysdos.symptomgroups USING btree (name);


--
-- Name: uniq_7727330664b64dcc9962506a; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_7727330664b64dcc9962506a ON pathwaysdos.userregions USING btree (userid, regionid);


--
-- Name: uniq_7ec263ae64b64dcc5d98f5af; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_7ec263ae64b64dcc5d98f5af ON pathwaysdos.userreferralroles USING btree (userid, referralroleid);


--
-- Name: uniq_8af64fff5e237e06; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_8af64fff5e237e06 ON pathwaysdos.referralroles USING btree (name);


--
-- Name: uniq_923e98ec5e237e06; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_923e98ec5e237e06 ON pathwaysdos.permissionattributedict USING btree (name);


--
-- Name: uniq_a0953149bb73fe6bf1290dd; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_a0953149bb73fe6bf1290dd ON pathwaysdos.dispositiongroupservicetypes USING btree (dispositiongroupid, servicetypeid);


--
-- Name: uniq_aaca31cf89697fa8c2f62bd8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_aaca31cf89697fa8c2f62bd8 ON pathwaysdos.serviceagegroups USING btree (serviceid, agegroupid);


--
-- Name: uniq_ab7143b85e237e06; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_ab7143b85e237e06 ON pathwaysdos.permissions USING btree (name);


--
-- Name: uniq_b5142da605405b0968c3886; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_b5142da605405b0968c3886 ON pathwaysdos.permissionattributes USING btree (permissionid, permissionattributedictid);


--
-- Name: uniq_be30a7b064b64dcc89697fa8; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_be30a7b064b64dcc89697fa8 ON pathwaysdos.userservices USING btree (userid, serviceid);


--
-- Name: uniq_cd1c55096d95540f7015c8dc; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_cd1c55096d95540f7015c8dc ON pathwaysdos.capacitygridcustomformulastyles USING btree (formulaid, styleid);


--
-- Name: uniq_cd848f1e61325b4d; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_cd848f1e61325b4d ON pathwaysdos.capacitygridsheets USING btree (capacitygridsheetid);


--
-- Name: uniq_d5428aedf85e0677; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_d5428aedf85e0677 ON pathwaysdos.users USING btree (username);


--
-- Name: uniq_d9f6dd7e61325b4d87d85175; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_d9f6dd7e61325b4d87d85175 ON pathwaysdos.servicecapacitygrids USING btree (capacitygridsheetid, servicecapacityid);


--
-- Name: uniq_e7984bb264b64dcc605405b0; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_e7984bb264b64dcc605405b0 ON pathwaysdos.userpermissions USING btree (userid, permissionid);


--
-- Name: uniq_fa62cf5289697fa8149eca10; Type: INDEX; Schema: pathwaysdos; Owner: -
--

CREATE UNIQUE INDEX uniq_fa62cf5289697fa8149eca10 ON pathwaysdos.servicedispositions USING btree (serviceid, dispositionid);


--
-- Name: dispositiongroupdispositions afterrowdeletedispositiongroupdispositions; Type: TRIGGER; Schema: pathwaysdos; Owner: -
--

CREATE TRIGGER afterrowdeletedispositiongroupdispositions AFTER DELETE ON pathwaysdos.dispositiongroupdispositions FOR EACH ROW EXECUTE FUNCTION pathwaysdos.deletedispositiongroup();


--
-- Name: servicecapacitygrids afterrowdeleteservicecapacitygrids; Type: TRIGGER; Schema: pathwaysdos; Owner: -
--

CREATE TRIGGER afterrowdeleteservicecapacitygrids AFTER DELETE ON pathwaysdos.servicecapacitygrids FOR EACH ROW EXECUTE FUNCTION pathwaysdos.deletecapacitygrid();


--
-- Name: symptomgroupsymptomdiscriminators afterrowdeletesymptomgroupsymptomdiscriminators; Type: TRIGGER; Schema: pathwaysdos; Owner: -
--

CREATE TRIGGER afterrowdeletesymptomgroupsymptomdiscriminators AFTER DELETE ON pathwaysdos.symptomgroupsymptomdiscriminators FOR EACH ROW EXECUTE FUNCTION pathwaysdos.deletesymptomgroup();


--
-- Name: serviceattributes afterrowinsertserviceattributes; Type: TRIGGER; Schema: pathwaysdos; Owner: -
--

CREATE TRIGGER afterrowinsertserviceattributes AFTER INSERT ON pathwaysdos.serviceattributes FOR EACH ROW EXECUTE FUNCTION pathwaysdos.insertserviceattributevalues();


--
-- Name: services beforerowinsertservices; Type: TRIGGER; Schema: pathwaysdos; Owner: -
--

CREATE TRIGGER beforerowinsertservices BEFORE INSERT ON pathwaysdos.services FOR EACH ROW EXECUTE FUNCTION pathwaysdos.assignservicesuid();


--
-- Name: servicereferralroles fk_15fd08b85d98f5af; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferralroles
    ADD CONSTRAINT fk_15fd08b85d98f5af FOREIGN KEY (referralroleid) REFERENCES pathwaysdos.referralroles(id) ON DELETE CASCADE;


--
-- Name: servicereferralroles fk_15fd08b889697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferralroles
    ADD CONSTRAINT fk_15fd08b889697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: usersavedsearches fk_206d130164b64dcc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.usersavedsearches
    ADD CONSTRAINT fk_206d130164b64dcc FOREIGN KEY (userid) REFERENCES pathwaysdos.users(id) ON DELETE CASCADE;


--
-- Name: usersavedsearches fk_206d1301ddc59acc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.usersavedsearches
    ADD CONSTRAINT fk_206d1301ddc59acc FOREIGN KEY (savedsearchid) REFERENCES pathwaysdos.savedsearches(id) ON DELETE CASCADE;


--
-- Name: serviceagerange fk_3150feb789697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceagerange
    ADD CONSTRAINT fk_3150feb789697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: servicesgsds fk_32508c7f7c74e29f; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicesgsds
    ADD CONSTRAINT fk_32508c7f7c74e29f FOREIGN KEY (sdid) REFERENCES pathwaysdos.symptomdiscriminators(id) ON DELETE CASCADE;


--
-- Name: servicesgsds fk_32508c7f7e325cc6; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicesgsds
    ADD CONSTRAINT fk_32508c7f7e325cc6 FOREIGN KEY (sgid) REFERENCES pathwaysdos.symptomgroups(id) ON DELETE CASCADE;


--
-- Name: servicesgsds fk_32508c7f89697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicesgsds
    ADD CONSTRAINT fk_32508c7f89697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: newsacknowledgedbyusers fk_3a1dd30f19d52895; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsacknowledgedbyusers
    ADD CONSTRAINT fk_3a1dd30f19d52895 FOREIGN KEY (newsid) REFERENCES pathwaysdos.news(id);


--
-- Name: newsacknowledgedbyusers fk_3a1dd30f64b64dcc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsacknowledgedbyusers
    ADD CONSTRAINT fk_3a1dd30f64b64dcc FOREIGN KEY (userid) REFERENCES pathwaysdos.users(id) ON DELETE CASCADE;


--
-- Name: servicedayopenings fk_42566457194eb424; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedayopenings
    ADD CONSTRAINT fk_42566457194eb424 FOREIGN KEY (dayid) REFERENCES pathwaysdos.openingtimedays(id);


--
-- Name: servicedayopenings fk_4256645789697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedayopenings
    ADD CONSTRAINT fk_4256645789697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: capacitygridparentsheets fk_427a70a661325b4d; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridparentsheets
    ADD CONSTRAINT fk_427a70a661325b4d FOREIGN KEY (capacitygridsheetid) REFERENCES pathwaysdos.capacitygridsheets(capacitygridsheetid) ON DELETE CASCADE;


--
-- Name: capacitygridparentsheets fk_427a70a6a628ae7e; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridparentsheets
    ADD CONSTRAINT fk_427a70a6a628ae7e FOREIGN KEY (capacitygridparentid) REFERENCES pathwaysdos.capacitygridsheets(capacitygridsheetid) ON DELETE CASCADE;


--
-- Name: servicegenders fk_46360b4c827402c; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicegenders
    ADD CONSTRAINT fk_46360b4c827402c FOREIGN KEY (genderid) REFERENCES pathwaysdos.genders(id);


--
-- Name: servicegenders fk_46360b4c89697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicegenders
    ADD CONSTRAINT fk_46360b4c89697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: symptomgroupsymptomdiscriminators fk_49630122bacd168f; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomgroupsymptomdiscriminators
    ADD CONSTRAINT fk_49630122bacd168f FOREIGN KEY (symptomgroupid) REFERENCES pathwaysdos.symptomgroups(id);


--
-- Name: symptomgroupsymptomdiscriminators fk_49630122d648d605; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomgroupsymptomdiscriminators
    ADD CONSTRAINT fk_49630122d648d605 FOREIGN KEY (symptomdiscriminatorid) REFERENCES pathwaysdos.symptomdiscriminators(id) ON DELETE CASCADE;


--
-- Name: dispositiongroupdispositions fk_576ec73b149eca10; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupdispositions
    ADD CONSTRAINT fk_576ec73b149eca10 FOREIGN KEY (dispositionid) REFERENCES pathwaysdos.dispositions(id) ON DELETE CASCADE;


--
-- Name: dispositiongroupdispositions fk_576ec73b9bb73fe6; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupdispositions
    ADD CONSTRAINT fk_576ec73b9bb73fe6 FOREIGN KEY (dispositiongroupid) REFERENCES pathwaysdos.dispositiongroups(id);


--
-- Name: servicereferrals fk_59052f1554022ebc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferrals
    ADD CONSTRAINT fk_59052f1554022ebc FOREIGN KEY (referredserviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: servicereferrals fk_59052f15f70c1dca; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicereferrals
    ADD CONSTRAINT fk_59052f15f70c1dca FOREIGN KEY (referralserviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: capacitygridcustomformulas fk_59e3a63685963223; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridcustomformulas
    ADD CONSTRAINT fk_59e3a63685963223 FOREIGN KEY (capacitygriddataid) REFERENCES pathwaysdos.capacitygriddata(capacitygriddataid) ON DELETE CASCADE;


--
-- Name: capacitygridservicetypes fk_5dc51fa261325b4d; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridservicetypes
    ADD CONSTRAINT fk_5dc51fa261325b4d FOREIGN KEY (capacitygridsheetid) REFERENCES pathwaysdos.capacitygridsheets(capacitygridsheetid) ON DELETE CASCADE;


--
-- Name: capacitygridservicetypes fk_5dc51fa2bf1290dd; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridservicetypes
    ADD CONSTRAINT fk_5dc51fa2bf1290dd FOREIGN KEY (servicetypeid) REFERENCES pathwaysdos.servicetypes(id) ON DELETE CASCADE;


--
-- Name: symptomdiscriminatorsynonyms fk_5dc998c1d648d605; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.symptomdiscriminatorsynonyms
    ADD CONSTRAINT fk_5dc998c1d648d605 FOREIGN KEY (symptomdiscriminatorid) REFERENCES pathwaysdos.symptomdiscriminators(id) ON DELETE CASCADE;


--
-- Name: dispositionservicetypes fk_67076541149eca10; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositionservicetypes
    ADD CONSTRAINT fk_67076541149eca10 FOREIGN KEY (dispositionid) REFERENCES pathwaysdos.dispositions(id) ON DELETE CASCADE;


--
-- Name: dispositionservicetypes fk_67076541bf1290dd; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositionservicetypes
    ADD CONSTRAINT fk_67076541bf1290dd FOREIGN KEY (servicetypeid) REFERENCES pathwaysdos.servicetypes(id) ON DELETE CASCADE;


--
-- Name: legacycollisions fk_6fd396b6f59fa73c; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.legacycollisions
    ADD CONSTRAINT fk_6fd396b6f59fa73c FOREIGN KEY (serviceagerangeid) REFERENCES pathwaysdos.serviceagerange(id) ON DELETE CASCADE;


--
-- Name: capacitygridheaders fk_714894ae61325b4d; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridheaders
    ADD CONSTRAINT fk_714894ae61325b4d FOREIGN KEY (capacitygridsheetid) REFERENCES pathwaysdos.capacitygridsheets(capacitygridsheetid) ON DELETE CASCADE;


--
-- Name: servicespecifiedopeningtimes fk_75adf67a6f27795; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicespecifiedopeningtimes
    ADD CONSTRAINT fk_75adf67a6f27795 FOREIGN KEY (servicespecifiedopeningdateid) REFERENCES pathwaysdos.servicespecifiedopeningdates(id) ON DELETE CASCADE;


--
-- Name: userregions fk_7727330664b64dcc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userregions
    ADD CONSTRAINT fk_7727330664b64dcc FOREIGN KEY (userid) REFERENCES pathwaysdos.users(id) ON DELETE CASCADE;


--
-- Name: userregions fk_772733069962506a; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userregions
    ADD CONSTRAINT fk_772733069962506a FOREIGN KEY (regionid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: userreferralroles fk_7ec263ae5d98f5af; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userreferralroles
    ADD CONSTRAINT fk_7ec263ae5d98f5af FOREIGN KEY (referralroleid) REFERENCES pathwaysdos.referralroles(id) ON DELETE CASCADE;


--
-- Name: userreferralroles fk_7ec263ae64b64dcc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userreferralroles
    ADD CONSTRAINT fk_7ec263ae64b64dcc FOREIGN KEY (userid) REFERENCES pathwaysdos.users(id) ON DELETE CASCADE;


--
-- Name: capacitygridsheethistories fk_84cebb7189697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridsheethistories
    ADD CONSTRAINT fk_84cebb7189697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: services fk_8a44833f10ee4cee; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.services
    ADD CONSTRAINT fk_8a44833f10ee4cee FOREIGN KEY (parentid) REFERENCES pathwaysdos.services(id);


--
-- Name: services fk_8a44833f6b848fb5; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.services
    ADD CONSTRAINT fk_8a44833f6b848fb5 FOREIGN KEY (subregionid) REFERENCES pathwaysdos.services(id);


--
-- Name: services fk_8a44833f9bf49490; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.services
    ADD CONSTRAINT fk_8a44833f9bf49490 FOREIGN KEY (typeid) REFERENCES pathwaysdos.servicetypes(id);


--
-- Name: services fk_8a44833ff112f078; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.services
    ADD CONSTRAINT fk_8a44833ff112f078 FOREIGN KEY (statusid) REFERENCES pathwaysdos.servicestatuses(id);


--
-- Name: serviceendpoints fk_9e65c23389697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceendpoints
    ADD CONSTRAINT fk_9e65c23389697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: servicerankingstrategies fk_a03561c689697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicerankingstrategies
    ADD CONSTRAINT fk_a03561c689697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: dispositiongroupservicetypes fk_a0953149bb73fe6; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupservicetypes
    ADD CONSTRAINT fk_a0953149bb73fe6 FOREIGN KEY (dispositiongroupid) REFERENCES pathwaysdos.dispositiongroups(id) ON DELETE CASCADE;


--
-- Name: dispositiongroupservicetypes fk_a095314bf1290dd; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.dispositiongroupservicetypes
    ADD CONSTRAINT fk_a095314bf1290dd FOREIGN KEY (servicetypeid) REFERENCES pathwaysdos.servicetypes(id) ON DELETE CASCADE;


--
-- Name: capacitygridtriggers fk_a2f43bd661325b4d; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridtriggers
    ADD CONSTRAINT fk_a2f43bd661325b4d FOREIGN KEY (capacitygridsheetid) REFERENCES pathwaysdos.capacitygridsheets(capacitygridsheetid) ON DELETE CASCADE;


--
-- Name: serviceagegroups fk_aaca31cf89697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceagegroups
    ADD CONSTRAINT fk_aaca31cf89697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: serviceagegroups fk_aaca31cfc2f62bd8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceagegroups
    ADD CONSTRAINT fk_aaca31cfc2f62bd8 FOREIGN KEY (agegroupid) REFERENCES pathwaysdos.agegroups(id) ON DELETE CASCADE;


--
-- Name: servicespecifiedopeningdates fk_b1f9f8f589697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicespecifiedopeningdates
    ADD CONSTRAINT fk_b1f9f8f589697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: permissionattributes fk_b5142da605405b0; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissionattributes
    ADD CONSTRAINT fk_b5142da605405b0 FOREIGN KEY (permissionid) REFERENCES pathwaysdos.permissions(id);


--
-- Name: permissionattributes fk_b5142da968c3886; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.permissionattributes
    ADD CONSTRAINT fk_b5142da968c3886 FOREIGN KEY (permissionattributedictid) REFERENCES pathwaysdos.permissionattributedict(id);


--
-- Name: userservices fk_be30a7b064b64dcc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userservices
    ADD CONSTRAINT fk_be30a7b064b64dcc FOREIGN KEY (userid) REFERENCES pathwaysdos.users(id) ON DELETE CASCADE;


--
-- Name: userservices fk_be30a7b089697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userservices
    ADD CONSTRAINT fk_be30a7b089697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: capacitygriddata fk_c956674961325b4d; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygriddata
    ADD CONSTRAINT fk_c956674961325b4d FOREIGN KEY (capacitygridsheetid) REFERENCES pathwaysdos.capacitygridsheets(capacitygridsheetid) ON DELETE CASCADE;


--
-- Name: capacitygridcustomformulastyles fk_cd1c55096d95540f; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridcustomformulastyles
    ADD CONSTRAINT fk_cd1c55096d95540f FOREIGN KEY (formulaid) REFERENCES pathwaysdos.capacitygridcustomformulas(capacitygridcustomformulaid) ON DELETE CASCADE;


--
-- Name: capacitygridcustomformulastyles fk_cd1c55097015c8dc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.capacitygridcustomformulastyles
    ADD CONSTRAINT fk_cd1c55097015c8dc FOREIGN KEY (styleid) REFERENCES pathwaysdos.capacitygridconditionalstyles(id) ON DELETE CASCADE;


--
-- Name: servicecapacitygrids fk_d9f6dd7e61325b4d; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacitygrids
    ADD CONSTRAINT fk_d9f6dd7e61325b4d FOREIGN KEY (capacitygridsheetid) REFERENCES pathwaysdos.capacitygridsheets(capacitygridsheetid) ON DELETE CASCADE;


--
-- Name: servicecapacitygrids fk_d9f6dd7e87d85175; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacitygrids
    ADD CONSTRAINT fk_d9f6dd7e87d85175 FOREIGN KEY (servicecapacityid) REFERENCES pathwaysdos.servicecapacities(id) ON DELETE CASCADE;


--
-- Name: userpermissions fk_e7984bb2605405b0; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userpermissions
    ADD CONSTRAINT fk_e7984bb2605405b0 FOREIGN KEY (permissionid) REFERENCES pathwaysdos.permissions(id) ON DELETE CASCADE;


--
-- Name: userpermissions fk_e7984bb264b64dcc; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.userpermissions
    ADD CONSTRAINT fk_e7984bb264b64dcc FOREIGN KEY (userid) REFERENCES pathwaysdos.users(id) ON DELETE CASCADE;


--
-- Name: servicedayopeningtimes fk_e835fd1f6ebd7092; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedayopeningtimes
    ADD CONSTRAINT fk_e835fd1f6ebd7092 FOREIGN KEY (servicedayopeningid) REFERENCES pathwaysdos.servicedayopenings(id) ON DELETE CASCADE;


--
-- Name: newsforpermissions fk_ee31b38c19d52895; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsforpermissions
    ADD CONSTRAINT fk_ee31b38c19d52895 FOREIGN KEY (newsid) REFERENCES pathwaysdos.news(id);


--
-- Name: newsforpermissions fk_ee31b38c605405b0; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.newsforpermissions
    ADD CONSTRAINT fk_ee31b38c605405b0 FOREIGN KEY (permissionid) REFERENCES pathwaysdos.permissions(id);


--
-- Name: changes fk_ef9d81a189697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.changes
    ADD CONSTRAINT fk_ef9d81a189697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: servicedispositions fk_fa62cf52149eca10; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedispositions
    ADD CONSTRAINT fk_fa62cf52149eca10 FOREIGN KEY (dispositionid) REFERENCES pathwaysdos.dispositions(id) ON DELETE CASCADE;


--
-- Name: servicedispositions fk_fa62cf5289697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicedispositions
    ADD CONSTRAINT fk_fa62cf5289697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: servicecapacities fk_fbf2e96844c57db; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacities
    ADD CONSTRAINT fk_fbf2e96844c57db FOREIGN KEY (capacitystatusid) REFERENCES pathwaysdos.capacitystatuses(capacitystatusid) ON DELETE CASCADE;


--
-- Name: servicecapacities fk_fbf2e9689697fa8; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicecapacities
    ADD CONSTRAINT fk_fbf2e9689697fa8 FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: organisationpostcodes fk_op_location_id; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationpostcodes
    ADD CONSTRAINT fk_op_location_id FOREIGN KEY (locationid) REFERENCES pathwaysdos.locations(id) ON DELETE CASCADE;


--
-- Name: organisationpostcodes fk_op_organisation_id; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationpostcodes
    ADD CONSTRAINT fk_op_organisation_id FOREIGN KEY (organisationid) REFERENCES pathwaysdos.organisations(id) ON DELETE CASCADE;


--
-- Name: organisations fk_organisation_organisationtype; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisations
    ADD CONSTRAINT fk_organisation_organisationtype FOREIGN KEY (organisationtypeid) REFERENCES pathwaysdos.organisationtypes(id);


--
-- Name: organisationrankingstrategies fk_ors_organisation_id; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationrankingstrategies
    ADD CONSTRAINT fk_ors_organisation_id FOREIGN KEY (organisationid) REFERENCES pathwaysdos.organisations(id) ON DELETE CASCADE;


--
-- Name: organisationrankingstrategies fk_ors_servicetype_id; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisationrankingstrategies
    ADD CONSTRAINT fk_ors_servicetype_id FOREIGN KEY (servicetypeid) REFERENCES pathwaysdos.servicetypes(id) ON DELETE CASCADE;


--
-- Name: scenarios fk_scenarios_disposition; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenarios
    ADD CONSTRAINT fk_scenarios_disposition FOREIGN KEY (dispositionid) REFERENCES pathwaysdos.dispositions(id);


--
-- Name: scenarios fk_scenarios_scenariobundle; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenarios
    ADD CONSTRAINT fk_scenarios_scenariobundle FOREIGN KEY (scenariobundleid) REFERENCES pathwaysdos.scenariobundles(id);


--
-- Name: scenarios fk_scenarios_symptomdiscriminator; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenarios
    ADD CONSTRAINT fk_scenarios_symptomdiscriminator FOREIGN KEY (symptomdiscriminatorid) REFERENCES pathwaysdos.symptomdiscriminators(id);


--
-- Name: scenarios fk_scenarios_symptomgroup; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.scenarios
    ADD CONSTRAINT fk_scenarios_symptomgroup FOREIGN KEY (symptomgroupid) REFERENCES pathwaysdos.symptomgroups(id);


--
-- Name: services fk_services_organisation_id; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.services
    ADD CONSTRAINT fk_services_organisation_id FOREIGN KEY (organisationid) REFERENCES pathwaysdos.organisations(id);


--
-- Name: organisations organisations_subregionid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.organisations
    ADD CONSTRAINT organisations_subregionid_fkey FOREIGN KEY (subregionid) REFERENCES pathwaysdos.services(id);


--
-- Name: servicealignments servicealignments_commissioningorganisationid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicealignments
    ADD CONSTRAINT servicealignments_commissioningorganisationid_fkey FOREIGN KEY (commissioningorganisationid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: servicealignments servicealignments_serviceid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicealignments
    ADD CONSTRAINT servicealignments_serviceid_fkey FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: serviceattributes serviceattributes_createduserid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributes
    ADD CONSTRAINT serviceattributes_createduserid_fkey FOREIGN KEY (createduserid) REFERENCES pathwaysdos.users(id);


--
-- Name: serviceattributes serviceattributes_modifieduserid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributes
    ADD CONSTRAINT serviceattributes_modifieduserid_fkey FOREIGN KEY (modifieduserid) REFERENCES pathwaysdos.users(id);


--
-- Name: serviceattributes serviceattributes_serviceattributetypeid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributes
    ADD CONSTRAINT serviceattributes_serviceattributetypeid_fkey FOREIGN KEY (serviceattributetypeid) REFERENCES pathwaysdos.serviceattributetypes(id);


--
-- Name: serviceattributevalues serviceattributevalues_serviceattributeid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceattributevalues
    ADD CONSTRAINT serviceattributevalues_serviceattributeid_fkey FOREIGN KEY (serviceattributeid) REFERENCES pathwaysdos.serviceattributes(id);


--
-- Name: servicenotes servicenotes_services_id_fk; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicenotes
    ADD CONSTRAINT servicenotes_services_id_fk FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: servicenotes servicenotes_users_id_fk; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicenotes
    ADD CONSTRAINT servicenotes_users_id_fk FOREIGN KEY (createdby) REFERENCES pathwaysdos.users(id) ON DELETE SET NULL;


--
-- Name: servicephonenumbers servicephonenumbers_serviceid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.servicephonenumbers
    ADD CONSTRAINT servicephonenumbers_serviceid_fkey FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id) ON DELETE CASCADE;


--
-- Name: serviceserviceattributes serviceserviceattributes_serviceattributeid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceserviceattributes
    ADD CONSTRAINT serviceserviceattributes_serviceattributeid_fkey FOREIGN KEY (serviceattributeid) REFERENCES pathwaysdos.serviceattributes(id);


--
-- Name: serviceserviceattributes serviceserviceattributes_serviceattributevalueid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceserviceattributes
    ADD CONSTRAINT serviceserviceattributes_serviceattributevalueid_fkey FOREIGN KEY (serviceattributevalueid) REFERENCES pathwaysdos.serviceattributevalues(id);


--
-- Name: serviceserviceattributes serviceserviceattributes_serviceid_fkey; Type: FK CONSTRAINT; Schema: pathwaysdos; Owner: -
--

ALTER TABLE ONLY pathwaysdos.serviceserviceattributes
    ADD CONSTRAINT serviceserviceattributes_serviceid_fkey FOREIGN KEY (serviceid) REFERENCES pathwaysdos.services(id);


--
-- PostgreSQL database dump complete
--

