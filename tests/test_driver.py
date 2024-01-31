import sys

import pytest

from jack_server import Server
from tests.conftest import check_property


@pytest.mark.parametrize(
    ("name", "value", "param_value"), (("rate", 41000, 41000), ("period", 256, 256))
)
def test_driver_properties(driver: str, name: str, value: str, param_value: str):
    server = Server(driver=driver)
    check_property(server.driver, name, value, param_value)


@pytest.mark.skipif(
    sys.platform != "linux", reason="nperiods is only supported on Linux"
)
def test_driver_nperiods():
    server = Server(driver="alsa", nperiods=2)
    check_property(server.driver, name="nperiods", value=2, param_value=2)
