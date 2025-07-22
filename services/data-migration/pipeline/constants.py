from enum import StrEnum


class TargetEnvironment(StrEnum):
    local = "local"
    dev = "dev"
    test = "test"
    int = "int"
    sandpit = "sandpit"
