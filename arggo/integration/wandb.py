# Integration utilities for Weights & Biases
import sys
from typing import Any, Dict, Union

from arggo.plugin import Plugin

_DISABLE_FLAG = "--wandb_disable"


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


def is_wandb_disabled() -> bool:
    return _DISABLE_FLAG in sys.argv


class WandbPlugin(Plugin):
    @property
    def name(self):
        return "wandb"

    def parameters_dump(
        self, parameters: Dict[str, Any]
    ) -> Union[Dict[str, Any], None]:
        if is_wandb_disabled() or not is_wandb_available():
            return None
        import wandb

        if wandb.run is None:
            wandb.init(config=parameters)
        run = wandb.run
        return {"run_id": run.id, "run_name": run.name, "run_url": run.get_url()}
