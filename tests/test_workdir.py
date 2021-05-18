import os
from os.path import abspath

import pytest

from arggo._internal.global_store import GlobalStore
from arggo.environment.workdir import Workdir, DirectoryStrategy
from tests.test_utils import FakeDirectoryStrategy


@pytest.fixture()
def global_store():
    return GlobalStore()


@pytest.fixture()
def strategy():
    return FakeDirectoryStrategy()


class TestWorkdir:
    def test_workdir_is_same_if_no_init(self, global_store, strategy):
        workdir = Workdir(global_store, strategy)
        assert abspath(workdir.workdir()) == abspath(workdir.original_workdir())

    def test_workdir_is_different_if_init(self, global_store, strategy):
        workdir = Workdir(global_store, strategy)
        workdir.initialize("logs")
        assert abspath(workdir.workdir()) != abspath(workdir.original_workdir())
        workdir.revert()

    def test_workdir_is_cwd(self, global_store, strategy):
        workdir = Workdir(global_store, strategy)
        workdir.initialize("logs")
        assert abspath(workdir.workdir()) == abspath(strategy.getcwd())
        workdir.revert()
