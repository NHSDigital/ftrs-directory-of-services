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
-- Data for Name: agegroups; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.agegroups VALUES (1, 'Adult (16+)', 16, 129);
INSERT INTO pathwaysdos.agegroups VALUES (2, 'Child (5-15)', 5, 15);
INSERT INTO pathwaysdos.agegroups VALUES (3, 'Toddler (1-4)', 1, 4);
INSERT INTO pathwaysdos.agegroups VALUES (4, 'Neonate & Infant (0)', 0, 0);
INSERT INTO pathwaysdos.agegroups VALUES (8, 'Older People (65+)', 65, 129);


--
-- Data for Name: capacitystatuses; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.capacitystatuses VALUES (1, 'GREEN');
INSERT INTO pathwaysdos.capacitystatuses VALUES (2, 'AMBER');
INSERT INTO pathwaysdos.capacitystatuses VALUES (3, 'RED');


--
-- Data for Name: genders; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.genders VALUES (1, 'Female', 'F');
INSERT INTO pathwaysdos.genders VALUES (2, 'Male', 'M');
INSERT INTO pathwaysdos.genders VALUES (3, 'Indeterminate', 'I');


--
-- Data for Name: openingtimedays; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.openingtimedays VALUES (1, 'Monday');
INSERT INTO pathwaysdos.openingtimedays VALUES (2, 'Tuesday');
INSERT INTO pathwaysdos.openingtimedays VALUES (3, 'Wednesday');
INSERT INTO pathwaysdos.openingtimedays VALUES (4, 'Thursday');
INSERT INTO pathwaysdos.openingtimedays VALUES (5, 'Friday');
INSERT INTO pathwaysdos.openingtimedays VALUES (6, 'Saturday');
INSERT INTO pathwaysdos.openingtimedays VALUES (7, 'Sunday');
INSERT INTO pathwaysdos.openingtimedays VALUES (8, 'BankHoliday');


--
-- Data for Name: organisationtypes; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.organisationtypes VALUES (1, 'CCG');
INSERT INTO pathwaysdos.organisationtypes VALUES (2, 'LAD');
INSERT INTO pathwaysdos.organisationtypes VALUES (3, 'LDA');


