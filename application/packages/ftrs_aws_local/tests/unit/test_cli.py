from typer import Typer

from dynamodb.cli import typer_app


def test_typer_app_init() -> None:
    """
    Test the initialization of the Typer app.
    """
    expected_commands = ["reset", "init"]

    assert isinstance(typer_app, Typer)
    assert typer_app.info.name == "ftrs-aws-local"
    assert typer_app.info.help == "AWS Local CLI for managing local AWS services"
    assert len(typer_app.registered_commands) == len(expected_commands)

    assert all(
        command.name in expected_commands for command in typer_app.registered_commands
    )
