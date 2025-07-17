from typer import Typer

from pipeline.cli import typer_app


def test_typer_app_init() -> None:
    """
    Test the initialization of the Typer app.
    """
    expected_command_count = 1

    assert isinstance(typer_app, Typer)
    assert typer_app.info.name == "dos-etl"
    assert typer_app.info.help == "DoS Data Migration Pipeline CLI"
    assert len(typer_app.registered_commands) == expected_command_count

    assert all(command.name in ["migrate"] for command in typer_app.registered_commands)
