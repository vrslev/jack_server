import pytest

import jack_server._server
from jack_server import (
    DriverNotFoundError,
    Server,
    ServerNotOpenedError,
    ServerNotStartedError,
)
from jack_server._parameter import ValueType
from tests.conftest import check_property


def test_start_stop(server: Server):
    server.start()
    assert server._created
    assert server._opened
    assert server._started
    server.stop()
    assert not server._opened
    assert not server._started


@pytest.mark.parametrize(
    ("name", "value", "param_value"),
    (
        ("name", "myfancyserver", b"myfancyserver"),
        ("sync", True, True),
        ("realtime", False, False),
    ),
)
def test_server_properties(
    driver: str, name: str, value: ValueType, param_value: ValueType
):
    server = Server(driver=driver)
    check_property(server, name, value, param_value)


def test_init_full_args(driver: str):
    server = Server(
        name="myfancyserver",
        sync=True,
        realtime=False,
        driver=driver,
        rate=48000,
        period=512,
    )
    server.start()
    server.stop()


def returns_false(*args: object):
    return False


def test_server_not_opened(server: Server, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(jack_server._server.lib, "jackctl_server_open", returns_false)
    with pytest.raises(ServerNotOpenedError):
        server._open()


def test_server_not_started(server: Server, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(jack_server._server.lib, "jackctl_server_start", returns_false)
    with pytest.raises(ServerNotStartedError):
        server._start()


def test_driver_not_found(server: Server):
    with pytest.raises(DriverNotFoundError):
        server._get_driver_by_name("not_existing_driver")
