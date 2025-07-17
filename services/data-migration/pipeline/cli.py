import logging

from typer import Typer

from pipeline.recordlevel import local_handler

typer_app = Typer(
    name="dos-etl",
    help="DoS Data Migration Pipeline CLI",
)
typer_app.command("migrate")(local_handler)
