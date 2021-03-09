from dataclasses import field, MISSING
from typing import List, Any


# noinspection PyShadowingBuiltins
def parser_field(default=MISSING, default_factory=MISSING,
                 help: str = None,
                 choices: List[Any] = None,
                 *args,
                 **kwargs):
    metadata = kwargs.pop('metadata', None)
    if metadata is None:
        metadata = dict()

    if help is not None:
        metadata['help'] = help
    if choices is not None:
        metadata['choices'] = choices

    return field(
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        *args,
        **kwargs
    )
