CREATE SCHEMA if not exists "Core" AUTHORIZATION CURRENT_USER;

SET search_path TO "Core";

-- Table: Core.HealthcareService
DROP TABLE IF EXISTS "Core"."HealthcareService";

CREATE TABLE IF NOT EXISTS "Core"."HealthcareService"
(
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "identifier_oldDos_uid" character varying(255),
    "identifier_oldDos_id" integer,
    "identifier_oldDos_odscode" character varying(255),
    "location" uuid,
    "providedBy" uuid,
    "active" boolean,
    "oldDOS_status" character varying(255),
    "name" character varying(255),
    "ageEligibilityCriteria_DaysFrom" double precision,
    "ageEligibilityCriteria_DaysTo" double precision,
    "openAllHours" boolean,
    "publicInformation" character varying(255),
    "additionalServiceInformation" character varying(255),
    "referralRestrictions" boolean,
    "referralRoles" character varying(255),
    "sexEligibilityCriteria_Female" boolean,
    "sexEligibilityCriteria_Male" boolean,
    "sexEligibilityCriteria_Indeterminate" boolean,
    "telecom_phone_public" character varying(255),
    "telecom_phone_private" character varying(255),
    "telecom_fax" character varying(255),
    "createdBy" character varying(255),
    "createdDateTime" timestamp(0) with time zone,
    "modifiedBy" character varying(255),
    "modifiedDateTime" timestamp(0) with time zone,
    -- Below this is the items we need to consider
    "accessibility" character varying(255),
    "activities" character varying(255),
    "attributes" character varying(255),
    "conditions" character varying(255),
    "exclusion" character varying(255),
    "searchAvailablity" character varying(255)
    -- below this is items we don't necessarily cover in the new system currently but may want.
    -- "oldDos_name" character varying(255),
    -- "oldDos_telephonetriagereferralinstructions" character varying(255),
    -- "oldDos_email" character varying(255),
    -- "oldDos_web" character varying(512),
    -- "oldDos_isNational" character varying(255)
);

ALTER TABLE "Core"."HealthcareService" ALTER COLUMN "createdDateTime" SET DEFAULT now();

ALTER TABLE IF EXISTS "Core"."HealthcareService"
    OWNER to CURRENT_USER;

-- "Core"."Endpoint"
DROP TABLE IF EXISTS "Core"."Endpoint";

CREATE TABLE IF NOT EXISTS "Core"."Endpoint"
(
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "identifier_oldDOS_id" character varying(255),
    "status" character varying(255), --https://build.fhir.org/valueset-endpoint-status.html
    "connectionType" character varying(255), -- https://build.fhir.org/valueset-endpoint-connection-type.html to review?
    "name" character varying(255),
    "payloadType" character varying(255), -- https://build.fhir.org/valueset-endpoint-payload-type.html  to review?
    "address" character varying(255), -- url/email etc
    "managedBy" uuid, -- organisation that manages this
    "service" uuid,
    "createdBy" character varying(255),
    "createdDateTime" timestamp(0) with time zone,
    "modifiedBy" character varying(255),
    "modifiedDateTime" timestamp(0) with time zone
);

ALTER TABLE "Core"."Endpoint" ALTER COLUMN "createdDateTime" SET DEFAULT now();

ALTER TABLE IF EXISTS "Core"."Endpoint"
    OWNER to CURRENT_USER;

-- "Core"."Organisation"
DROP TABLE IF EXISTS "Core"."Organisation";

CREATE TABLE IF NOT EXISTS "Core"."Organisation"
(
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "identifier_ODS_ODSCode" character varying(20),
    "active" boolean NOT NULL,
    "createdBy" character varying(255),
    "createdDateTime" timestamp(0) with time zone,
    "modifiedBy" character varying(255),
    "modifiedDateTime" timestamp(0) with time zone,
    "name" character varying(255),
    "telecom" character varying(255),
    "type" character varying(255) -- requires DoS dataset
    -- address is to be pulled from Location for organisation primary address.
);

