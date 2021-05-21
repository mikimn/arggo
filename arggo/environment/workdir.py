import abc
import datetime
import os
from os.path import join

from arggo._internal.global_store import GlobalStore


class DirectoryStrategy(abc.ABC):
    @abc.abstractmethod
    def makedirs(self, path):
        raise NotImplementedError()

    @abc.abstractmethod
    def chdir(self, path):
        raise NotImplementedError()

    @abc.abstractmethod
    def getcwd(self):
        raise NotImplementedError()


class DefaultDirectoryStrategy(DirectoryStrategy):
    def makedirs(self, path):
        os.makedirs(path, exist_ok=True)

    def chdir(self, path):
        os.chdir(path)

    def getcwd(self):
        return os.getcwd()


class Workdir:
    _KEY_ORIGINAL_WORKDIR = "original_workdir"
    _KEY_CURRENT_WORKDIR = "current_workdir"
    _KEY_INITIALIZED = "workdir_initialized"

    def __init__(
        self, global_store: GlobalStore, strategy: DirectoryStrategy = None
    ) -> None:
        super().__init__()
        self.gs = global_store
        if strategy is None:
            strategy = DefaultDirectoryStrategy()
        self.strategy = strategy

    def _should_initialize(self):
        return not self.gs.get(Workdir._KEY_INITIALIZED, False)

    def _mark_initialized(self):
        self.gs.put(Workdir._KEY_INITIALIZED, True)

    def initialize(self, root_directory: str) -> str:
        if self._should_initialize():
            new_workdir, original_workdir = init_workdir(root_directory, self.strategy)
            self.gs.put(Workdir._KEY_CURRENT_WORKDIR, new_workdir)
            self.gs.put(Workdir._KEY_ORIGINAL_WORKDIR, original_workdir)
            self._mark_initialized()
            return new_workdir
        return self.workdir()

    def workdir(self):
        return self.gs.get(Workdir._KEY_CURRENT_WORKDIR, os.getcwd())

    def original_workdir(self) -> str:
        return self.gs.get(Workdir._KEY_ORIGINAL_WORKDIR, os.getcwd())

    def revert(self):
        os.chdir(self.original_workdir())
        self.gs.delete(Workdir._KEY_CURRENT_WORKDIR)
        self.gs.delete(Workdir._KEY_ORIGINAL_WORKDIR)


def init_workdir(
    root_directory: str, strategy: DirectoryStrategy, _template="%Y-%m-%d/%H-%M-%S"
):
    original_working_dir = strategy.getcwd()
    output_dir = join(root_directory, datetime.datetime.now().strftime(_template))
    strategy.makedirs(output_dir)
    strategy.chdir(output_dir)
    return os.path.abspath(strategy.getcwd()), original_working_dir


def get_workdir() -> Workdir:
    """Get the default `Workdir` object, which can be used to determine the current workdir and the original,
    if it was changed during initialization.

    """
    return Workdir(GlobalStore())