--
-- Data for Name: publicholidays; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.publicholidays VALUES (1, '2018-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (2, '2018-12-26 00:00:00+00', 'Boxing Day');
INSERT INTO pathwaysdos.publicholidays VALUES (3, '2019-01-01 00:00:00+00', 'New Year''s Day');
INSERT INTO pathwaysdos.publicholidays VALUES (4, '2019-04-18 23:00:00+00', 'Good Friday');
INSERT INTO pathwaysdos.publicholidays VALUES (5, '2019-04-20 23:00:00+00', 'Easter Sunday');
INSERT INTO pathwaysdos.publicholidays VALUES (6, '2019-04-21 23:00:00+00', 'Easter Monday');
INSERT INTO pathwaysdos.publicholidays VALUES (7, '2019-05-05 23:00:00+00', 'Early May bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (8, '2019-05-26 23:00:00+00', 'Spring bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (9, '2019-08-25 23:00:00+00', 'Summer bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (10, '2019-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (11, '2019-12-26 00:00:00+00', 'Boxing Day');
INSERT INTO pathwaysdos.publicholidays VALUES (12, '2020-01-01 00:00:00+00', 'New Year''s Day');
INSERT INTO pathwaysdos.publicholidays VALUES (34, '2020-04-09 23:00:00+00', 'Good Friday');
INSERT INTO pathwaysdos.publicholidays VALUES (35, '2020-04-11 23:00:00+00', 'Easter Sunday');
INSERT INTO pathwaysdos.publicholidays VALUES (36, '2020-04-12 23:00:00+00', 'Easter Monday');
INSERT INTO pathwaysdos.publicholidays VALUES (37, '2020-05-07 23:00:00+00', 'Early May bank holiday (VE day)');
INSERT INTO pathwaysdos.publicholidays VALUES (38, '2020-05-24 23:00:00+00', 'Spring bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (39, '2020-08-30 23:00:00+00', 'Summer bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (40, '2020-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (41, '2020-12-28 00:00:00+00', 'Boxing Day (substitute day)');
INSERT INTO pathwaysdos.publicholidays VALUES (42, '2021-01-01 00:00:00+00', 'New Year''s Day');
INSERT INTO pathwaysdos.publicholidays VALUES (43, '2021-04-01 23:00:00+00', 'Good Friday');
INSERT INTO pathwaysdos.publicholidays VALUES (44, '2021-04-03 23:00:00+00', 'Easter Sunday');
INSERT INTO pathwaysdos.publicholidays VALUES (45, '2021-04-04 23:00:00+00', 'Easter Monday');
INSERT INTO pathwaysdos.publicholidays VALUES (46, '2021-05-02 23:00:00+00', 'Early May bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (47, '2021-05-30 23:00:00+00', 'Spring bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (48, '2021-08-29 23:00:00+00', 'Summer bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (49, '2021-12-27 00:00:00+00', 'Christmas Day (substitute day)');
INSERT INTO pathwaysdos.publicholidays VALUES (50, '2021-12-28 00:00:00+00', 'Boxing Day (substitute day)');
INSERT INTO pathwaysdos.publicholidays VALUES (51, '2021-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (52, '2022-01-03 00:00:00+00', 'New Year''s Day (substitute day)');
INSERT INTO pathwaysdos.publicholidays VALUES (53, '2022-04-14 23:00:00+00', 'Good Friday');
INSERT INTO pathwaysdos.publicholidays VALUES (54, '2022-04-16 23:00:00+00', 'Easter Sunday');
INSERT INTO pathwaysdos.publicholidays VALUES (55, '2022-04-17 23:00:00+00', 'Easter Monday');
INSERT INTO pathwaysdos.publicholidays VALUES (56, '2022-05-01 23:00:00+00', 'Early May bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (57, '2022-06-01 23:00:00+00', 'Spring bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (58, '2022-06-02 23:00:00+00', 'Platinum Jubilee bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (59, '2022-08-28 23:00:00+00', 'Summer bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (60, '2022-12-26 00:00:00+00', 'Boxing Day');
INSERT INTO pathwaysdos.publicholidays VALUES (61, '2022-12-27 00:00:00+00', 'Christmas Day (substitute day)');
INSERT INTO pathwaysdos.publicholidays VALUES (62, '2022-09-18 23:00:00+00', 'Bank Holiday for the State Funeral of Queen Elizabeth II');
INSERT INTO pathwaysdos.publicholidays VALUES (63, '2023-01-02 00:00:00+00', 'New Year''s Day (substitute day)');
INSERT INTO pathwaysdos.publicholidays VALUES (64, '2023-04-06 23:00:00+00', 'Good Friday');
INSERT INTO pathwaysdos.publicholidays VALUES (65, '2023-04-08 23:00:00+00', 'Easter Sunday');
INSERT INTO pathwaysdos.publicholidays VALUES (66, '2023-04-09 23:00:00+00', 'Easter Monday');
INSERT INTO pathwaysdos.publicholidays VALUES (67, '2023-04-30 23:00:00+00', 'Early May bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (68, '2023-05-28 23:00:00+00', 'Spring bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (69, '2023-08-27 23:00:00+00', 'Summer bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (70, '2023-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (71, '2023-12-26 00:00:00+00', 'Boxing Day');
INSERT INTO pathwaysdos.publicholidays VALUES (72, '2022-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (73, '2023-05-07 23:00:00+00', 'Bank holiday for the coronation of King Charles III');
INSERT INTO pathwaysdos.publicholidays VALUES (74, '2024-01-01 00:00:00+00', 'New Year''s Day');
INSERT INTO pathwaysdos.publicholidays VALUES (75, '2024-03-29 00:00:00+00', 'Good Friday');
INSERT INTO pathwaysdos.publicholidays VALUES (76, '2024-03-31 00:00:00+00', 'Easter Sunday');
INSERT INTO pathwaysdos.publicholidays VALUES (77, '2024-03-31 23:00:00+00', 'Easter Monday');
INSERT INTO pathwaysdos.publicholidays VALUES (78, '2024-05-05 23:00:00+00', 'Early May bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (79, '2024-05-26 23:00:00+00', 'Spring bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (80, '2024-08-25 23:00:00+00', 'Summer bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (81, '2024-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (82, '2024-12-26 00:00:00+00', 'Boxing Day');
INSERT INTO pathwaysdos.publicholidays VALUES (83, '2025-01-01 00:00:00+00', 'New Year''s Day');
INSERT INTO pathwaysdos.publicholidays VALUES (84, '2025-04-17 23:00:00+00', 'Good Friday');
INSERT INTO pathwaysdos.publicholidays VALUES (85, '2025-04-19 23:00:00+00', 'Easter Sunday');
INSERT INTO pathwaysdos.publicholidays VALUES (86, '2025-04-20 23:00:00+00', 'Easter Monday');
INSERT INTO pathwaysdos.publicholidays VALUES (87, '2025-05-04 23:00:00+00', 'Early May bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (88, '2025-05-25 23:00:00+00', 'Spring bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (89, '2025-08-24 23:00:00+00', 'Summer bank holiday');
INSERT INTO pathwaysdos.publicholidays VALUES (90, '2025-12-25 00:00:00+00', 'Christmas Day');
INSERT INTO pathwaysdos.publicholidays VALUES (91, '2025-12-26 00:00:00+00', 'Boxing Day');


--
-- Data for Name: referralroles; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.referralroles VALUES (1, 'Public Facing');
INSERT INTO pathwaysdos.referralroles VALUES (129, 'Digital Referral');
INSERT INTO pathwaysdos.referralroles VALUES (130, 'NHSUK');
INSERT INTO pathwaysdos.referralroles VALUES (131, 'ED Streaming Referral');
INSERT INTO pathwaysdos.referralroles VALUES (132, 'Nil referrals');
INSERT INTO pathwaysdos.referralroles VALUES (24, 'Professional Referral');
INSERT INTO pathwaysdos.referralroles VALUES (23, '111 Telephony Referral');
INSERT INTO pathwaysdos.referralroles VALUES (25, 'CAS Referral');
INSERT INTO pathwaysdos.referralroles VALUES (26, '999 Referral');
INSERT INTO pathwaysdos.referralroles VALUES (133, '111 Telephony Referral DHU');
INSERT INTO pathwaysdos.referralroles VALUES (134, '111 Telephony Referral IOW');
INSERT INTO pathwaysdos.referralroles VALUES (135, '111 Telephony Referral LAS');
INSERT INTO pathwaysdos.referralroles VALUES (136, '111 Telephony Referral NWAS');
INSERT INTO pathwaysdos.referralroles VALUES (137, '111 Telephony Referral WMAS');
INSERT INTO pathwaysdos.referralroles VALUES (138, '111 Telephony Referral SCAS');
INSERT INTO pathwaysdos.referralroles VALUES (139, 'CAS Referral WMAS');
INSERT INTO pathwaysdos.referralroles VALUES (140, 'CAS Referral NWAS');
INSERT INTO pathwaysdos.referralroles VALUES (141, 'CAD Portal WMAS');
INSERT INTO pathwaysdos.referralroles VALUES (142, 'Primary Care Referral');


--
-- Data for Name: serviceattributes; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.serviceattributes VALUES (5, 'Digital_Go_With_Notif', 'Urgent Care Self Service referral, patient to go with notification', 1, true, '2021-06-18 13:27:08+00', 28576, '2021-06-18 13:27:08+00', 28576);
INSERT INTO pathwaysdos.serviceattributes VALUES (1009, 'webchat_enabled', 'Describes whether or not a service can accept webchat for 111Online', 1, true, '2022-01-26 10:50:16+00', 5828, '2022-01-26 10:50:16+00', 5828);
INSERT INTO pathwaysdos.serviceattributes VALUES (4, 'requirebooking', 'The service only accepts referrals with an accompanying booked appointment.', 1, true, '2020-04-22 09:48:52+00', 31, '2020-04-22 09:48:52+00', 31);
INSERT INTO pathwaysdos.serviceattributes VALUES (2015, 'Website Signposting', 'Services that use a website as their primary method of referral', 1, true, '2023-09-08 12:18:28+00', 31, '2023-09-08 12:18:28+00', 31);


--
-- Data for Name: serviceattributetypes; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.serviceattributetypes VALUES (1, 'Boolean', 'True or false', '["TRUE", "FALSE"]');


--
-- Data for Name: serviceattributevalues; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.serviceattributevalues VALUES (7, 4, 'TRUE');
INSERT INTO pathwaysdos.serviceattributevalues VALUES (9, 5, 'TRUE');
INSERT INTO pathwaysdos.serviceattributevalues VALUES (10, 5, 'FALSE');
INSERT INTO pathwaysdos.serviceattributevalues VALUES (1014, 1009, 'TRUE');
INSERT INTO pathwaysdos.serviceattributevalues VALUES (1015, 1009, 'FALSE');
INSERT INTO pathwaysdos.serviceattributevalues VALUES (2022, 2015, 'TRUE');
INSERT INTO pathwaysdos.serviceattributevalues VALUES (2023, 2015, 'FALSE');


--
-- Data for Name: servicestatuses; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.servicestatuses VALUES (1, 'active');
INSERT INTO pathwaysdos.servicestatuses VALUES (2, 'closed');
INSERT INTO pathwaysdos.servicestatuses VALUES (3, 'commissioning');
INSERT INTO pathwaysdos.servicestatuses VALUES (4, 'pending');
INSERT INTO pathwaysdos.servicestatuses VALUES (5, 'suspended');
INSERT INTO pathwaysdos.servicestatuses VALUES (6, 'retired');
INSERT INTO pathwaysdos.servicestatuses VALUES (7, 'template');


--
-- Data for Name: servicetypes; Type: TABLE DATA; Schema: pathwaysdos; Owner: appuser
--

INSERT INTO pathwaysdos.servicetypes VALUES (139, 'Integrated Urgent Care (IUC) Validation', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (140, 'Same Day Emergency Care (SDEC)', '8', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (143, 'Sexual Assault Referral Centre (SARC)', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (146, 'Urgent Community Response (UCR)', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (131, 'Pharmacy Urgent Medicines Supply', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (22, 'Commissioning Organisation', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (-1, 'DoS Region', NULL, true, 'n/a', 'interval ');
INSERT INTO pathwaysdos.servicetypes VALUES (20, 'Community Based', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (6, 'Commissioning Cluster', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (107, '(Capacity) Critical Care (CC)', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (108, '(Capacity) Paediatrics Intensive Care Unit (PICU)', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (109, '(Capacity) Burns (B)', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (110, '(Capacity) Maternity and Neonate (MN)', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (111, '(Capacity) Paediatrics (PDR)', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (114, '(Capacity) Acute Hospital', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (115, '(Capacity) Provider Escalation/RAG', NULL, true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (13, 'Pharmacy', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (134, 'Pharmacy Distance Selling', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (7, 'Mental Health', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (29, 'Sexual Health', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (113, 'Health Information', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (129, 'Safeguarding', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (8, 'Social Care', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (18, 'Health Visitor', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (19, 'Midwifery', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (27, 'Intermediate Care', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (50, 'Palliative Care', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (138, 'Emergency National Response', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (136, 'GP Access Hub', '4', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (100, 'GP Practice', '4', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (135, 'Urgent Treatment Centre (UTC)', '5', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (47, 'Dental Emergency', '8', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (121, 'Primary Percutaneous Coronary Intervention (PPCI)', '8', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (122, 'Hyper-Acute Stroke Unit (HASU)', '8', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (12, 'Dental Practice', '4', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (38, 'Community/District Nursing', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (133, 'Integrated Urgent Care (IUC) Clinical Assessment', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (25, 'Integrated Urgent Care (IUC) Treatment', '7', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (-2, 'Local Template', 'NULL', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (14, 'Optical', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (112, 'Optical Enhanced', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (137, 'Integrated Urgent Care (IUC) Pharmacy Clinical Assessment', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (132, 'Pharmacy Enhanced', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (21, 'Retired', 'NULL', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (48, 'Specialist', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (46, 'Urgent Care', '5', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (11, 'Voluntary', '3', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (41, 'Hospital Acute Assessment Unit (AAU)', '8', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (120, 'Emergency Department (ED) Eye Casualty', '8', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (141, 'Hospital Streaming', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (142, 'Mental Health Crisis', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (24, 'Care Home', '10', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (28, 'Community Hospital', '10', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (40, 'Emergency Department (ED) Catch-All', '9', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (105, 'Emergency Department (ED)', '9', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (17, 'Clinic', '10', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (144, 'Integrated Urgent Care (IUC) Dental Clinical Assessment', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (130, 'Integrated Urgent Care (IUC) NHS 111 Call Handling', '8', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (4, 'Therapy', '10', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (145, 'Integrated Urgent Care (IUC) Paediatric Clinical Assessment', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (147, 'Covid Medicines Delivery Unit (CMDU)', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (148, 'Pharmacy Blood Pressure Check', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (149, 'Pharmacy Contraception', '1', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (150, 'Urgent Treatment Centre (UTC) Co-Located with ED', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (151, 'Primary Care Network (PCN)', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (152, 'Primary Care Network (PCN) Enhanced Service', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (153, 'Maternity and Neonatal', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (154, 'Early Pregnancy Assessment Unit (EPAU)', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (155, 'Virtual Ward', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (156, 'Dental Urgent Care', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (157, 'Infection Hub', '6', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (158, 'Ambulance Service Pathway', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (159, 'Primary Care Clinic', '2', true, 'n/a', 'interval');
INSERT INTO pathwaysdos.servicetypes VALUES (160, 'Care Transfer Hub', '10', true, 'n/a', 'interval');


--
-- Name: capacitystatuses_capacitystatusid_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.capacitystatuses_capacitystatusid_seq', 2040, true);


--
-- Name: genders_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.genders_id_seq', 2007, true);


--
-- Name: openingtimedays_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.openingtimedays_id_seq', 2040, true);


--
-- Name: organisationtypes_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.organisationtypes_id_seq', 2010, true);


--
-- Name: publicholidays_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.publicholidays_id_seq', 123, true);


--
-- Name: serviceattributes_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.serviceattributes_id_seq', 2047, true);


--
-- Name: serviceattributetypes_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.serviceattributetypes_id_seq', 2008, true);


--
-- Name: serviceattributevalues_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.serviceattributevalues_id_seq', 2055, true);


--
-- Name: servicestatuses_id_seq; Type: SEQUENCE SET; Schema: pathwaysdos; Owner: appuser
--

SELECT pg_catalog.setval('pathwaysdos.servicestatuses_id_seq', 2007, true);


--
-- PostgreSQL database dump complete
--