ALTER TABLE "Core"."Organisation" ALTER COLUMN "createdDateTime" SET DEFAULT now();

ALTER TABLE IF EXISTS "Core"."Organisation"
    OWNER to CURRENT_USER;

-- "Core"."OrganisationAffilation"
DROP TABLE IF EXISTS "Core"."OrganisationAffilation";

CREATE TABLE IF NOT EXISTS "Core"."OrganisationAffilation"
(
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "active" boolean NOT NULL,
    "code" character varying(255),
    "createdBy" character varying(255), -- When it went live
    "createdDateTime" timestamp(0) with time zone,
    "modifiedBy" character varying(255), -- End period if active is false
    "modifiedDateTime" timestamp(0) with time zone,
    "organisation" uuid NOT NULL,
    "participatingOrganisation" uuid NOT NULL
);

ALTER TABLE "Core"."OrganisationAffilation" ALTER COLUMN "createdDateTime" SET DEFAULT now();

ALTER TABLE IF EXISTS "Core"."OrganisationAffilation"
    OWNER to CURRENT_USER;

-- "Core"."OrganisationAffilation"
DROP TABLE IF EXISTS "Core"."Location";

CREATE TABLE IF NOT EXISTS "Core"."Location"
(
    "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    "active" boolean NOT NULL,
    "address" character varying(255),
    "createdBy" character varying(255), -- When it went live
    "createdDateTime" timestamp(0) with time zone,
    "managingOrganisation" uuid,
    "modifiedBy" character varying(255), -- End period if active is false
    "modifiedDateTime" timestamp(0) with time zone,
    "name" character varying(255),
    "positionGCS_latitude" double precision,
    "positionGCS_longitude" double precision,
    "postitionReferenceNumber_UPRN"	character varying(255),
    "postitionReferenceNumber_UBRN"	character varying(255),
    "primaryAddress" boolean NOT NULL, -- maybe we should add the link inside organisation to it's primary Location rather than boolean here for enforcing singular primary address for organisation
    "partOf" uuid -- will be null for a while
);

ALTER TABLE "Core"."Location" ALTER COLUMN "createdDateTime" SET DEFAULT now();

ALTER TABLE IF EXISTS "Core"."Location"
    OWNER to CURRENT_USER;

-- Add foreign keys for referential integrity, none are enforced required.
ALTER TABLE "Core"."Endpoint" ADD FOREIGN KEY ("managedBy") REFERENCES "Organisation" ("id");
ALTER TABLE "Core"."Location" ADD FOREIGN KEY ("managingOrganisation") REFERENCES "Organisation" ("id");
ALTER TABLE "Core"."OrganisationAffilation" ADD FOREIGN KEY ("organisation") REFERENCES "Organisation" ("id");
ALTER TABLE "Core"."OrganisationAffilation" ADD FOREIGN KEY ("participatingOrganisation") REFERENCES "Organisation" ("id");
ALTER TABLE "Core"."HealthcareService" ADD FOREIGN KEY ("location") REFERENCES "Location" ("id");
ALTER TABLE "Core"."HealthcareService" ADD FOREIGN KEY ("providedBy") REFERENCES "Organisation" ("id");


-- we can copy source system modified at, but should consider a trigger
--    in future when one-way sync turned on and we want to test other data sources.

-- CREATE OR REPLACE FUNCTION "update_modified_column"()
-- RETURNS TRIGGER AS $$
--     BEGIN
--         NEW.modifiedDateTime = now();
--         RETURN NEW;
--     END;
-- $$ language 'plpgsql';

-- CREATE TRIGGER update_modified_time_HealthcareService
--     BEFORE UPDATE ON "Core"."HealthcareService"
--     FOR EACH ROW
--     WHEN (OLD.modifiedDateTime = NEW.modifiedDateTime)
--     EXECUTE FUNCTION update_modified_column();
