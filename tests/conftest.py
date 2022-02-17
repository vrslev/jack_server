import sys
from typing import Union

import pytest

from jack_server import Driver, Server
from jack_server._parameter import ValueType


@pytest.fixture(scope="session")
def driver() -> str:
    if sys.platform == "darwin":  # pragma: no cover
        return "coreaudio"
    elif sys.platform == "linux":  # pragma: no cover
        return "dummy"
    raise NotImplementedError  # pragma: no cover


@pytest.fixture
def server(driver: str):
    server = Server(driver=driver, period=1024, sync=True, realtime=False)
    yield server
    server.stop()


def check_property(
    inst: Union[Server, Driver], name: str, value: ValueType, param_value: ValueType
):
    setattr(inst, name, value)
    assert getattr(inst, name) == value
    assert inst.params[name].value == param_value
