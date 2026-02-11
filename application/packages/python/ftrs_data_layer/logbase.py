from logging import DEBUG, ERROR, INFO, WARNING

from ftrs_common.logger import LogBase, LogReference


class DDBLogBase(LogBase):
    """
    LogBase for DynamoDB operations.
    """

    DDB_CORE_001 = LogReference(level=DEBUG, message="Initialised DynamoDB repository")
    DDB_CORE_002 = LogReference(level=DEBUG, message="Putting item into DynamoDB table")
    DDB_CORE_003 = LogReference(level=INFO, message="Item put into DynamoDB table")
    DDB_CORE_004 = LogReference(
        level=ERROR, message="Error putting item into DynamoDB table"
    )

    DDB_CORE_005 = LogReference(level=DEBUG, message="Getting item from DynamoDB table")
    DDB_CORE_006 = LogReference(
        level=INFO, message="Item retrieved from DynamoDB table"
    )
    DDB_CORE_007 = LogReference(
        level=ERROR, message="Error retrieving item from DynamoDB table"
    )
    DDB_CORE_008 = LogReference(
        level=WARNING, message="Item not found in DynamoDB table"
    )

    DDB_CORE_009 = LogReference(level=DEBUG, message="Querying DynamoDB table")
    DDB_CORE_010 = LogReference(level=INFO, message="Completed query on DynamoDB table")
    DDB_CORE_011 = LogReference(level=ERROR, message="Error querying DynamoDB table")

    DDB_CORE_012 = LogReference(
        level=DEBUG, message="Perfoming batch write to DynamoDB"
    )
    DDB_CORE_013 = LogReference(level=INFO, message="Completed batch write to DynamoDB")
    DDB_CORE_014 = LogReference(level=ERROR, message="Error performing batch write")
    DDB_CORE_015 = LogReference(level=ERROR, message="Unprocessed items in batch write")


