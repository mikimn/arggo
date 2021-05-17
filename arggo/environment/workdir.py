import datetime
import os
from os.path import join

from arggo._internal.global_store import GlobalStore


class Workdir:
    _KEY_ORIGINAL_WORKDIR = "original_workdir"
    _KEY_CURRENT_WORKDIR = "current_workdir"

    def __init__(self, global_store: GlobalStore) -> None:
        super().__init__()
        self.gs = global_store

    def initialize(self, root_directory: str) -> str:
        new_workdir, original_workdir = init_workdir(root_directory)
        self.gs.put(Workdir._KEY_CURRENT_WORKDIR, new_workdir)
        self.gs.put(Workdir._KEY_ORIGINAL_WORKDIR, original_workdir)
        return new_workdir

    def workdir(self):
        return self.gs.get(Workdir._KEY_CURRENT_WORKDIR, os.getcwd())

    def original_workdir(self) -> str:
        return self.gs.get(Workdir._KEY_ORIGINAL_WORKDIR, os.getcwd())

    def revert(self):
        os.chdir(self.original_workdir())
        self.gs.delete(Workdir._KEY_CURRENT_WORKDIR)
        self.gs.delete(Workdir._KEY_ORIGINAL_WORKDIR)


def init_workdir(root_directory: str, _template="%Y-%m-%d/%H-%M-%S"):
    original_working_dir = os.getcwd()

    output_dir = join(root_directory, datetime.datetime.now().strftime(_template))
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)
    return os.path.abspath(os.getcwd()), original_working_dir
