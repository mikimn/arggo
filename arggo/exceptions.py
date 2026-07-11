class ArggoReservedError(Exception):
    """Raised when a user-defined dataclass field collides with an argument name
    reserved by Arggo for its own meta-arguments (e.g. --arggo_interactive)."""


class ArggoAlreadyConfiguredError(Exception):
    """Raised when a second, distinct consume/configure-decorated entry point
    is invoked in a process that has already been configured by another one."""
