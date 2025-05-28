from typer import Typer

from dynamodb.cli import typer_app


def test_typer_app_init() -> None:
    """
    Test the initialization of the Typer app.
    """
    expected_command_count = 2

    assert isinstance(typer_app, Typer)
    assert typer_app.info.name == "ftrs-aws-local"
    assert typer_app.info.help == "AWS Local CLI for managing local AWS services"
    assert len(typer_app.registered_commands) == expected_command_count

    assert all(
        command.name in ["start", "reset"]
        for command in typer_app.registered_commands
    )
