# Integration utilities for Weights & Biases
import sys
from argparse import ArgumentParser
from typing import Any, Dict, Union

from arggo.plugin import Plugin


def is_wandb_available() -> bool:
    try:
        import wandb  # noqa: F401
    except Exception:
        # wandb pulls in a large, fast-moving dependency chain (protobuf, grpc, ...)
        # that can fail for reasons other than "not installed" (e.g. a protobuf version
        # mismatch); treat any failure to import as "unavailable" rather than crashing
        # the user's run over an optional integration.
        return False
    return True


class WandbPlugin(Plugin):
    _DISABLE_FLAG = "--wandb_disable"

    @property
    def name(self):
        return "wandb"

    @classmethod
    def add_meta_arguments(cls, meta_parser: ArgumentParser) -> None:
        meta_parser.add_argument(
            cls._DISABLE_FLAG,
            action="store_true",
            help="Disable logging this run's parameters to Weights & Biases, even if wandb is installed",
        )

    @classmethod
    def is_disabled(cls) -> bool:
        return cls._DISABLE_FLAG in sys.argv

    def parameters_dump(
        self, parameters: Dict[str, Any]
    ) -> Union[Dict[str, Any], None]:
        if self.is_disabled() or not is_wandb_available():
            return None
        import wandb

        if wandb.run is None:
            wandb.init(config=parameters)
        run = wandb.run
        return {"run_id": run.id, "run_name": run.name, "run_url": run.get_url()}
