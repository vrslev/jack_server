from unittest.mock import Mock

from _pytest.capture import CaptureFixture

from jack_server import Server, set_error_function, set_info_function


def test_set_output_functions_none(capsys: CaptureFixture[str], server: Server):
    set_error_function(None)
    set_info_function(None)
    server.start()
    captured = capsys.readouterr()
    assert not captured.out
    assert not captured.err


def test_set_output_functions_not_none(server: Server):
    out_mock = Mock()
    err_mock = Mock()
    set_error_function(out_mock)
    set_info_function(err_mock)
    server.start()
    out_mock.assert_called()
    err_mock.assert_called()
