import logging

from typer import Typer

from processor import extract

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

typer_app = Typer(
    name="dos-etl",
    help="DoS ODS extraction pipeline",
)
typer_app.command("extract")(extract)
