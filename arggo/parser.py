# Copyright 2020 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import dataclasses
import json
import sys
from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    ArgumentError,
)
from enum import Enum
from gettext import gettext as _
from pathlib import Path
from typing import Any, Iterable, List, NewType, Optional, Tuple, Union, Dict, Type

from arggo.types import EnumEncoder

DataClass = NewType("DataClass", Any)
DataClassType = NewType("DataClassType", Any)


# From https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def string_to_bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ArgumentTypeError(
            f"Truthy value expected: got {v} but expected one of yes/no, true/false, t/f, y/n, 1/0 (case insensitive)."
        )


def _handle_kwargs_bool(field, kwargs):
    kwargs["type"] = string_to_bool
    if field.type is bool or (
        field.default is not None and field.default is not dataclasses.MISSING
    ):
        # Default value is True if we have no default when of type bool.
        default = True if field.default is dataclasses.MISSING else field.default
        # This is the value that will get picked if we don't include --field_name in any way
        kwargs["default"] = default
        # This tells argparse we accept 0 or 1 value after --field_name
        kwargs["nargs"] = "?"
        # This is the value that will get picked if we do --field_name (without value)
        kwargs["const"] = True
    return kwargs


def _handle_kwargs_list(field, kwargs):
    # Handle Generic list types
    kwargs["nargs"] = "+"
    kwargs["type"] = field.type.__args__[0]
    assert all(
        x == kwargs["type"] for x in field.type.__args__
    ), "{} cannot be a List of mixed types".format(field.name)
    if field.default_factory is not dataclasses.MISSING:
        kwargs["default"] = field.default_factory()
    return kwargs


def _handle_kwargs_enum(field, kwargs):
    def parse_argument(arg):
        assert isinstance(arg, str)
        arg = arg.lower()
        enum_types = {
            **{
                enum_type.name.lower(): enum_type.value
                for enum_type in list(field.type)
            },
            **{str(enum_type.value): enum_type.value for enum_type in list(field.type)},
        }
        if arg in enum_types:
            return field.type(enum_types[arg.lower()])
        else:
            msg = "invalid choice: {} (choose from {})"
            choices = ", ".join(sorted(repr(choice) for choice in enum_types.keys()))
            raise ArgumentTypeError(msg.format(arg, choices))

    kwargs["type"] = parse_argument
    kwargs["choices"] = [x.value for x in field.type] + [
        x.name.lower() for x in field.type
    ]
    if field.default is not dataclasses.MISSING:
        kwargs["default"] = field.default
    elif field.default_factory is not dataclasses.MISSING:
        kwargs["default"] = field.default_factory()
    else:
        kwargs["required"] = True
    return kwargs


