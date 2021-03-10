
import functools
from dataclasses import is_dataclass
from typing import Any, Callable, Optional, get_type_hints
from .parser import HfArgumentParser

TaskFunction = Callable[[Any], Any]


def argo(
    parser_argument_index=0,
) -> Callable[[TaskFunction], Any]:
    """
    :param config_path: the config path, a directory relative to the declaring python file.
    :param config_name: the name of the config (usually the file name without the .yaml extension)
    """

    def main_decorator(task_function: TaskFunction) -> Callable[[], None]:
        @functools.wraps(task_function)
        def decorated_main(args_passthrough: Optional[Any] = None) -> Any:
            if args_passthrough is not None:
                return task_function(args_passthrough)
            else:
                type_hints = list(get_type_hints(task_function).items())
                parser_argument_name, parser_argument_type_hint = type_hints[parser_argument_index]
                assert is_dataclass(parser_argument_type_hint)

                parser = HfArgumentParser(parser_argument_type_hint)
                args = parser.parse_args()
                task_function(args)

        return decorated_main

    return main_decorator
