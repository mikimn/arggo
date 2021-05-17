import sys
from dataclasses import field, dataclass

from arggo import arggo


@dataclass
class Arguments:
    just_a_string: str = field(default="Hello")


class TestMainAnnotation:
    def test_function_no_arguments(self):
        @arggo()
        def decorated():
            return 1

        assert decorated() == 1

    def test_non_zero_argument_index(self):
        # old_sys_argv = sys.argv.copy()
        # sys.argv.clear()

        @arggo(1)
        def decorated(s: str, args: Arguments):
            return f"{args.just_a_string}, {s}"

        # assert decorated("World!") == "Hello, World!"
        # sys.argv += old_sys_argv
