import json
import subprocess
import sys
from abc import ABC, abstractmethod
from argparse import Namespace
from dataclasses import is_dataclass, asdict
from os.path import join, abspath, isdir, exists
from typing import List

from arggo.parser import dataclass_to_json, DataClassType
from arggo.plugin import Plugin

_PARAMETERS_FILE_NAME = "parameters.json"
_METADATA_KEY = "__arggo"


class Experiment(ABC):
    @property
    @abstractmethod
    def parameters(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def stripped_parameters(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def meta_parameters(self):
        raise NotImplementedError()

    def to_json(self, plugins: List[Plugin]):
        meta_params = self.meta_parameters
        for plugin in plugins:
            dump = plugin.parameters_dump()
            if dump is not None:
                meta_params[plugin.name] = dump
        return dataclass_to_json(self.stripped_parameters, {_METADATA_KEY: meta_params})


class NewExperiment(Experiment):
    def __init__(self, args: DataClassType, reproduced_from_path=None):
        if args is None:
            raise ValueError("args cannot be None")
        if not is_dataclass(args):
            raise ValueError(
                f"args must be a dataclass object, but got {args.__class__.__name__}, "
                f"which is not a dataclass."
            )
        self._args = args
        self._reproduced_from_path = reproduced_from_path

    @property
    def parameters(self):
        return {**asdict(self._args), _METADATA_KEY: self.meta_parameters}

    @property
    def stripped_parameters(self):
        return self._args

    @property
    def meta_parameters(self):
        additional_metadata = dict()
        if self._reproduced_from_path is not None:
            additional_metadata["reproduced_from"] = abspath(self._reproduced_from_path)
        additional_metadata["executable"] = sys.executable
        additional_metadata["command"] = " ".join(sys.argv)
        additional_metadata["script"] = sys.argv[0]
        return additional_metadata

    def save_json(self, base_dir: str, plugins: List[Plugin]):
        parameters_file_path = join(base_dir, _PARAMETERS_FILE_NAME)
        with open(parameters_file_path, "w") as f:
            f.write(self.to_json(plugins))

    @classmethod
    def from_reproduced(cls, parser, reproduced_from_dir):
        reproduce_from_file = _try_discover_parameters_file(reproduced_from_dir)
        (args,) = parser.parse_json_file(reproduce_from_file)[:1]
        return NewExperiment(args, reproduce_from_file)

    @classmethod
    def from_arguments(cls, parser, args=None):
        (parsed_args,) = parser.parse_args_into_dataclasses(
            args=args, return_remaining_strings=True
        )[:1]
        return NewExperiment(parsed_args)


def _try_discover_parameters_file(path: str):
    if isdir(path):
        file_name = _PARAMETERS_FILE_NAME
        if exists(join(path, file_name)):
            return join(path, file_name)
        raise FileNotFoundError(
            f"Could not find a {file_name} file in {path}. Make sure this is a valid directory."
        )
    if exists(path):
        return path
    raise FileNotFoundError(f"Parameters file {path} does not exist")


class FinishedExperiment(Experiment):
    def __init__(self, base_dir):
        if base_dir is None:
            raise ValueError(
                "base_dir must not be None, as this must be an existing experiment"
            )
        self._base_dir = base_dir
        self._parameters = None

    def _parameters_file_path(self):
        return join(self._base_dir, "parameters.json")

    @property
    def parameters(self):
        if self._parameters is None:
            with open(self._parameters_file_path()) as f:
                self._parameters = json.load(f)
        return self._parameters

    @property
    def stripped_parameters(self):
        p = dict(self.parameters)
        del p[_METADATA_KEY]
        return Namespace(**p)

    @property
    def meta_parameters(self):
        return self.parameters[_METADATA_KEY]

    def reproduce(self):
        print(f"Reproducing from {self._base_dir}")
        executable = self.meta_parameters["executable"]
        command = self.meta_parameters["script"]
        subprocess.run([executable, command, "--arggo_reproduce", self._base_dir])
