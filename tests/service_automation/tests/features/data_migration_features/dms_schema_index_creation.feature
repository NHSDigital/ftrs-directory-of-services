@rds_schema_modification @data_migration

Feature: DMS Schema Index Creation After Full Load

  Background:
    Given the database has schema and data from source

  Scenario: Indexes are created for services table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_8a44833f5e237e06" should exist on "services" table

  Scenario: Indexes are created for servicetypes table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_13a6b93b5e237e06" should exist on "servicetypes" table


  Scenario: Indexes are created for serviceendpoints table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_9e65c23389697fa8" should exist on "serviceendpoints" table


  Scenario: Indexes are created for servicedayopenings table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_4256645789697fa8" should exist on "servicedayopenings" table


  Scenario: Indexes are created for servicedayopeningtimes table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_servicedayopeningtimes_servicedayopeningid" should exist on "servicedayopeningtimes" table


  Scenario: Indexes are created for servicesgsds table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_32508c7f89697fa8" should exist on "servicesgsds" table


  Scenario: Indexes are created for servicedispositions table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_fa62cf5289697fa8" should exist on "servicedispositions" table


  Scenario: Indexes are created for servicespecifiedopeningdates table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_servicespecifiedopeningdates_serviceid" should exist on "servicespecifiedopeningdates" table


  Scenario: Indexes are created for servicespecifiedopeningtimes table
    When the DMS provisioner creates indexes from schema file
    Then the index "idx_servicespecifiedopeningtimes_servicespecifiedopeningdateid" should exist on "servicespecifiedopeningtimes" table


  Scenario: Index creation is idempotent
    Given the index "idx_8a44833f5e237e06" already exists on "services" table
    When the DMS provisioner creates indexes from schema file
    And the DMS provisioner creates indexes from schema file
    Then the index "idx_8a44833f5e237e06" should exist on "services" table
    And no errors should occur


  Scenario: All required tables receive indexes
    Given all INDEXES_TABLES exist with data
    And all indexes are dropped from all INDEXES_TABLES
    When the DMS provisioner creates indexes from schema file
    Then all INDEXES_TABLES should have their indexes created
