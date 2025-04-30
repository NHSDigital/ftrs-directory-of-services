import logging

from processor import extract
from typer import Typer

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