class DataClassArgumentParser(ArgumentParser):
    """
    This subclass of `argparse.ArgumentParser` uses type hints on dataclasses to generate arguments.
    The class is designed to play well with the native argparse. In particular, you can add more (non-dataclass backed)
    arguments to the parser after initialization and you'll get the output back after parsing as an additional
    namespace.
    """

    dataclass_types: Iterable[DataClassType]

    def __init__(
        self, dataclass_types: Union[DataClassType, Iterable[DataClassType]], **kwargs
    ):
        """
        Args:
            dataclass_types:
                Dataclass type, or list of dataclass types for which we will "fill" instances with the parsed args.
            kwargs:
                (Optional) Passed to `argparse.ArgumentParser()` in the regular way.
        """
        super().__init__(**kwargs)
        if dataclasses.is_dataclass(dataclass_types):
            dataclass_types = [dataclass_types]
        self.dataclass_types = dataclass_types
        self._argument_metadata = dict()
        for dtype in self.dataclass_types:
            self._add_dataclass_arguments(dtype)

    def _cleanup_complex_types(self, field):
        typestring = str(field.type)
        for prim_type in (int, float, str):
            for collection in (List,):
                if (
                    typestring == f"typing.Union[{collection[prim_type]}, NoneType]"
                    or typestring == f"typing.Optional[{collection[prim_type]}]"
                ):
                    field.type = collection[prim_type]
            if (
                typestring == f"typing.Union[{prim_type.__name__}, NoneType]"
                or typestring == f"typing.Optional[{prim_type.__name__}]"
            ):
                field.type = prim_type
        return field

    def _check_value(self, action, value):
        # converted value must be one of the choices (if specified)
        if isinstance(value, Enum):
            value = value.value
        if action.choices is not None and value not in action.choices:
            args = {"value": value, "choices": ", ".join(map(repr, action.choices))}
            msg = _("invalid choice: %(value)r (choose from %(choices)s)")
            raise ArgumentError(action, msg % args)

    def _add_dataclass_arguments(self, dtype: DataClassType):
        assert dtype not in self._argument_metadata
        argument_metadata = dict()
        for field in dataclasses.fields(dtype):
            if not field.init:
                continue
            field_name = f"--{field.name}"
            kwargs = field.metadata.copy()
            # field.metadata is not used at all by Data Classes,
            # it is provided as a third-party extension mechanism.
            if isinstance(field.type, str):
                raise ImportError(
                    "This implementation is not compatible with Postponed Evaluation of Annotations (PEP 563),"
                    "which can be opted in from Python 3.7 with `from __future__ import annotations`."
                    "We will add compatibility when Python 3.9 is released."
                )

            field = self._cleanup_complex_types(field)
            if field.type is bool or field.type is Optional[bool]:
                if field.default is True:
                    self.add_argument(
                        f"--no_{field.name}",
                        action="store_false",
                        dest=field.name,
                        **kwargs,
                    )

                # Hack because type=bool in argparse does not behave as we want.
                kwargs = _handle_kwargs_bool(field, kwargs)
            elif hasattr(field.type, "__origin__") and issubclass(
                field.type.__origin__, List
            ):
                # Handle list types (+ generics)
                kwargs = _handle_kwargs_list(field, kwargs)
            elif isinstance(field.type, type) and issubclass(field.type, Enum):
                kwargs = _handle_kwargs_enum(field, kwargs)
            else:
                kwargs["type"] = field.type
                if field.default is not dataclasses.MISSING:
                    kwargs["default"] = field.default
                elif field.default_factory is not dataclasses.MISSING:
                    kwargs["default"] = field.default_factory()
                else:
                    kwargs["required"] = True
            self.add_argument(field_name, **kwargs)

        self._argument_metadata[dtype] = argument_metadata

    def parse_args_into_dataclasses(
        self,
        args=None,
        return_remaining_strings=False,
        look_for_args_file=True,
        args_filename=None,
    ) -> Tuple[DataClass, ...]:
        """
        Parse command-line args into instances of the specified dataclass types.
        This relies on argparse's `ArgumentParser.parse_known_args`. See the doc at:
        docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser.parse_args
        Args:
            args:
                List of strings to parse. The default is taken from sys.argv. (same as argparse.ArgumentParser)
            return_remaining_strings:
                If true, also return a list of remaining argument strings.
            look_for_args_file:
                If true, will look for a ".args" file with the same base name as the entry point script for this
                process, and will append its potential content to the command line args.
            args_filename:
                If not None, will uses this file instead of the ".args" file specified in the previous argument.
        Returns:
            Tuple consisting of:
                - the dataclass instances in the same order as they were passed to the initializer.abspath
                - if applicable, an additional namespace for more (non-dataclass backed) arguments added to the parser
                  after initialization.
                - The potential list of remaining argument strings. (same as argparse.ArgumentParser.parse_known_args)
        """
        if args_filename or (look_for_args_file and len(sys.argv)):
            if args_filename:
                args_file = Path(args_filename)
            else:
                args_file = Path(sys.argv[0]).with_suffix(".args")

            if args_file.exists():
                fargs = args_file.read_text().split()
                args = fargs + args if args is not None else fargs + sys.argv[1:]
                # in case of duplicate arguments the first one has precedence
                # so we append rather than prepend.
        namespace, remaining_args = self.parse_known_args(args=args)
        outputs = []
        for dtype in self.dataclass_types:
            keys = {f.name for f in dataclasses.fields(dtype) if f.init}

            inputs = {k: v for k, v in vars(namespace).items() if k in keys}
            for k in keys:
                delattr(namespace, k)
            obj = dtype(**inputs)
            outputs.append(obj)
        if len(namespace.__dict__) > 0:
            # additional namespace.
            outputs.append(namespace)
        if return_remaining_strings:
            return (*outputs, remaining_args)
        else:
            if remaining_args:
                raise ValueError(
                    f"Some specified arguments are not used by the HfArgumentParser: {remaining_args}"
                )

            return (*outputs,)

    def parse_json_file(self, json_file: str) -> Tuple[DataClass, ...]:
        """
        Alternative helper method that does not use `argparse` at all, instead loading a json file and populating the
        dataclass types.
        """
        data = json.loads(Path(json_file).read_text())
        return self.parse_dict(data)

    def parse_dict(self, args: dict) -> Tuple[DataClass, ...]:
        """
        Alternative helper method that does not use `argparse` at all, instead uses a dict and populating the dataclass
        types.
        """
        outputs = []
        for dtype in self.dataclass_types:
            fields = dataclasses.fields(dtype)
            inputs = dict()
            for field in fields:
                if isinstance(field.type, type) and issubclass(field.type, Enum):
                    inputs[field.name] = field.type(args[field.name])
                elif field.init:
                    inputs[field.name] = args[field.name]

            obj = dtype(**inputs)
            outputs.append(obj)
        return (*outputs,)


def dataclass_to_json(args: DataClassType, additional_dict: dict = None) -> str:
    """
    Convert a dataclass arguments object to a JSON string.

    :param args: An arguments object, must be an instance of a `dataclass`
    :return: A JSON encoded string

    """
    assert dataclasses.is_dataclass(
        args
    ), f"Argument must be an instance of a dataclass, got {args.__class__}"
    args_dict = dataclasses.asdict(args)
    if additional_dict is not None:
        args_dict.update(additional_dict)
    return json.dumps(args_dict, cls=EnumEncoder, indent=4)
