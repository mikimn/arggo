import pytest

from arggo._internal.global_store import (
    global_store_init,
    global_store_get,
    global_store_put,
    global_store_delete,
    _global_store,
    GLOBAL_STORE_KEY,
)


class TestGlobalStore:
    def setup_method(self):
        """ setup any state specific to the execution of the given module."""
        _global_store().clear()

    def test_no_init_get_throws_assert_error(self):
        """Calling global_store_get() without init() throws an AssertionError"""
        with pytest.raises(AssertionError):
            _ = global_store_get(GLOBAL_STORE_KEY, "key")

    def test_global_store_init_existing_name_throws_value_error(self):
        with pytest.raises(ValueError):
            global_store_init()
            global_store_init()

    def test_no_init_put_throws_assert_error(self):
        with pytest.raises(AssertionError):
            global_store_put(GLOBAL_STORE_KEY, "key", "value")

    def test_get_returns_none_new_key(self):
        global_store_init()
        value = global_store_get(GLOBAL_STORE_KEY, "key")
        assert value is None

    def test_get_after_put_returns_same_value(self):
        global_store_init()
        global_store_put(GLOBAL_STORE_KEY, "key", 1)
        assert global_store_get(GLOBAL_STORE_KEY, "key") == 1

    def test_get_returns_default_new_key(self):
        print(_global_store())
        global_store_init()

        value = global_store_get(GLOBAL_STORE_KEY, "key", default="value")
        assert value == "value"

    def test_put_none_value_throws_value_error(self):
        with pytest.raises(ValueError):
            global_store_init()
            global_store_put(GLOBAL_STORE_KEY, "key", None)

    def test_global_store_init_with_different_name(self):
        name = "my_global_store"
        global_store_init(key=name)

        global_store_put(name, "key", "value")
        assert global_store_get(name, "key") == "value"

    def test_global_store_delete_non_existing_key_throws_value_error(self):
        global_store_init()
        with pytest.raises(ValueError):
            global_store_delete(GLOBAL_STORE_KEY, "non_existing_key")

    def test_global_store_delete_successful(self):
        global_store_init()
        global_store_put(GLOBAL_STORE_KEY, "key", 1)

        global_store_delete(GLOBAL_STORE_KEY, "key")
        assert global_store_get(GLOBAL_STORE_KEY, "key") is None
