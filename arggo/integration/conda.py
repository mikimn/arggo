# Integration utilities for Anaconda/Miniconda
import os
from dataclasses import dataclass, asdict
from typing import Union, Dict, Any

from arggo.plugin import Plugin


def is_under_conda():
    return "CONDA_DEFAULT_ENV" in os.environ


@dataclass
class Environment:
    name: str
    prefix: str


def conda_environment() -> Union[Environment, None]:
    if not is_under_conda():
        return None
    return Environment(
        name=os.environ.get("CONDA_DEFAULT_ENV"),
        prefix=os.environ.get("CONDA_PREFIX", None),
    )


class CondaPlugin(Plugin):
    @property
    def name(self):
        return "conda"

    def parameters_dump(self) -> Union[Dict[str, Any], None]:
        if not is_under_conda():
            return None
        return asdict(conda_environment())
