Feature: DMS Schema Index Creation After Full Load
  As a data migration engineer
  I want to ensure that indexes are created after DMS full load
  So that database performance is maintained after bulk data migration

  Background:
    Given the database has schema and data from source

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for services table
    Given the "services" table exists with data
    And all indexes are dropped from "services" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "services" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for servicetypes table
    Given the "servicetypes" table exists with data
    And all indexes are dropped from "servicetypes" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "servicetypes" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for serviceendpoints table
    Given the "serviceendpoints" table exists with data
    And all indexes are dropped from "serviceendpoints" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "serviceendpoints" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for servicedayopenings table
    Given the "servicedayopenings" table exists with data
    And all indexes are dropped from "servicedayopenings" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "servicedayopenings" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for servicedayopeningtimes table
    Given the "servicedayopeningtimes" table exists with data
    And all indexes are dropped from "servicedayopeningtimes" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "servicedayopeningtimes" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for servicesgsds table
    Given the "servicesgsds" table exists with data
    And all indexes are dropped from "servicesgsds" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "servicesgsds" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for servicedispositions table
    Given the "servicedispositions" table exists with data
    And all indexes are dropped from "servicedispositions" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "servicedispositions" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for servicespecifiedopeningdates table
    Given the "servicespecifiedopeningdates" table exists with data
    And all indexes are dropped from "servicespecifiedopeningdates" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "servicespecifiedopeningdates" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Indexes are created for servicespecifiedopeningtimes table
    Given the "servicespecifiedopeningtimes" table exists with data
    And all indexes are dropped from "servicespecifiedopeningtimes" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "servicespecifiedopeningtimes" table

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: Index creation is idempotent
    Given the "services" table exists with data
    And all indexes are already created on "services" table
    When the DMS provisioner creates indexes from schema file
    Then all indexes should exist on "services" table
    And no errors should occur

  @test-db-load-schema-data-migration
  @dms_schema
  Scenario: All required tables receive indexes
    Given all INDEXES_TABLES exist with data
    And all indexes are dropped from all INDEXES_TABLES
    When the DMS provisioner creates indexes from schema file
    Then all INDEXES_TABLES should have their indexes created
