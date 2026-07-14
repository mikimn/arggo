import os
import pytest

from arggo._internal.global_store import GlobalStore

# Prevent the wandb plugin from making real network calls or spawning its
# background service process while running the test suite.
os.environ.setdefault("WANDB_MODE", "disabled")


@pytest.fixture(autouse=True)
def _reset_global_store():
    """Each test should behave like its own process: arggo's process-wide
    GlobalStore (parser/experiment cache, workdir state) must not leak
    between tests."""
    GlobalStore().clear()
    yield
    GlobalStore().clear()
