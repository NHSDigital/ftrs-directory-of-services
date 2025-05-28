import logging

from typer import Typer

from pipeline.extract import extract
from pipeline.load import load
from pipeline.transform import transform

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

typer_app = Typer(
    name="dos-etl",
    help="DoS Data Migration Pipeline CLI",
)
typer_app.command("load")(load)
typer_app.command("transform")(transform)
typer_app.command("extract")(extract)

