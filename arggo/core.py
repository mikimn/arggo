import argparse
import functools
import os
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import fields, is_dataclass
from os.path import join
from typing import Any, Callable, Optional, get_type_hints, Union, Text, Sequence, List
from rich.console import Console

console = Console()

from .experiment import NewExperiment
from .exceptions import ArggoAlreadyConfiguredError, ArggoReservedError
from . import integration  # noqa: F401 - importing registers the built-in plugins
from .plugin import Plugin

if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
    from typing import Protocol
else:
    from typing_extensions import Protocol

from ._internal.global_store import GlobalStore
from .environment.workdir import Workdir
from .logger import FileLogger
from .parser import DataClassArgumentParser
from interactive_argparse import InteractiveArgumentParser

_OUTPUT_FILE_NAME = "output.log"


global_store = GlobalStore()


class TaskFunction(Protocol):
    def __call__(self, a: Any, b: Any, **kwargs) -> Any:
        ...


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


def _init_work_directory(
    logging_dir: str, tag: str = None, init_working_dir: bool = True
) -> Workdir:
    from .environment.workdir import get_workdir

    workdir = get_workdir()
    if init_working_dir:
        logging_dir = logging_dir if tag is None else join(logging_dir, tag)
        workdir.initialize(logging_dir)
    else:
        output_dir = join(workdir.workdir(), logging_dir)
        os.makedirs(output_dir, exist_ok=True)

    return workdir


def _init_logging_to_file(output_dir: str, output_file_name: str = _OUTPUT_FILE_NAME):
    output_file_path = join(output_dir, output_file_name)
    file_logger = FileLogger(global_store, output_file_path)
    file_logger.bind()


def _add_meta_arguments(meta_parser: ArgumentParser) -> None:
    meta_parser.add_argument("--arggo_help", action=_MetaHelpAction, nargs=0)
    meta_parser.add_argument(
        "--arggo_interactive",
        action="store_true",
        help="Use this meta-argument to accept program arguments in an interactive mode",
    )
    meta_parser.add_argument(
        "--arggo_reproduce",
        type=str,
        required=False,
        default=None,
        help=f"Use this argument to reproduce a configuration from a previously saved run. Must be either "
        f"a directory containing a parameters file, or a path to such a file",
    )
    for plugin_cls in Plugin.registry:
        plugin_cls.add_meta_arguments(meta_parser)


def _build_meta_parser() -> ArgumentParser:
    meta_parser = ArgumentParser(add_help=False)
    _add_meta_arguments(meta_parser)
    return meta_parser


def _meta_arguments():
    (meta_args,) = _build_meta_parser().parse_known_args()[:1]
    return meta_args


def _reserved_argument_names() -> Sequence[str]:
    return [
        action.dest for action in _build_meta_parser()._actions if action.dest != "help"
    ]


def _check_reserved_arguments(dtype, override_reserved_arguments: bool) -> None:
    if override_reserved_arguments:
        return
    reserved_names = _reserved_argument_names()
    for f in fields(dtype):
        if f.name in reserved_names:
            raise ArggoReservedError(
                f"Error: Argument --{f.name} is reserved by Arggo. Please either rename it or set "
                f"@arggo.configure(override_reserved_arguments=True) when initializing. "
                f"Reserved argument names: {', '.join(sorted(reserved_names))}"
            )


def _check_not_already_configured(task_function: TaskFunction) -> None:
    configured_by = global_store.get("configured_by", None)
    if configured_by is not None and configured_by is not task_function:
        raise ArggoAlreadyConfiguredError(
            f"Error: Arggo has already been configured by a different entry point "
            f"({configured_by.__qualname__}) in this process. consume()/configure() "
            f"perform a one-time, process-wide setup: call the same decorated function "
            f"repeatedly (e.g. in a loop) rather than decorating more than one entry point."
        )


def _load_default_plugins():
    return [plugin_cls() for plugin_cls in Plugin.registry]


def _main_annotation(
    parser_argument_index=0,
    logging_dir="logs",
    init_working_dir=True,
    plugins: List[Plugin] = None,
    override_reserved_arguments: bool = False,
) -> Callable[[Any], Any]:
    """Decorate a main method with this decorator to enable Arggo

    :param parser_argument_index: The index of the argument which will be our dataclass (default: 0). This is useful
    when the main method receives more than one argument in a non-standard ordering.
    :param override_reserved_arguments: By default, a dataclass field whose name collides with one of Arggo's
    reserved meta-argument names (e.g. arggo_interactive) raises ArggoReservedError. Set this to True to allow
    the collision instead.
    """
    if plugins is None:
        plugins = []
    # Default plugins
    for default_plugin in _load_default_plugins():
        if default_plugin not in plugins:
            plugins.append(default_plugin)

    def main_decorator(task_function: TaskFunction) -> Callable[[], None]:
        @functools.wraps(task_function)
        def decorated_main(*args_passed, **kwargs_passed) -> Any:
            type_hints = list(get_type_hints(task_function).items())
            if len(type_hints) == 0:
                return task_function(*args_passed, **kwargs_passed)

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

            _check_not_already_configured(task_function)

            meta_args = _meta_arguments()
            parser = global_store.get("parser", None)
            update_parser = False
            # TODO Proper caching
            if not parser:
                _check_reserved_arguments(
                    parser_argument_type_hint, override_reserved_arguments
                )
                parser = DataClassArgumentParser(parser_argument_type_hint)
                update_parser = True

                if meta_args and meta_args.arggo_interactive:
                    console.print(
                        "[bold cyan] Running with interactive mode [/bold cyan]"
                    )
                    parser = InteractiveArgumentParser(parser)

            if update_parser:
                global_store.put("parser", parser)
                global_store.put("configured_by", task_function)

                if meta_args and meta_args.arggo_reproduce is not None:
                    experiment = NewExperiment.from_reproduced(
                        parser, meta_args.arggo_reproduce
                    )
                else:
                    # `InteractiveArgumentParser` only prompts when it sees no left-over
                    # CLI args of its own; arggo's `--arggo_interactive` meta-flag would
                    # otherwise count as one, so force it to treat the call as bare.
                    interactive_args = (
                        [] if meta_args and meta_args.arggo_interactive else None
                    )
                    experiment = NewExperiment.from_arguments(
                        parser, args=interactive_args
                    )
                global_store.put("experiment", experiment)
            else:
                experiment = global_store.get("experiment")

            workdir = _init_work_directory(logging_dir, None, init_working_dir)
            output_dir = workdir.workdir()

            # Save output
            if log_to_file:
                _init_logging_to_file(output_dir)

            # Save parameters
            if save_parameters:
                experiment.save_json(output_dir, plugins)

            new_args_passed = [
                *args_passed[:parser_argument_index],
                experiment.stripped_parameters,
                *args_passed[parser_argument_index:],
            ]
            return task_function(*new_args_passed, **kwargs_passed)

        return decorated_main

    return main_decorator


configure = _main_annotation
consume = _main_annotation()
