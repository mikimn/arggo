from dataclasses import field, MISSING
from enum import Enum
from typing import List, Any, Type, Callable


# noinspection PyShadowingBuiltins
def parser_field(
    default=MISSING,
    default_factory=MISSING,
    help: str = None,
    choices: List[Any] = None,
    required: bool = False,
    *args,
    **kwargs
):
    metadata = kwargs.pop("metadata", None)
    if metadata is None:
        metadata = dict()

    if help is not None:
        metadata["help"] = help
    if choices is not None:
        metadata["choices"] = choices
    metadata["required"] = required

    return field(
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        *args,
        **kwargs
    )


def mapped_field(mapper: Callable[[Any], Any], *args, **kwargs):
    return parser_field(*args, **kwargs, metadata={"type": mapper})
