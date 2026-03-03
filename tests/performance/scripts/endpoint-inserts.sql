with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        1 as endpointorder,
        'email' as transport,
        'PDF' as format,
        'urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0' as interaction,
        'Primary' as buisnessscenario,
        'uncompressed' as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 2 = 0
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    (id || '-dummy-endpoint.email@nhs.net') as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;


with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        2 as endpointorder,
        'email' as transport,
        'PDF' as format,
        'urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0' as interaction,
        'Copy' as buisnessscenario,
        'uncompressed' as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 2 = 0
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    (id || '-dummy-endpoint.email@nhs.net') as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;



with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        2 as endpointorder,
        'http' as transport,
        'CDA' as format,
        'urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0' as interaction,
        'Primary' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 2 = 0
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    ('https://MYTEST.test.test.uk/9cefde/interoperability/gb/test/test-service/report/' || id) as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;



with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        1 as endpointorder,
        'http' as transport,
        'HTML' as format,
        'urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0' as interaction,
        'Primary' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 2 = 1
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    ('https://abc-aaa.test.test.uk:1880/TEST12345TEST_20_R1.svc/'|| id ||'.ITK1') as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;


with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        2 as endpointorder,
        'http' as transport,
        'HTML' as format,
        'urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0' as interaction,
        'Primary' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 2 = 1
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    ('https://MYTEST.test.test.uk/9cefde/interoperability/gb/test/test-service/report/' || id) as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;


with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        2 as endpointorder,
        'http' as transport,
        'HTML' as format,
        'urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0' as interaction,
        'Copy' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 2 = 1
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    (id || '-dummy-endpoint-email@nhs.net') as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;



with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        3 as endpointorder,
        'http' as transport,
        'HTML' as format,
         (array['scheduling', 'urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0'])[ceil(random() * 2)] as interaction,
        'Copy' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 100 = 1
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    (id || '-dummy-endpoint-email@nhs.net') as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;



with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        3 as endpointorder,
        'http' as transport,
        'HTML' as format,
         (array['scheduling', 'urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0'])[ceil(random() * 2)] as interaction,
        'Copy' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 100 and id % 2 = 1
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    (id || '-dummy-endpoint-email@nhs.net') as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;



-- other types 

with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        1 as endpointorder,
        'http' as transport,
        'HTML' as format,
         (array['scheduling', 'urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0'])[ceil(random() * 2)] as interaction,
        'Copy' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 132
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    (id || '-dummy-endpoint-email@nhs.net') as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;



with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        2 as endpointorder,
        'http' as transport,
        'CDA' as format,
        'urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0' as interaction,
        'Primary' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 132
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    ('https://MYTEST.test.test.uk/9cefde/interoperability/gb/test/test-service/report/' || id) as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;



with candidates as (
    SELECT
        nextval('pathwaysdos.serviceendpoints_id_seq'::regclass) as id,
        3 as endpointorder,
        'http' as transport,
        'PDF' as format,
        'urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0' as interaction,
        'Primary' as buisnessscenario,
         (array['uncompressed', 'compressed'])[ceil(random() * 2)] as iscompressionenabled,
        s.id as serviceid
    FROM pathwaysdos.services s
    WHERE typeid = 132
    order by id asc
)
INSERT INTO pathwaysdos.serviceendpoints(id, endpointorder, transport, format, interaction, businessscenario, address, "comment", iscompressionenabled, serviceid)
SELECT 
    id, 
    endpointorder, 
    transport, 
    format, 
    interaction, 
    buisnessscenario, 
    ('https://MYTEST.test.test.uk/9cefde/interoperability/gb/test/test-service/report/' || id) as address,
    ('endpoint comment ' || id) as "comment",
    iscompressionenabled,
    serviceid
FROM candidates;