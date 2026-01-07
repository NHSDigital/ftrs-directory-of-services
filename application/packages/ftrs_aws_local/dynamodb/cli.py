import logging

from typer import Typer

from dynamodb.init import init_command
from dynamodb.reset import reset_command

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

typer_app.command("init")(init_command)
typer_app.command("reset")(reset_command)
