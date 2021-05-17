import argparse
import functools
import os
from argparse import ArgumentParser, Namespace
from dataclasses import is_dataclass
from os.path import join, abspath
from typing import Any, Callable, Optional, get_type_hints, Union, Text, Sequence

from ._internal.global_store import GlobalStore
from .environment.workdir import Workdir
from .logger import bind_logger_to_stdout
from .parser import DataClassArgumentParser, dataclass_to_json

_PARAMETERS_FILE_NAME = "parameters.json"
_OUTPUT_FILE_NAME = "output.log"
_METADATA_KEY = "__arggo"

TaskFunction = Union[Callable[[Any], Any], Callable[[], Any]]


class _MetaHelpAction(argparse.Action):
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = ...,
    ) -> None:
        parser.print_help()
        parser.exit()


def _init_work_directory(logging_dir: str, init_working_dir: bool) -> Workdir:
    from .environment.workdir import Workdir

    workdir = Workdir(GlobalStore())
    if init_working_dir:
        workdir.initialize(logging_dir)
    else:
        output_dir = join(workdir.workdir(), logging_dir)
        os.makedirs(output_dir, exist_ok=True)

    return workdir


def _try_discover_parameters_file(path: str):
    if os.path.isdir(path):
        file_name = _PARAMETERS_FILE_NAME
        if os.path.exists(join(path, file_name)):
            return join(path, file_name)
        raise FileNotFoundError(
            f"Could not find a {file_name} file in {path}. Make sure this is a valid directory."
        )
    if os.path.exists(path):
        return path
    raise FileNotFoundError(f"Parameters file {path} does not exist")


def arggo(
    parser_argument_index=0, logging_dir="logs", init_working_dir=True
) -> Callable[[Any], Any]:
    """Decorate a main method with this decorator to enable Arggo

    :param parser_argument_index: The index of the argument which will be our dataclass (default: 0). This is useful
    when the main method receives more than one argument in a non-standard ordering.
    """

    def main_decorator(task_function: TaskFunction) -> Callable[[], None]:
        @functools.wraps(task_function)
        def decorated_main(args_passthrough: Optional[Any] = None) -> Any:
            type_hints = list(get_type_hints(task_function).items())
            if args_passthrough is not None:
                return task_function(args_passthrough)

            if len(type_hints) == 0:
                return task_function()

            parser_argument_name, parser_argument_type_hint = type_hints[
                parser_argument_index
            ]
            if not is_dataclass(parser_argument_type_hint):
                raise ValueError(
                    f"Function argument {parser_argument_name} "
                    f"declared type {parser_argument_type_hint} "
                    f"but {parser_argument_type_hint} is not a dataclass."
                )

            save_parameters = True
            log_to_file = True

            parser = DataClassArgumentParser(parser_argument_type_hint)
            meta_parser = argparse.ArgumentParser(add_help=False)

            meta_parser.add_argument("--arggo_help", action=_MetaHelpAction, nargs=0)
            meta_parser.add_argument(
                "--arggo_reproduce",
                type=str,
                required=False,
                default=None,
                help=f"Use this argument to reproduce a configuration from a previously saved run. Must be either "
                f"a directory containing a {_PARAMETERS_FILE_NAME} file, or a path to such a file",
            )
            (meta_args,) = meta_parser.parse_known_args()[:1]
            reproduce_from_file = None
            if meta_args and meta_args.arggo_reproduce is not None:
                reproduce_from_file = _try_discover_parameters_file(
                    meta_args.arggo_reproduce
                )
                (args,) = parser.parse_json_file(reproduce_from_file)[:1]
            else:
                (args,) = parser.parse_args_into_dataclasses()[:1]

            workdir = _init_work_directory(logging_dir, init_working_dir)
            output_dir = workdir.workdir()

            # Save output
            if log_to_file:
                # TODO Make configurable
                output_file_name = _OUTPUT_FILE_NAME
                output_file_path = join(output_dir, output_file_name)
                bind_logger_to_stdout(output_file_path)

                # output_file_name = "output.err"
                # output_file_path = join(output_dir, output_file_name)
                # bind_logger_to_stderr(output_file_path)

            # Save parameters
            if save_parameters:
                # TODO Make configurable
                parameters_file_name = _PARAMETERS_FILE_NAME
                parameters_file_path = join(output_dir, parameters_file_name)
                additional_metadata = dict()
                if reproduce_from_file is not None:
                    additional_metadata["reproduced_from"] = abspath(
                        reproduce_from_file
                    )
                with open(parameters_file_path, "w") as f:
                    f.write(
                        dataclass_to_json(args, {_METADATA_KEY: additional_metadata})
                    )

            task_function(args)

        return decorated_main

    return main_decorator
