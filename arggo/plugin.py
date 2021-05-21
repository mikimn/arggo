from abc import ABC, abstractmethod
from typing import Dict, Any, Union


class Plugin(ABC):
    # @abstractmethod
    # def install(self):
    #     raise NotImplementedError()

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError()

    @abstractmethod
    def parameters_dump(self) -> Union[Dict[str, Any], None]:
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, Plugin):
            return self.name == other.name
        return False
