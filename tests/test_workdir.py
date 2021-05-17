import os

import pytest
from os.path import abspath

from arggo._internal.global_store import GlobalStore, _global_store
from arggo.environment.workdir import Workdir


@pytest.fixture()
def global_store():
    return GlobalStore()


class TestWorkdir:
    def test_workdir_is_same_if_no_init(self, global_store):
        workdir = Workdir(global_store)
        assert abspath(workdir.workdir()) == abspath(workdir.original_workdir())

    def test_workdir_is_different_if_init(self, global_store):
        workdir = Workdir(global_store)
        workdir.initialize("logs")
        assert abspath(workdir.workdir()) != abspath(workdir.original_workdir())
        workdir.revert()

    def test_workdir_is_cwd(self, global_store):
        workdir = Workdir(global_store)
        workdir.initialize("logs")
        assert abspath(workdir.workdir()) == abspath(os.getcwd())
        workdir.revert()
