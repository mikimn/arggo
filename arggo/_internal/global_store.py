from typing import Any, Dict

GLOBAL_STORE_KEY = "__arggo__"


class GlobalStore:
    def __init__(self, name=GLOBAL_STORE_KEY) -> None:
        super().__init__()
        self.name = name
        if name not in _global_store():
            global_store_init(name)

    def get(self, key: str, default: Any = None) -> Any:
        return global_store_get(self.name, key, default)

    def put(self, key: str, value: Any):
        return global_store_put(self.name, key, value)

    def delete(self, key: str):
        return global_store_delete(self.name, key)

    def clear(self):
        return global_store_clear(self.name)


_GLOBAL_DICT = dict()


def _global_store() -> Dict[str, Any]:
    return _GLOBAL_DICT


def global_store_init(key: str = GLOBAL_STORE_KEY):
    if key in _global_store():
        raise ValueError(
            f"Cannot initialize a global store named '{key}'. It either exists or this key is reserved"
        )
    _global_store().update({key: dict()})


def _ensure_global_store_init(global_store_name: str):
    assert global_store_name in _global_store(), (
        "The global store was not initialized. " "Call global_store_init first."
    )


def global_store_get(global_store_name: str, key: str, default=None) -> Any:
    _ensure_global_store_init(global_store_name)
    global_store: Dict[str, Any] = _global_store()[global_store_name]
    if key not in global_store:
        return default
    return global_store[key]


def global_store_put(global_store_name: str, key: str, value: Any):
    _ensure_global_store_init(global_store_name)
    if value is None:
        raise ValueError(f"Cannot put a None value in the global store for key '{key}'")
    global_store: Dict[str, Any] = _global_store()[global_store_name]
    global_store[key] = value


def global_store_delete(global_store_name: str, key: str):
    _ensure_global_store_init(global_store_name)
    global_store: Dict[str, Any] = _global_store()[global_store_name]
    if key not in global_store:
        raise ValueError(f"Key '{key}' is not in the store")
    del global_store[key]


def global_store_clear(global_store_name: str):
    _ensure_global_store_init(global_store_name)
    _global_store()[global_store_name].clear()
