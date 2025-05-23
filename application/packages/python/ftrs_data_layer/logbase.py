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

class ETLPipelineLogBase(LogBase):
    """
    LogBase for ETL Pipeline operations
    """
    ETL_EXTRACT_001 = LogReference(level=INFO, message="Extracting data to {output_path}")
    ETL_EXTRACT_002 = LogReference(level=INFO, message="Percentage of service profiles: {service_profiles_percentage}%")
    ETL_EXTRACT_003 = LogReference(level=INFO, message="Percentage of all data fields: {data_fields_percentage}%")
    ETL_EXTRACT_004 = LogReference(level=INFO, message="Data extraction completed successfully.")

    ETL_TRANSFORM_001 = LogReference(level=INFO, message="Transforming data from {input_path} to {output_path}")
    ETL_TRANSFORM_002 = LogReference(level=INFO, message="Transform completed successfully.")

    ETL_LOAD_001 = LogReference(level=INFO, message="Loading {len_input_df} {table_value}s into {table_value}")
    ETL_LOAD_002 = LogReference(level=INFO, message="Loaded {count} {table_value}s into the database.")
    ETL_LOAD_003 = LogReference(level=INFO, message="Data loaded successfully into {env_value} environment, workspace: {workspace_value}")

    ETL_RESET_001 = LogReference(level=INFO, message="Initializing tables...")
    ETL_RESET_002 = LogReference(level=ERROR, message="The init option is only supported for the local environment.")
    ETL_RESET_003 = LogReference(level=INFO, message="Table {table_name} created successfully.")
    ETL_RESET_004 = LogReference(level=INFO, message="Table {table_name} already exists.")
    ETL_RESET_005 = LogReference(level=ERROR, message="Invalid environment: {env}. Only 'dev' and 'local' are allowed.")
    ETL_RESET_006 = LogReference(level=INFO, message="Deleted {count} items from {table_name}")
    ETL_RESET_007 = LogReference(level=ERROR, message="Unsupported entity type: {entity_type}")

class UtilsLogBase(LogBase):
    """
    LogBase for utils operations
    """
    UTILS_FILEIO_001 = LogReference(level=INFO, message="Reading from S3 path: {file_path}")
    UTILS_FILEIO_002 = LogReference(level=INFO, message="Reading from local file path: {file_path}")
    UTILS_FILEIO_003 = LogReference(level=ERROR, message="Unsupported path type: {path_type}")
    UTILS_FILEIO_004 = LogReference(level=INFO, message="Writing to S3 path: {file_path}")
    UTILS_FILEIO_005 = LogReference(level=INFO, message="Writing to local file path: {file_path}")
    UTILS_FILEIO_006 = LogReference(level=ERROR, message="Unsupported path type: {path_type}")

    UTILS_SECRET_001 = LogReference(level=ERROR, message="The environment or project name does not exist")

    UTILS_VALIDATOR_001 = LogReference(level=INFO, message="Bucket {bucket_name} exists and is accessible.")
    UTILS_VALIDATOR_002 = LogReference(level=WARNING, message="Error checking bucket {bucket_name}: {e}")
    UTILS_VALIDATOR_003 = LogReference(level=INFO, message="Object {object_key} exists in bucket {bucket_name}.")
    UTILS_VALIDATOR_004 = LogReference(level=WARNING, message="Error checking object {object_key} in bucket {bucket_name}: {e}")
    UTILS_VALIDATOR_005 = LogReference(level=ERROR, message="Invalid S3 URI: {s3_uri}. Please provide a valid S3 URI and confirm you have access to the S3 bucket.")
    UTILS_VALIDATOR_006 = LogReference(level=ERROR, message="File does not exist in S3: {s3_uri}. Please provide a valid S3 URI to an existing file.")
    UTILS_VALIDATOR_007 = LogReference(level=ERROR, message="File already exists in S3: {s3_uri}. Please provide a different S3 URI.")
    UTILS_VALIDATOR_008 = LogReference(level=ERROR, message="Parent directory does not exist: {parsed_path_parent}. Please provide a valid path to a file.")
    UTILS_VALIDATOR_009 = LogReference(level=ERROR, message="File does not exist: {parsed_path}. Please provide a valid path to a file.")
    UTILS_VALIDATOR_010 = LogReference(level=ERROR, message="File already exists: {parsed_path}. Please provide a different path.")