class DataMigrationLogBase(LogBase):
    """
    LogBase for Data Migration ETL Pipeline operations
    """

    ETL_EXTRACT_001 = LogReference(
        level=INFO, message="Extracting data to {output_path}"
    )
    ETL_EXTRACT_002 = LogReference(
        level=INFO,
        message="Percentage of service profiles: {service_profiles_percentage}%",
    )
    ETL_EXTRACT_003 = LogReference(
        level=INFO, message="Percentage of all data fields: {data_fields_percentage}%"
    )
    ETL_EXTRACT_004 = LogReference(
        level=INFO, message="Data extraction completed successfully."
    )

    ETL_TRANSFORM_001 = LogReference(
        level=INFO, message="Transforming data from {input_path} to {output_path}"
    )
    ETL_TRANSFORM_002 = LogReference(
        level=INFO, message="Transform completed successfully."
    )

    ETL_LOAD_001 = LogReference(
        level=INFO, message="Loading {len_input_df} {table_value}s into {table_value}"
    )
    ETL_LOAD_002 = LogReference(
        level=INFO, message="Loaded {count} {table_value}s into the database."
    )
    ETL_LOAD_003 = LogReference(
        level=INFO,
        message="Data loaded successfully into {env_value} environment, workspace: {workspace_value}",
    )

    ETL_RESET_001 = LogReference(level=INFO, message="Initializing tables...")
    ETL_RESET_002 = LogReference(
        level=ERROR,
        message="The init option is only supported for the local environment.",
    )
    ETL_RESET_003 = LogReference(
        level=INFO, message="Table {table_name} created successfully."
    )
    ETL_RESET_004 = LogReference(
        level=INFO, message="Table {table_name} already exists."
    )
    ETL_RESET_005 = LogReference(
        level=ERROR,
        message="Invalid environment: {env}. Only 'dev' and 'local' are allowed.",
    )
    ETL_RESET_006 = LogReference(
        level=INFO, message="Deleted {count} items from {table_name}"
    )
    ETL_RESET_007 = LogReference(
        level=ERROR, message="Unsupported entity type: {entity_type}"
    )

    DM_ETL_000 = LogReference(
        level=INFO, message="Starting Data Migration ETL Pipeline"
    )
    DM_ETL_001 = LogReference(level=DEBUG, message="Starting to process record")
    DM_ETL_002 = LogReference(
        level=DEBUG,
        message="Transformer {transformer_name} is not valid for record: {reason}",
    )
    DM_ETL_003 = LogReference(
        level=INFO, message="Transformer {transformer_name} selected for record"
    )
    DM_ETL_004 = LogReference(
        level=INFO,
        message="Record was not migrated due to reason: {reason}",
    )
    DM_ETL_005 = LogReference(
        level=INFO,
        message="Record skipped due to condition: {reason}",
    )
    DM_ETL_006 = LogReference(
        level=DEBUG,
        message="Record successfully transformed into future data model",
    )
    DM_ETL_007 = LogReference(
        level=INFO,
        message="Record successfully migrated",
    )
    DM_ETL_008 = LogReference(
        level=ERROR,
        message="Error processing record: {error}",
    )
    DM_ETL_009 = LogReference(
        level=ERROR,
        message="Error parsing event: {error}",
    )
    DM_ETL_010 = LogReference(
        level=WARNING, message="Unsupported event method: {method}"
    )
    DM_ETL_011 = LogReference(
        level=WARNING,
        message="Table {table_name} not supported for event method: {method}",
    )
    DM_ETL_012 = LogReference(
        level=WARNING,
        message="No symptom discriminators found for Symptom Group ID: {sg_id}",
    )
    DM_ETL_013 = LogReference(
        level=WARNING,
        message="Record {record_id} has {issue_count} validation issues {issues}",
    )
    DM_ETL_014 = LogReference(
        level=WARNING,
        message="Record {record_id} failed validation and was not migrated",
    )
    DM_ETL_017 = LogReference(
        level=INFO,
        message="No ageEligibilityCriteria created for Service ID {service_id} as no age range found",
    )

    DM_ETL_018 = LogReference(
        level=WARNING,
        message="Disposition ID {disposition_id} not found in metadata for Service ID {service_id}, skipping disposition",
    )

    DM_ETL_019 = LogReference(
        level=INFO,
        message="State record found for Service ID {record_id}, proceeding with incremental migration",
    )
    DM_ETL_020 = LogReference(
        level=INFO,
        message="No State record found for Service ID {record_id}, proceeding with initial migration",
    )
    DM_ETL_021 = LogReference(
        level=INFO,
        message="Successfully written {item_count} items to DynamoDB",
    )
    DM_ETL_022 = LogReference(
        level=ERROR,
        message="DynamoDB Transaction Cancelled - one or more items failed to write",
    )
    DM_ETL_023 = LogReference(
        level=INFO,
        message="Skipping organisation creation as no transformed organisation data present",
    )
    DM_ETL_024 = LogReference(
        level=INFO, message="Adding organisation create item to transaction"
    )
    DM_ETL_025 = LogReference(
        level=INFO,
        message="Skipping location creation as no transformed location data present",
    )
    DM_ETL_026 = LogReference(
        level=INFO, message="Adding location create item to transaction"
    )
    DM_ETL_027 = LogReference(
        level=INFO,
        message="Skipping healthcare service creation as no transformed healthcare service data present",
    )
    DM_ETL_028 = LogReference(
        level=INFO,
        message="Adding healthcare service create item to transaction",
    )
    DM_ETL_029 = LogReference(
        level=INFO,
        message="Skipping organisation update as no fields have changed since last migration",
    )
    DM_ETL_030 = LogReference(
        level=INFO,
        message="Organisation update detected, adding update item to transaction",
    )
    DM_ETL_031 = LogReference(
        level=INFO,
        message="Skipping location update as no fields have changed since last migration",
    )
    DM_ETL_032 = LogReference(
        level=INFO,
        message="Location update detected, adding update item to transaction",
    )
    DM_ETL_033 = LogReference(
        level=INFO,
        message="Skipping healthcare service update as no fields have changed since last migration",
    )
    DM_ETL_034 = LogReference(
        level=INFO,
        message="Healthcare service update detected, adding update item to transaction",
    )
    DM_ETL_035 = LogReference(
        level=INFO,
        message="Initial migration detected, added migration state record to records",
    )
    DM_ETL_036 = LogReference(
        level=INFO,
        message="Incremental migration detected, added migration state update to records",
    )
    DM_ETL_037 = LogReference(
        level=INFO,
        message="Skipping state record item as no changes were required during migration",
    )

    DM_ETL_999 = LogReference(
        level=INFO, message="Data Migration ETL Pipeline completed successfully."
    )

    DM_QP_000 = LogReference(
        level=INFO,
        message="Starting Data Migration Queue Populator for type_ids={type_ids} and status_ids={status_ids}",
    )
    DM_QP_001 = LogReference(
        level=INFO,
        message="Populating SQS queue with {count} total messages in full sync",
    )

    DM_QP_002 = LogReference(
        level=DEBUG, message="Sending {count} messages to SQS queue"
    )
    DM_QP_003 = LogReference(
        level=ERROR, message="Failed to send {count} messages to SQS queue"
    )
    DM_QP_004 = LogReference(
        level=DEBUG, message="Successfully sent {count} messages to SQS queue"
    )
    DM_QP_005 = LogReference(
        level=INFO,
        message="Populating SQS queue with 1 message in single service sync for service_id={service_id} and record_id={record_id}",
    )
    DM_QP_999 = LogReference(
        level=INFO, message="Data Migration Queue Populator completed"
    )


