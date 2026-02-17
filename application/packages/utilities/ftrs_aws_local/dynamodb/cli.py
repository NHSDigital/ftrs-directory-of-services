import logging

from typer import Typer
from ftrs_aws_local.dynamodb.reset import reset
from ftrs_aws_local.dynamodb.init import init_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

typer_app = Typer(
    name="ftrs-aws-local",
    help="AWS Local CLI for managing local AWS services",
)

typer_app.command("reset")(reset)
typer_app.command("init")(init_tables)
