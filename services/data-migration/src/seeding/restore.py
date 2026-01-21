import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import batched
from multiprocessing import cpu_count
from time import sleep
from typing import Generator

import awswrangler as wr
import boto3
import rich
from aws_lambda_powertools.utilities.parameters import get_parameter
from botocore.config import Config
from botocore.exceptions import ClientError
from ftrs_common.utils.db_service import format_table_name

CONSOLE = rich.get_console()
DDB_CLIENT = boto3.client(
    "dynamodb",
    config=Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 5}),
)


def iter_batches(
    items: list[dict],
    batch_size: int = 25,
) -> Generator[list[str], None, None]:
    for batch in batched(items, batch_size):
        yield [json.loads(item)["Item"] for item in batch]


def write_item_batch(
    table_name: str,
    batch: list[dict],
    backoff: int = 1,
    initial_start_time: float | None = None,
) -> None:
    """
    Write a batch of items to a DynamoDB table
    """

    try:
        start_time = initial_start_time or time.monotonic()
        DDB_CLIENT.transact_write_items(
            TransactItems=[
                {"Put": {"TableName": table_name, "Item": item}} for item in batch
            ]
        )
        elapsed_time = time.monotonic() - start_time

        CONSOLE.print(
            f"Written {len(batch)} items to [bright_blue]{table_name}[/bright_blue] in {elapsed_time:.2f} seconds",
            style="bright_black",
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "ThrottlingException":
            CONSOLE.print(
                f"Table {table_name} is being throttled. Waiting for {backoff} seconds...",
                style="yellow",
            )
            sleep(backoff)
            return write_item_batch(table_name, batch, backoff * 2, start_time)

        elif e.response["Error"]["Code"] == "ReadTimeoutError":
            CONSOLE.print(
                f"Read timeout occurred when writing to [bright_blue]{table_name}[/bright_blue]. Retrying after {backoff} seconds...",
                style="yellow",
            )
            sleep(backoff)
            return write_item_batch(table_name, batch, backoff * 2, start_time)

        CONSOLE.print(
            f"Error writing items to [bright_blue]{table_name}[/bright_blue]: {e}",
            style="bright_red",
        )

    except Exception as e:
        CONSOLE.print(
            f"Error writing items to [bright_blue]{table_name}[/bright_blue]: {e}",
            style="bright_red",
        )


def existing_items_in_table(table_name: str) -> bool:
    """
    Check if a DynamoDB table has existing items
    """
    try:
        response = DDB_CLIENT.scan(
            TableName=table_name,
            Select="COUNT",
            Limit=1,
        )
        return response.get("Count", 0) > 0

    except ClientError as e:
        CONSOLE.print(
            f"Error checking items in [bright_blue]{table_name}[/bright_blue]: {e}",
            style="bright_red",
        )
        return False


async def bulk_load_table(table_name: str, items: list[dict]) -> None:
    """
    Bulk load items into a DynamoDB table
    """
    workers = cpu_count() * 2
    CONSOLE.print(
        f"Bulk loading {len(items)} items into table [bright_blue]{table_name}[/bright_blue] using {workers} workers"
    )
    loop = asyncio.get_running_loop()

    if existing_items_in_table(table_name):
        CONSOLE.print(
            f"Table [bright_blue]{table_name}[/bright_blue] already has data. Skipping bulk load.",
            style="yellow",
        )
        return

    with ThreadPoolExecutor(max_workers=workers) as executor:
        tasks = []
        for batch in iter_batches(items):
            tasks.append(
                loop.run_in_executor(executor, write_item_batch, table_name, batch)
            )

        for done in asyncio.as_completed(tasks):
            await done

    CONSOLE.print(
        f"Successfully written {len(items)} items to [bright_blue]{table_name}[/bright_blue]",
        style="green",
    )


async def run_s3_restore(env: str, workspace: str | None) -> None:
    """
    Run the actual S3 restore process (async)
    """
    CONSOLE.print(
        f"Restoring data from S3 for environment [bright_blue]{env}[/bright_blue] and workspace [bright_blue]{workspace}[/bright_blue]"
    )

    CONSOLE.print("Downloading backup files from S3", style="bright_black")
    backup_uris = get_parameter(
        name=f"/ftrs-dos/{env}/dynamodb-backup-arns",
        transform="json",
    )
    data = {
        entity_type: wr.s3.read_parquet(path=path)
        for entity_type, path in backup_uris.items()
    }

    CONSOLE.print("Restoring data to DynamoDB", style="bright_black")
    tasks = [
        bulk_load_table(
            format_table_name(
                entity_type,
                env,
                workspace,
                stack_name=get_stack_name(entity_type),
            ),
            df["data"].tolist(),
        )
        for entity_type, df in data.items()
    ]

    await asyncio.gather(*tasks)

    CONSOLE.print(
        f"Data restoration complete to [bright_blue]{env}[/bright_blue] and workspace [bright_blue]{workspace}[/bright_blue]",
        style="bright_green",
    )


def get_stack_name(entity_type: str) -> str:
    """
    Get the stack name based on the entity type
    """
    return "data-migration" if entity_type == "state-table" else "database"
