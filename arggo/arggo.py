import functools
from dataclasses import is_dataclass
from typing import Any, Callable, Optional, get_type_hints
from .parser import DataClassArgumentParser

TaskFunction = Callable[[Any], Any]


def arggo(
    parser_argument_index=0,
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

            parser = DataClassArgumentParser(parser_argument_type_hint)
            (args,) = parser.parse_args_into_dataclasses()
            task_function(args)

        return decorated_main

    return main_decorator
