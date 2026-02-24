if [[ -z "$DB_HOST" ]]; then
    echo "Must provide DB_HOST in environment" 1>&2
    exit 1
fi

if [[ -z "$DB_NAME" ]]; then
    echo "Must provide DBNAME in environment" 1>&2
    exit 1
fi

if [[ -z "$PGUSER" ]]; then
    echo "Must provide PGUSER in environment" 1>&2
    exit 1
fi

if [[ -z "$PGPASSWORD" ]]; then
    echo "Must provide PGPASSWORD in environment" 1>&2
    exit 1
fi

echo "services"

psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 132 order by random()) TO 'data_generation/database_updates/test_data_exports/services_132.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 131 order by random()) TO 'data_generation/database_updates/test_data_exports/services_131.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 12 order by random()) TO 'data_generation/database_updates/test_data_exports/services_12.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 100 order by random()) TO 'data_generation/database_updates/test_data_exports/services_100.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 20 order by random()) TO 'data_generation/database_updates/test_data_exports/services_20.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 13 order by random()) TO 'data_generation/database_updates/test_data_exports/services_13.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 149 order by random()) TO 'data_generation/database_updates/test_data_exports/services_149.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 7 order by random()) TO 'data_generation/database_updates/test_data_exports/services_7.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 148 order by random()) TO 'data_generation/database_updates/test_data_exports/services_148.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 21 order by random()) TO 'data_generation/database_updates/test_data_exports/services_21.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 112 order by random()) TO 'data_generation/database_updates/test_data_exports/services_112.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 14 order by random()) TO 'data_generation/database_updates/test_data_exports/services_14.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 29 order by random()) TO 'data_generation/database_updates/test_data_exports/services_29.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 48 order by random()) TO 'data_generation/database_updates/test_data_exports/services_48.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 25 order by random()) TO 'data_generation/database_updates/test_data_exports/services_25.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 11 order by random()) TO 'data_generation/database_updates/test_data_exports/services_11.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 140 order by random()) TO 'data_generation/database_updates/test_data_exports/services_140.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 38 order by random()) TO 'data_generation/database_updates/test_data_exports/services_38.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 156 order by random()) TO 'data_generation/database_updates/test_data_exports/services_156.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 50 order by random()) TO 'data_generation/database_updates/test_data_exports/services_50.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 135 order by random()) TO 'data_generation/database_updates/test_data_exports/services_135.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 105 order by random()) TO 'data_generation/database_updates/test_data_exports/services_105.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT id FROM pathwaysdos.services WHERE typeid = 146 order by random()) TO 'data_generation/database_updates/test_data_exports/services_146.csv' WITH CSV HEADER;"

echo "serviceendpoints"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 132 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_132.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 131 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_131.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 12 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_12.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 100 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_100.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 20 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_20.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 13 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_13.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 149 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_149.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 7 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_7.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 148 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_148.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 21 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_21.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 112 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_112.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 14 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_14.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 29 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_29.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 48 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_48.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 25 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_25.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 11 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_11.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 140 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_140.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 38 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_38.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 156 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_156.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 50 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_50.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 135 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_135.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 105 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_105.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (SELECT se.id FROM pathwaysdos.serviceendpoints se join pathwaysdos.services s on se.serviceid = s.id WHERE s.typeid = 146 order by random()) TO 'data_generation/database_updates/test_data_exports/serviceendpoints_146.csv' WITH CSV HEADER;"

echo "servicesgsds"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 132 group by s.id  order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_132.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 131 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_131.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 12 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_12.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 100 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_100.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 20 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_20.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 13 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_13.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 149 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_149.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 7 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_7.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 148 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_148.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 21 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_21.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 112 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_112.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 14 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_14.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 29 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_29.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 48 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_48.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 25 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_25.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 11 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_11.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 140 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_140.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 38 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_38.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 156 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_156.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 50 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_50.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 135 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_135.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 105 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_105.csv' WITH CSV HEADER;"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select s.id, string_agg(ssgsd.sdid::text, '|') as aggegated_sdid from pathwaysdos.servicesgsds ssgsd join pathwaysdos.services s on ssgsd.serviceid = s.id where s.typeid = 146 group by s.id order by random()) TO 'data_generation/database_updates/test_data_exports/servicesgsds_146.csv' WITH CSV HEADER;"

echo "servicesgsds"
psql -h $DB_HOST -d $DB_NAME -c "\COPY (select symptomgroupid, symptomdiscriminatorid from pathwaysdos.symptomgroupsymptomdiscriminators) TO 'data_generation/database_updates/test_data_exports/symptomgroupsymptomdiscriminators.csv' WITH CSV HEADER;"