class UtilsLogBase(LogBase):
    """
    LogBase for utils operations
    """

    UTILS_FILEIO_001 = LogReference(
        level=INFO, message="Reading from S3 path: {file_path}"
    )
    UTILS_FILEIO_002 = LogReference(
        level=INFO, message="Reading from local file path: {file_path}"
    )
    UTILS_FILEIO_003 = LogReference(
        level=ERROR, message="Unsupported path type: {path_type}"
    )
    UTILS_FILEIO_004 = LogReference(
        level=INFO, message="Writing to S3 path: {file_path}"
    )
    UTILS_FILEIO_005 = LogReference(
        level=INFO, message="Writing to local file path: {file_path}"
    )
    UTILS_FILEIO_006 = LogReference(
        level=ERROR, message="Unsupported path type: {path_type}"
    )

    UTILS_SECRET_001 = LogReference(
        level=ERROR, message="The environment or project name does not exist"
    )

    UTILS_VALIDATOR_001 = LogReference(
        level=INFO, message="Bucket {bucket_name} exists and is accessible."
    )
    UTILS_VALIDATOR_002 = LogReference(
        level=WARNING, message="Error checking bucket {bucket_name}: {e}"
    )
    UTILS_VALIDATOR_003 = LogReference(
        level=INFO, message="Object {object_key} exists in bucket {bucket_name}."
    )
    UTILS_VALIDATOR_004 = LogReference(
        level=WARNING,
        message="Error checking object {object_key} in bucket {bucket_name}: {e}",
    )
    UTILS_VALIDATOR_005 = LogReference(
        level=ERROR,
        message="Invalid S3 URI: {s3_uri}. Please provide a valid S3 URI and confirm you have access to the S3 bucket.",
    )
    UTILS_VALIDATOR_006 = LogReference(
        level=ERROR,
        message="File does not exist in S3: {s3_uri}. Please provide a valid S3 URI to an existing file.",
    )
    UTILS_VALIDATOR_007 = LogReference(
        level=ERROR,
        message="File already exists in S3: {s3_uri}. Please provide a different S3 URI.",
    )
    UTILS_VALIDATOR_008 = LogReference(
        level=ERROR,
        message="Parent directory does not exist: {parsed_path_parent}. Please provide a valid path to a file.",
    )
    UTILS_VALIDATOR_009 = LogReference(
        level=ERROR,
        message="File does not exist: {parsed_path}. Please provide a valid path to a file.",
    )
    UTILS_VALIDATOR_010 = LogReference(
        level=ERROR,
        message="File already exists: {parsed_path}. Please provide a different path.",
    )

    UTILS_ADDRESS_FORMATTER_000 = LogReference(
        level=INFO,
        message="Formatting address with address: {address}, town: {town}, postcode: {postcode}",
    )
    UTILS_ADDRESS_FORMATTER_001 = LogReference(
        level=DEBUG, message="Searching county for name: {county_name}"
    )
    UTILS_ADDRESS_FORMATTER_002 = LogReference(
        level=WARNING, message="Error searching for county{county_name}: {error}"
    )
    UTILS_ADDRESS_FORMATTER_003 = LogReference(
        level=DEBUG, message="Matched county name: {county_name}"
    )
    UTILS_ADDRESS_FORMATTER_004 = LogReference(
        level=DEBUG,
        message="No county match found for name falling back to predefined list: {county_name}",
    )
    UTILS_ADDRESS_FORMATTER_005 = LogReference(
        level=DEBUG, message="No county found for name: {county_name}"
    )

    UTILS_GP_PRACTICE_VALIDATOR_001 = LogReference(
        level=INFO,
        message="GP Practice name suffix discarded: original length is {original_length}, sanitized length is {sanitized_length}",
    )
    UTILS_GP_PRACTICE_VALIDATOR_002 = LogReference(
        level=WARNING, message="Disallowed HTML entities detected in GP Practice name"
    )
    UTILS_GP_PRACTICE_VALIDATOR_003 = LogReference(
        level=WARNING, message="Suspicious characters detected in GP practice name"
    )
    UTILS_GP_PRACTICE_VALIDATOR_004 = LogReference(
        level=WARNING,
        message="GP Practice name exceeds maximum length of {max_chars} characters",
    )
    UTILS_GP_PRACTICE_VALIDATOR_005 = LogReference(
        level=INFO,
        message="Suspicious encoding or dangerous patterns detected in GP Practice name",
    )


