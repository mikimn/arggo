from dataclasses import field, dataclass
from enum import Enum

import pytest

import arggo
from arggo.dataclass_utils import parser_field


@dataclass
class SimpleArguments:
    just_a_string: str = field(default="Hello")


class GreetingType(Enum):
    NORMAL = 1
    ENGAGING = 2


@dataclass
class ComplexArguments:
    name: str = parser_field(help="The user's name.")
    should_greet: bool = parser_field(help="Whether or not I should greet the user")
    greeting: str = parser_field(
        help="A list of possible greetings", choices=["Hello", "Greetings", "Regards"]
    )
    type: GreetingType = field(default=GreetingType.NORMAL)


class TestSimpleAnnotation:
    def test_function_no_arguments(self):
        @arggo.consume
        def decorated():
            return 1

        assert decorated() == 1

    def test_function_unrelated_arguments(self):
        @arggo.consume
        def decorated(_: SimpleArguments, x: int, y: int):
            return x * y

        assert decorated(5, 6) == 30

    def test_function_multiple_dataclasses(self):
        args = SimpleArguments(just_a_string=", World!")

        @arggo.consume
        def decorated(args1: SimpleArguments, args2: SimpleArguments):
            print("Hello!")
            return args1.just_a_string + args2.just_a_string

        assert decorated(args) == "Hello, World!"

    def test_expected_dataclass_raises_value_error(self):
        @arggo.consume
        def decorated(x: int):
            return x + 5

        with pytest.raises(ValueError):
            decorated()

    def test_dataclass_in_different_index(self):
        @arggo.configure(parser_argument_index=1)
        def decorated(x: int, args: SimpleArguments):
            return f"{args.just_a_string} = {x}"

        assert decorated(5) == "Hello = 5"


class TestConfigureAnnotation:
    # FIXME
    def test_non_zero_argument_index(self):
        # old_sys_argv = sys.argv.copy()
        # sys.argv.clear()

        @arggo.configure(parser_argument_index=1)
        def decorated(s: str, args: SimpleArguments):
            return f"{args.just_a_string}, {s}"

        # assert decorated("World!") == "Hello, World!"
        # sys.argv += old_sys_argv
