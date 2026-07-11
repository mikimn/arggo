from dataclasses import dataclass, field

import pytest

from arggo.core import _check_reserved_arguments
from arggo.exceptions import ArggoReservedError


@dataclass
class ReservedArguments:
    arggo_interactive: bool = field(default=False)


@dataclass
class UnreservedArguments:
    name: str = field(default="World")


class TestCheckReservedArguments:
    def test_raises_on_reserved_field_name(self):
        with pytest.raises(ArggoReservedError):
            _check_reserved_arguments(
                ReservedArguments, override_reserved_arguments=False
            )

    def test_override_bypasses_check(self):
        _check_reserved_arguments(ReservedArguments, override_reserved_arguments=True)

    def test_unreserved_field_name_passes(self):
        _check_reserved_arguments(
            UnreservedArguments, override_reserved_arguments=False
        )
