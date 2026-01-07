from logging import DEBUG, ERROR, INFO, WARNING

from ftrs_common.logbase import LogBase, LogReference


class ServiceMigrationLogBase(LogBase):
    """
    LogBase for Data Migration ETL Pipeline operations
    """

    SM_APP_001 = LogReference(
        level=DEBUG, message="Starting Service Migration Lambda Application"
    )
    SM_APP_002 = LogReference(
        level=INFO, message="Started Service Migration Application"
    )
    SM_APP_003 = LogReference(level=INFO, message="Handling incoming SQS event")
    SM_APP_004 = LogReference(level=INFO, message="Completed handling of SQS event")
    SM_APP_005 = LogReference(
        level=WARNING,
        message="Some records could not be processed - reporting failures to SQS",
    )
    SM_APP_006 = LogReference(level=INFO, message="Starting to process DMS event")
    SM_APP_007 = LogReference(
        level=INFO, message="Completed processing DMS event in {duration:.3f} seconds"
    )
    SM_APP_008a = LogReference(
        level=WARNING,
        message="A recoverable service migration exception occurred during processing: {error}",
    )
    SM_APP_008b = LogReference(
        level=WARNING,
        message="A non-recoverable service migration exception occurred during processing: {error}",
    )
    SM_APP_009 = LogReference(
        level=ERROR,
        message="An unexpected exception occurred during processing: {error}",
        capture_exception=True,
    )
    SM_APP_010 = LogReference(
        level=ERROR,
        message="Processing of entire batch failed due to: {error}",
        capture_exception=True,
    )
    SM_APP_011 = LogReference(
        level=ERROR,
        message="Failed to parse SQS record: {error}",
        capture_exception=True,
    )

    SM_PROC_001 = LogReference(level=DEBUG, message="Querying legacy service data")
    SM_PROC_002 = LogReference(level=INFO, message="Legacy service data retrieved")
    SM_PROC_003 = LogReference(
        level=DEBUG,
        message="Transformer {transformer_name} does not support service due to: {reason}",
    )
    SM_PROC_004 = LogReference(
        level=DEBUG, message="Transformer {transformer_name} is valid for service"
    )
    SM_PROC_005 = LogReference(
        level=INFO,
        message="Transformer {transformer_name} selected for service",
    )
    SM_PROC_006 = LogReference(
        level=INFO,
        message="Service skipped migration due to reason: {reason}",
    )
    SM_PROC_007 = LogReference(
        level=INFO,
        message="Service successfully transformed and ready for migration",
    )
    SM_PROC_007a = LogReference(
        level=DEBUG,
        message="Service successfully transformed with content",
    )
    SM_PROC_008 = LogReference(
        level=DEBUG, message="Retrieving existing state from DynamoDB"
    )
    SM_PROC_009 = LogReference(
        level=INFO,
        message="No existing state found for service - proceeding with initial migration",
    )
    SM_PROC_010 = LogReference(
        level=INFO,
        message="Existing state found for service - proceeding with incremental migration",
    )

    SM_PROC_011 = LogReference(
        level=DEBUG,
        message="Skipping organisation insert as no organisation data present",
    )
    SM_PROC_012 = LogReference(
        level=INFO,
        message="Added organisation with ID {organisation_id} to migration items",
    )
    SM_PROC_013 = LogReference(
        level=DEBUG,
        message="Skipping location insert as no location data present",
    )
    SM_PROC_014 = LogReference(
        level=INFO,
        message="Added location with ID {location_id} to migration items",
    )
    SM_PROC_015 = LogReference(
        level=DEBUG,
        message="Skipping healthcare service insert as no healthcare service data present",
    )
    SM_PROC_016 = LogReference(
        level=INFO,
        message="Added healthcare service with ID {healthcare_service_id} to migration items",
    )
    SM_PROC_017 = LogReference(
        level=INFO,
        message="Skipping organisation update as no changes detected",
    )
    SM_PROC_018 = LogReference(
        level=INFO,
        message="Organisation changes detected - adding update to migration items",
    )
    SM_PROC_019 = LogReference(
        level=INFO,
        message="Skipping location update as no changes detected",
    )
    SM_PROC_020 = LogReference(
        level=INFO,
        message="Location changes detected - adding update to migration items",
    )
    SM_PROC_021 = LogReference(
        level=INFO,
        message="Skipping healthcare service update as no changes detected",
    )
    SM_PROC_022 = LogReference(
        level=INFO,
        message="Healthcare service changes detected - adding update to migration items",
    )

    SM_PROC_023 = LogReference(
        level=INFO,
        message="Added migration state insert with source record ID {source_record_id} to migration items",
    )
    SM_PROC_024 = LogReference(
        level=INFO,
        message="Added migration state update to version {new_version} with source record ID {source_record_id} to migration items",
    )
    SM_PROC_025 = LogReference(level=INFO, message="No items")
    SM_PROC_026 = LogReference(
        level=INFO, message="Skipping DynamoDB transaction as no items to write"
    )
    SM_PROC_027 = LogReference(
        level=DEBUG, message="Executing DynamoDB transaction with {item_count} items"
    )
    SM_PROC_028 = LogReference(
        level=INFO,
        message="DynamoDB transaction completed successfully",
    )
    SM_PROC_029 = LogReference(
        level=WARNING,
        message="DynamoDB transaction cancelled due to conditional check failure: {error}",
    )
    SM_PROC_030 = LogReference(
        level=ERROR,
        message="DynamoDB transaction failed: {error}",
    )

    SM_VAL_001 = LogReference(
        level=INFO, message="Starting validation of service data using {validator_name}"
    )
    SM_VAL_002 = LogReference(level=INFO, message="Service validation issue identified")
    SM_VAL_003 = LogReference(
        level=INFO, message="Some fields were changed before transformation"
    )

    DM_ETL_001 = LogReference(level=DEBUG, message="Starting to process DMS event")
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

    DM_ETL_014 = LogReference(
        level=WARNING,
        message="Record {record_id} failed validation and was not migrated",
    )
    DM_ETL_015 = LogReference(
        level=INFO,
        message="Address for Organisation ID {organisation} is {address}",
    )
    DM_ETL_016 = LogReference(
        level=WARNING,
        message="No address found for Organisation ID {organisation}, setting address to None",
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
        message="State record found for Service ID {record_id}, Skipping now...",
    )
    DM_ETL_020 = LogReference(
        level=INFO,
        message="No State record found for Service ID {record_id}, Proceeding with creating one...",
    )

    DM_ETL_021 = LogReference(
        level=INFO,
        message="Successfully wrote {item_count} items transactionally for Service ID {record_id}",
    )

    DM_ETL_022 = LogReference(
        level=ERROR,
        message="One or more items exist for  Service ID {record_id}",
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


class ReferenceDataLoadLogBase(LogBase):
    """"""

    RD_APP_001 = LogReference(
        level=DEBUG, message="Starting Reference Data Load Lambda Application"
    )
    RD_APP_002 = LogReference(
        level=INFO, message="Started Reference Data Load Application"
    )

    RD_APP_003 = LogReference(
        level=INFO,
        message="Handling incoming Reference Data Load event of type: {event_type}",
    )
    RD_APP_004 = LogReference(
        level=ERROR,
        message="An unexpected exception occurred during processing: {error}",
        capture_exception=True,
    )

    RD_TC_001 = LogReference(level=INFO, message="Starting triage code load process")
    RD_TC_002 = LogReference(level=INFO, message="Triage code load process completed")

    RD_TC_003 = LogReference(level=DEBUG, message="Loading all Symptom Groups")
    RD_TC_004 = LogReference(
        level=INFO,
        message="Loaded {record_count} Symptom Groups from source database",
    )

    RD_TC_005 = LogReference(level=DEBUG, message="Loading all Symptom Discriminators")
    RD_TC_006 = LogReference(
        level=INFO,
        message="Loaded {record_count} Symptom Discriminators from source database",
    )

    RD_TC_007 = LogReference(level=DEBUG, message="Loading all Dispositions")
    RD_TC_008 = LogReference(
        level=INFO,
        message="Loaded {record_count} Dispositions from source database",
    )

    RD_TC_009 = LogReference(level=DEBUG, message="Reading all SGSD combinations")
    RD_TC_010 = LogReference(
        level=INFO,
        message="Read all SGSD combinations from source database",
    )
    RD_TC_011 = LogReference(level=DEBUG, message="Loading all SGSD combinations")
    RD_TC_012 = LogReference(
        level=INFO,
        message="Loaded {record_count} SGSD combinations from source database",
    )
