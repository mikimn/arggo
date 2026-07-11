import pytest

from arggo._internal.global_store import GlobalStore


@pytest.fixture(autouse=True)
def _reset_global_store():
    """Each test should behave like its own process: arggo's process-wide
    GlobalStore (parser/experiment cache, workdir state) must not leak
    between tests."""
    GlobalStore().clear()
    yield
    GlobalStore().clear()
