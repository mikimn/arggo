from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
from typing import Any, Dict, List, Type, Union


class PluginMeta(ABCMeta):
    """Auto-registers concrete Plugin subclasses, so a plugin only needs to be
    importable (e.g. from arggo/integration/__init__.py) to be picked up as a
    default plugin - core.py doesn't need to name it explicitly."""

    registry: List[Type["Plugin"]] = []

    def __new__(mcs, class_name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, class_name, bases, namespace, **kwargs)
        if not cls.__abstractmethods__:
            mcs.registry.append(cls)
        return cls


class Plugin(metaclass=PluginMeta):
    # @abstractmethod
    # def install(self):
    #     raise NotImplementedError()

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError()

    @abstractmethod
    def parameters_dump(
        self, parameters: Dict[str, Any]
    ) -> Union[Dict[str, Any], None]:
        raise NotImplementedError()

    @classmethod
    def add_meta_arguments(cls, meta_parser: ArgumentParser) -> None:
        """Override to register any CLI meta-arguments this plugin needs
        (e.g. an opt-out flag). Anything registered here is automatically
        protected by Arggo's reserved-argument-name check."""
        pass

    def __eq__(self, other):
        if isinstance(other, Plugin):
            return self.name == other.name
        return False
