from unittest.mock import MagicMock

import pytest

from arggo.integration.wandb import WandbPlugin, is_wandb_available

wandb = pytest.importorskip(
    "wandb",
    reason="wandb is an optional dependency; skip these tests when it isn't installed",
)


@pytest.fixture(autouse=True)
def _reset_wandb_run(monkeypatch):
    monkeypatch.setattr(wandb, "run", None)


def _fake_run(run_id="run-id", run_name="run-name", run_url="https://wandb.ai/run"):
    run = MagicMock()
    run.id = run_id
    run.name = run_name
    run.get_url.return_value = run_url
    return run


class TestIsWandbAvailable:
    def test_true_when_importable(self):
        assert is_wandb_available() is True

    def test_false_when_import_fails(self, monkeypatch):
        real_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "wandb":
                raise RuntimeError("simulated import failure")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", fake_import)
        assert is_wandb_available() is False


class TestWandbPluginIsDisabled:
    def test_false_by_default(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog"])
        assert WandbPlugin.is_disabled() is False

    def test_true_when_flag_present(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "--wandb_disable"])
        assert WandbPlugin.is_disabled() is True


class TestWandbPlugin:
    def test_parameters_dump_initializes_run_with_config(self, monkeypatch):
        mock_init = MagicMock(
            side_effect=lambda **kwargs: setattr(wandb, "run", _fake_run())
        )
        monkeypatch.setattr(wandb, "init", mock_init)

        dump = WandbPlugin().parameters_dump({"learning_rate": 0.1})

        mock_init.assert_called_once_with(config={"learning_rate": 0.1})
        assert dump == {
            "run_id": "run-id",
            "run_name": "run-name",
            "run_url": "https://wandb.ai/run",
        }

    def test_parameters_dump_reuses_existing_run(self, monkeypatch):
        monkeypatch.setattr(wandb, "run", _fake_run())
        mock_init = MagicMock()
        monkeypatch.setattr(wandb, "init", mock_init)

        WandbPlugin().parameters_dump({"learning_rate": 0.1})

        mock_init.assert_not_called()

    def test_parameters_dump_returns_none_when_disabled(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "--wandb_disable"])
        mock_init = MagicMock()
        monkeypatch.setattr(wandb, "init", mock_init)

        assert WandbPlugin().parameters_dump({}) is None
        mock_init.assert_not_called()

    def test_parameters_dump_returns_none_when_unavailable(self, monkeypatch):
        monkeypatch.setattr("arggo.integration.wandb.is_wandb_available", lambda: False)
        assert WandbPlugin().parameters_dump({}) is None
