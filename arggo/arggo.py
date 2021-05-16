import argparse
import functools
import json
import os
from argparse import ArgumentParser, Namespace
from dataclasses import is_dataclass
from os.path import join
from typing import Any, Callable, Optional, get_type_hints, Union, Text, Sequence

from .logger import bind_logger_to_stdout, bind_logger_to_stderr
from .parser import DataClassArgumentParser, dataclass_to_json

TaskFunction = Callable[[Any], Any]


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


def _init_logging_directory(logging_dir: str, init_working_dir: bool):
    if init_working_dir:
        from .utils import working_dir_init

        output_dir, original_working_dir = working_dir_init(logging_dir=logging_dir)
    else:
        original_working_dir = os.getcwd()
        output_dir = join(original_working_dir, logging_dir)
        os.makedirs(output_dir, exist_ok=True)

    return output_dir, original_working_dir


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
            if args_passthrough is not None:
                return task_function(args_passthrough)

            type_hints = list(get_type_hints(task_function).items())
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

            # Working directories
            # output_dir, original_working_dir = _init_logging_directory(logging_dir, init_working_dir)

            parser = DataClassArgumentParser(parser_argument_type_hint)
            meta_parser = argparse.ArgumentParser(add_help=False)

            meta_parser.add_argument("--arggo_help", action=_MetaHelpAction, nargs=0)
            meta_parser.add_argument(
                "--arggo_parameters_file",
                type=str,
                required=False,
                default=None,
                help="Use this argument to load a previously saved configuration directly from a JSON file.",
            )
            (meta_args,) = meta_parser.parse_known_args()[:1]
            if meta_args and meta_args.arggo_parameters_file is not None:
                json_file_path = meta_args.arggo_parameters_file
                if not os.path.exists(json_file_path):
                    raise FileNotFoundError(
                        f"Parameters file {json_file_path} does not exist."
                    )
                (args,) = parser.parse_json_file(json_file_path)[:1]
            else:
                (args,) = parser.parse_args_into_dataclasses()[:1]

            output_dir, original_working_dir = _init_logging_directory(
                logging_dir, init_working_dir
            )

            # Save output
            if log_to_file:
                # TODO Make configurable
                output_file_name = "output.log"
                output_file_path = join(output_dir, output_file_name)
                bind_logger_to_stdout(output_file_path)

                # output_file_name = "output.err"
                # output_file_path = join(output_dir, output_file_name)
                # bind_logger_to_stderr(output_file_path)

            # Save parameters
            if save_parameters:
                # TODO Make configurable
                parameters_file_name = "parameters.json"
                parameters_file_path = join(output_dir, parameters_file_name)
                with open(parameters_file_path, "w") as f:
                    f.write(dataclass_to_json(args))

            task_function(args)

        return decorated_main

    return main_decorator
