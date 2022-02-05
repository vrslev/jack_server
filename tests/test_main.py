import sys

import pytest

import jack_server


@pytest.fixture
def driver():
    if sys.platform == "darwin":
        return "coreaudio"
    elif sys.platform == "linux":
        return "dummy"


def test_simple(driver: str):
    server = jack_server.Server(driver=driver)
    server.start()
    assert server._created
    assert server._opened
    assert server._started
    server.stop()
    assert not server._opened
    assert not server._started
