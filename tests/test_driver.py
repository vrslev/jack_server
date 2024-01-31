import pytest

from jack_server import Server
from tests.conftest import check_property


@pytest.mark.parametrize(
    ("name", "value", "param_value"), (("rate", 41000, 41000), ("period", 256, 256))
)
def test_driver_properties(driver: str, name: str, value: str, param_value: str):
    server = Server(driver=driver)
    check_property(server.driver, name, value, param_value)
