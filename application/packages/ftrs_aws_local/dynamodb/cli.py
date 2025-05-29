import logging

from typer import Typer

from dynamodb.reset import reset

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

typer_app.command("start")(lambda: logging.info("Starting AWS Local services"))
typer_app.command("reset")(reset)
