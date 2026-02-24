# Data Generation Scripts

This subproject contains a set of data generation scripts designed to facilitate the re-generation of CSV data used by tests. These scripts automate the creation of test data, ensuring consistency and reproducibility across different testing scenarios.

## Purpose
The scripts in this directory are used to:
- Generate CSV files with test data based on predefined rules and weights
- Simulate realistic data for various test cases

## Usage
Run the scripts as needed to produce the required CSV files for your tests. Ensure that any dependencies, such as Python libraries, are installed before execution.

### DOS reference ids
The generation scripts atm do not connect to databases directly
Provide the scripts with the expected set of CSVs with ids either by running `extract_ids_from_source_db.sh` against the soruce database or by copying them from the shared performance test data bucket

### DOS database updates - feed and bulk
Service type split and field update action split based on https://nhsd-confluence.digital.nhs.uk/spaces/DR/pages/1018849299/Detailed+Update+Stats

Types corresponding to >1% of actions left in (correspond to >90% of total interactions), for each service type, different updates generated proportional to what's described in the pharma/non-pharma types split in related document.
Note: Some actions teporarly disabled to simplify, especially as current implemetation of  doesn't care what field is being updated, just requires an update.

For bulk updates, this is used as the source of truth: https://nhsd-confluence.digital.nhs.uk/spaces/DR/pages/996824555/Bulk+update+statistics


To produce a `../parameter_files/dos/feed_data.csv` and `../parameter_files/dos/bulk_data.csv` files, used by data migration jmeter threads, run:

```
cd scripts/
sh extract_ids_from_source_db.sh
cd data_generation/
poetry install
poetry run generate_database_update_data
```

The script generates 50k feed changes and a 10k rows bulk update file by default, if that is not enough, feel free to modify the script required.