class OdsETLPipelineLogBase(LogBase):
    """
    LogBase for the ODS ETL Pipeline operations
    """

    ETL_EXTRACTOR_START = LogReference(
        level=INFO,
        message="ETL ODS Extractor Lambda started.",
    )
    ETL_EXTRACTOR_COMPLETE = LogReference(
        level=INFO,
        message="ETL ODS Extractor Lambda completed successfully.",
    )
    ETL_EXTRACTOR_001 = LogReference(
        level=INFO, message="Fetching outdated organizations for date {date}."
    )
    ETL_EXTRACTOR_002 = LogReference(
        level=INFO,
        message="Fetching ODS Data returned {bundle_total} outdated organisations across {total_pages} pages.",
    )
    ETL_EXTRACTOR_003 = LogReference(
        level=INFO,
        message="Processing message id: {message_id} from ODS ETL queue.",
    )
    ETL_EXTRACTOR_007 = LogReference(
        level=WARNING, message="Organisation not found in database."
    )
    ETL_EXTRACTOR_012 = LogReference(
        level=WARNING, message="ODS code extraction failed: {e}."
    )
    ETL_EXTRACTOR_013 = LogReference(
        level=WARNING,
        message="Error when requesting queue url with queue name: {queue_name} with error: {error_message}.",
    )
    ETL_EXTRACTOR_014 = LogReference(
        level=INFO,
        message="Trying to send {number} messages to sqs queue.",
    )
    ETL_EXTRACTOR_015 = LogReference(
        level=WARNING,
        message="Failed to send {failed} messages in batch.",
    )
    ETL_EXTRACTOR_016 = LogReference(
        level=WARNING,
        message="Message {id}: {message} - {code}.",
    )
    ETL_EXTRACTOR_017 = LogReference(
        level=INFO,
        message="Succeeded to send {successful} messages in batch.",
    )
    ETL_EXTRACTOR_018 = LogReference(
        level=WARNING,
        message="Error sending data to queue with error: {error_message}.",
    )
    ETL_EXTRACTOR_020 = LogReference(
        level=INFO,
        message="No organisations found for the given date: {date}.",
    )
    ETL_EXTRACTOR_021 = LogReference(
        level=WARNING,
        message="Invalid environment variable value '{invalid_value}' provided, using default value.",
    )
    ETL_EXTRACTOR_022 = LogReference(
        level=WARNING,
        message="Error fetching data: {error_message}.",
    )
    ETL_EXTRACTOR_023 = LogReference(
        level=WARNING,
        message="Unexpected error: {error_message}.",
    )
    ETL_TRANSFORMER_START = LogReference(
        level=INFO,
        message="ETL ODS Transformer Lambda started.",
    )
    ETL_TRANSFORMER_BATCH_COMPLETE = LogReference(
        level=INFO,
        message="ETL ODS Transformer Lambda batch processing completed.",
    )
    ETL_TRANSFORMER_026 = LogReference(
        level=INFO,
        message="Successfully transformed data for ods_code: {ods_code}.",
    )
    ETL_TRANSFORMER_027 = LogReference(
        level=WARNING,
        message="Error processing organisation with ods_code {ods_code}: {error_message}",
    )
    ETL_EXTRACTOR_028 = LogReference(
        level=INFO,
        message="Fetching organisation uuid for ods code {ods_code}.",
    )
    ETL_EXTRACTOR_029 = LogReference(
        level=WARNING,
        message="Error processing date with code: {status_code} and message: {error_message}.",
    )
    ETL_EXTRACTOR_030 = LogReference(
        level=WARNING,
        message="Fetching organisation uuid for ods code {ods_code} failed, resource type {type} returned.",
    )
    ETL_EXTRACTOR_034 = LogReference(
        level=INFO, message="Processing page {page_num} for date {date}."
    )
    ETL_EXTRACTOR_035 = LogReference(
        level=INFO,
        message="Page {page_num} returned {page_total} organisations. Cumulative total: {cumulative_total}.",
    )
    ETL_CONSUMER_START = LogReference(
        level=INFO,
        message="ETL ODS Consumer Lambda started.",
    )
    ETL_CONSUMER_BATCH_COMPLETE = LogReference(
        level=INFO,
        message="ETL ODS Consumer Lambda batch processing completed.",
    )
    ETL_CONSUMER_001 = LogReference(
        level=INFO,
        message="Received event for ODS ETL consumer lambda.",
    )
    ETL_CONSUMER_002 = LogReference(
        level=INFO,
        message="Records received: {total_records}.",
    )
    ETL_CONSUMER_003 = LogReference(
        level=INFO,
        message="Processing message id: {message_id} of {total_records} from ODS ETL queue.",
    )
    ETL_CONSUMER_004 = LogReference(
        level=INFO,
        message="Message id: {message_id} processed successfully.",
    )
    ETL_CONSUMER_005 = LogReference(
        level=ERROR,
        message="Failed to process message id: {message_id}.",
    )
    ETL_CONSUMER_006 = LogReference(
        level=WARNING,
        message="Message id: {message_id} is missing 'path' or 'body' fields.",
    )
    ETL_CONSUMER_007 = LogReference(
        level=INFO,
        message="Successfully sent request to API. Response status code: {status_code}.",
    )
    ETL_CONSUMER_008 = LogReference(
        level=ERROR,
        message="Bad request returned for message id: {message_id}. Not re-processing.",
    )
    ETL_CONSUMER_009 = LogReference(
        level=ERROR,
        message="Request failed for message id: {message_id}.",
    )
    ETL_CONSUMER_010 = LogReference(
        level=ERROR,
        message="Returning {retry_count} messages to queue due to failure out of {total_records} records.",
    )
    ETL_UTILS_001 = LogReference(
        level=INFO,
        message="Running in local environment, using LOCAL_CRUD_API_URL environment variable.",
    )
    ETL_UTILS_002 = LogReference(
        level=INFO,
        message="Fetching base CRUD API URL from parameter store: {parameter_path}.",
    )
    ETL_UTILS_003 = LogReference(
        level=WARNING,
        message="HTTP error occurred: {http_err} - Status Code: {status_code}.",
    )
    ETL_UTILS_004 = LogReference(
        level=WARNING,
        message="Request to {method} {url} failed: {error_message}.",
    )
    ETL_UTILS_005 = LogReference(
        level=INFO,
        message="Running in local environment, using LOCAL api key environment variable.",
    )
    ETL_UTILS_006 = LogReference(
        level=ERROR,
        message="Error with secret: {secret_name} with message {error_message}.",
    )
    ETL_UTILS_007 = LogReference(
        level=ERROR,
        message="Error decoding json with issue: {error_message}.",
    )
    ETL_UTILS_008 = LogReference(
        level=INFO,
        message="Running in against automated tests, using api key for mock from secret manager.",
    )
    ETL_UTILS_009 = LogReference(
        level=INFO,
        message="Running in against automated tests, sending request to mock API Gateway with x-api-key header",
    )
    ETL_UTILS_010 = LogReference(
        level=INFO,
        message="Receiving API key for ODS Terminology API",
    )
    ETL_UTILS_011 = LogReference(
        level=INFO,
        message="Attempting to use mock ODS api in unauthorized environment: {env}. Mock can only be used in dev and test",
    )
    ETL_UTILS_012 = LogReference(
        level=ERROR,
        message="Unable to get ODS path with message: {error_message}.",
    )


