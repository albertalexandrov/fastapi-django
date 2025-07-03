import os
from enum import StrEnum


class EnvironmentEnum(StrEnum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    STAGE = "STAGE"
    PROD = "PROD"

    @classmethod
    def get_environment(cls):
        return cls(os.environ.get("ENVIRONMENT", "LOCAL"))
