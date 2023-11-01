import pytest
import os

import jack_server._lib
from jack_server._lib import _lib_names, get_library_name


@pytest.mark.parametrize("name", _lib_names)
def test_get_library_name_found(monkeypatch: pytest.MonkeyPatch, name: str):

    library_name = get_library_name()
    # check library found and is in list of names
    assert True in [name in library_name for name in _lib_names]


def test_get_library_name_not_found(monkeypatch: pytest.MonkeyPatch):
    def func(v: str):
        pass

    monkeypatch.setattr(                # fake windows as platform
        jack_server._lib.platform,
        "system",
        lambda: "Linux")
    monkeypatch.setattr(jack_server._lib, "find_library", func)
    with pytest.raises(RuntimeError, match="Couldn't find"):
        get_library_name()


@pytest.mark.parametrize("name", _lib_names)
def test_get_library_windows_name_found(monkeypatch: pytest.MonkeyPatch, name: str):
    monkeypatch.setattr(                # fake windows registries path function
        jack_server._lib,
        "get_windows_registries",
        lambda: {'InstallPath': ''})    # empty install path
    file_path = f"{name}.dll"           # library file path
    open(file_path, "a").close()        # create fake library file
    monkeypatch.setattr(                # fake windows as platform
        jack_server._lib.platform,
        "system",
        lambda: "Windows")
    assert get_library_name() == file_path
    os.remove(file_path)