class CrudApisLogBase(LogBase):
    """
    LogBase for the CRUD API operations
    """

    ORGANISATION_001 = LogReference(
        level=INFO,
        message="Received request to get organisation is with ODS code: {ods_code}.",
    )
    ORGANISATION_002 = LogReference(
        level=ERROR,
        message="Organisation with ODS code {ods_code} not found.",
    )
    ORGANISATION_003 = LogReference(
        level=INFO,
        message="Received request to read organisation with ID: {organisation_id}.",
    )
    ORGANISATION_004 = LogReference(
        level=INFO,
        message="Received request to read all organisations.",
    )
    ORGANISATION_005 = LogReference(
        level=INFO,
        message="Received request to update organisation with ID: {organisation_id}.",
    )
    ORGANISATION_006 = LogReference(
        level=INFO,
        message="Computed outdated fields: {outdated_fields} for organisation {organisation_id}.",
    )
    ORGANISATION_007 = LogReference(
        level=INFO,
        message="No changes detected for organisation {organisation_id}.",
    )
    ORGANISATION_008 = LogReference(
        level=INFO,
        message="Successfully updated organisation {organisation_id}.",
    )
    ORGANISATION_009 = LogReference(
        level=INFO,
        message="Applying updates to organisation: {organisation_id}.",
    )
    ORGANISATION_010 = LogReference(
        level=INFO,
        message="Organisation with ID {organisation_id} not found.",
    )
    ORGANISATION_011 = LogReference(
        level=INFO,
        message="Received request to create a new organisation with ODS code: {ods_code}.",
    )
    ORGANISATION_012 = LogReference(
        level=ERROR,
        message="Please provide an ODS code for the organisation.",
    )
    ORGANISATION_013 = LogReference(
        level=ERROR,
        message="Organisation with ODS code {ods_code} already exists.",
    )
    ORGANISATION_014 = LogReference(
        level=INFO,
        message="Organisation ID {organisation_id} provided for new organisations,Will be ignored.Creating a new organisation with a new ID.",
    )
    ORGANISATION_015 = LogReference(
        level=INFO,
        message="Successfully created organisation with ODS code: {ods_code} & organisation ID {organisation_id}.",
    )
    ORGANISATION_016 = LogReference(
        level=ERROR,
        message="Error creating organisation with ODS code {ods_code}:{error_message}.",
    )
    ORGANISATION_017 = LogReference(
        level=ERROR,
        message="Received request to delete organisation with ID: {organisation_id}.",
    )
    ORGANISATION_018 = LogReference(
        level=INFO,
        message="Successfully deleted organisation with ID: {organisation_id}.",
    )
    ORGANISATION_019 = LogReference(
        level=ERROR,
        message="Error updating organisation with organisation_id {organisation_id}:{error_message}.",
    )
    ORGANISATION_020 = LogReference(
        level=ERROR,
        message="Unable to retrieve any organisations.",
    )
    ORGANISATION_021 = LogReference(
        level=ERROR,
        message="Error getting organisation(s): {error_message}.",
    )
    ORGANISATION_022 = LogReference(
        level=ERROR,
        message="Error: Active field is required and cannot be null.",
    )
    ORGANISATION_023 = LogReference(
        level=WARNING,
        message="Received invalid legal dates, legal period start and end dates are equal: {date}.",
    )
    ORGANISATION_024 = LogReference(
        level=ERROR,
        message="Error when validating roles for organisation {organisation_id}: {error_message}.",
    )
    HEALTHCARESERVICE_001 = LogReference(
        level=INFO,
        message="Received request to create healthcare service with name: {name} and type: {type}.",
    )
    HEALTHCARESERVICE_002 = LogReference(
        level=INFO,
        message="Successfully created healthcare service with ID: {id}.",
    )
    HEALTHCARESERVICE_003 = LogReference(
        level=INFO,
        message="Received request to update healthcare service with ID: {service_id}.",
    )
    HEALTHCARESERVICE_004 = LogReference(
        level=INFO,
        message="Successfully updated healthcare service {service_id}.",
    )
    HEALTHCARESERVICE_005 = LogReference(
        level=INFO,
        message="Applying updates to healthcare service: {service_id}.",
    )
    HEALTHCARESERVICE_006 = LogReference(
        level=INFO,
        message="Received request to read healthcare service with ID: {service_id}.",
    )
    HEALTHCARESERVICE_007 = LogReference(
        level=INFO,
        message="Received request to read all healthcare services.",
    )
    HEALTHCARESERVICE_008 = LogReference(
        level=INFO,
        message="Successfully retrieved healthcare service: {service}.",
    )
    HEALTHCARESERVICE_009 = LogReference(
        level=ERROR,
        message="Received request to delete healthcare service with ID: {service_id}.",
    )
    HEALTHCARESERVICE_010 = LogReference(
        level=INFO,
        message="Successfully deleted healthcare service with ID: {service_id}.",
    )
    HEALTHCARESERVICE_011 = LogReference(
        level=INFO,
        message="Successfully created healthcare service: {service}.",
    )
    HEALTHCARESERVICE_012 = LogReference(
        level=INFO,
        message="Found {length} healthcare services.",
    )
    HEALTHCARESERVICE_E001 = LogReference(
        level=ERROR,
        message="Error updating healthcare service with service_id {service_id}:{error_message}.",
    )
    HEALTHCARESERVICE_E002 = LogReference(
        level=ERROR,
        message="Healthcare Service with ID {service_id} not found.",
    )
    HEALTHCARESERVICE_E003 = LogReference(
        level=ERROR,
        message="No healthcare services found.",
    )
    HEALTHCARESERVICE_E004 = LogReference(
        level=ERROR,
        message="Error fetching healthcare services.",
    )
    HEALTHCARESERVICE_E005 = LogReference(
        level=ERROR,
        message="Error detail: {detail}.",
    )
    CRUD_API_001 = LogReference(
        level=INFO, message="SEARCH TRIAGE CODE is ENABLED,Processing API request."
    )
    CRUD_API_002 = LogReference(
        level=INFO,
        message="SEARCH TRIAGE CODE is DISABLED,Returning 503 for API request.",
    )
    LOCATION_001 = LogReference(
        level=INFO,
        message="Received request to create location with name: {name} and Managing Organisation: {orgID}.",
    )
    LOCATION_002 = LogReference(
        level=INFO,
        message="Successfully created location with ID: {location_id}.",
    )
    LOCATION_003 = LogReference(
        level=INFO,
        message="Location with ID {location_id} found.",
    )
    LOCATION_004 = LogReference(
        level=INFO,
        message="Found {count} locations.",
    )
    LOCATION_005 = LogReference(
        level=INFO,
        message="Creating location with ID {location_id}.",
    )
    LOCATION_006 = LogReference(
        level=INFO,
        message="Getting location with ID {location_id}.",
    )
    LOCATION_007 = LogReference(
        level=INFO,
        message="Retrieving all locations",
    )
    LOCATION_008 = LogReference(
        level=INFO,
        message="Received request to delete location with ID: {location_id}.",
    )
    LOCATION_009 = LogReference(
        level=INFO,
        message="Successfully deleted location with ID: {location_id}.",
    )
    LOCATION_010 = LogReference(
        level=INFO,
        message="Received request to update location with ID: {location_id}.",
    )
    LOCATION_011 = LogReference(
        level=INFO,
        message="Successfully updated location {location_id}.",
    )
    LOCATION_E001 = LogReference(
        level=ERROR,
        message="Location with ID {location_id} not found",
    )
    LOCATION_E002 = LogReference(
        level=ERROR,
        message="No locations found.",
    )
    LOCATION_E003 = LogReference(
        level=Exception,
        message="Error fetching locations: {error_message}.",
    )
