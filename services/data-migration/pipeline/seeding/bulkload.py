import asyncio
import json
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import batched
from multiprocessing import cpu_count
from time import sleep
from typing import Generator

import boto3
import rich
from botocore.config import Config
from botocore.exceptions import ClientError

CONSOLE = rich.get_console()

DDB_CLIENT = boto3.client(
    "dynamodb",
    config=Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 5}),
)


def iter_batches(
    items: list[dict],
    batch_size: int = 25,
) -> Generator[list[dict], None, None]:
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

        CONSOLE.log(
            f"Written {len(batch)} items to [bright_blue]{table_name}[/bright_blue] in {elapsed_time:.2f} seconds",
            style="bright_black",
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "ThrottlingException":
            CONSOLE.log(
                f"Table {table_name} is being throttled. Waiting for {backoff} seconds...",
                style="yellow",
            )
            sleep(backoff)
            return write_item_batch(table_name, batch, backoff * 2, start_time)

        raise

    except Exception as e:
        CONSOLE.log(
            f"Error writing items to [bright_blue]{table_name}[/bright_blue]: {e}",
            style="bright_red",
        )


async def bulk_load_table(table_name: str, items: list[dict]) -> None:
    """ """
    workers = cpu_count() * 2
    CONSOLE.log(
        f"Bulk loading {len(items)} items into table [bright_blue]{table_name}[/bright_blue] using {workers} workers"
    )
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor(max_workers=workers) as executor:
        tasks = []
        for batch in iter_batches(items):
            tasks.append(
                loop.run_in_executor(executor, write_item_batch, table_name, batch)
            )

        for done in asyncio.as_completed(tasks):
            await done

    CONSOLE.log(
        f"Successfully written {len(items)} items to [bright_blue]{table_name}[/bright_blue]",
        style="green",
    )
