class ArggoReservedError(Exception):
    """Raised when a user-defined dataclass field collides with an argument name
    reserved by Arggo for its own meta-arguments (e.g. --arggo_interactive)."""
