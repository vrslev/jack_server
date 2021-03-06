import pytest

import jack_server._lib
from jack_server._lib import _lib_names, get_library_name


@pytest.mark.parametrize("name", _lib_names)
def test_get_library_name_found(monkeypatch: pytest.MonkeyPatch, name: str):
    def func(v: str):
        if v == name:
            return "ok"

    monkeypatch.setattr(jack_server._lib, "find_library", func)
    assert get_library_name() == "ok"


def test_get_library_name_not_found(monkeypatch: pytest.MonkeyPatch):
    def func(v: str):
        pass

    monkeypatch.setattr(jack_server._lib, "find_library", func)
    with pytest.raises(RuntimeError, match="Couldn't find"):
        get_library_name()
