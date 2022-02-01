from ctypes import POINTER, pointer
from typing import Any, Callable, Literal

import jack_server._libjackserver_bindings as _lib


class Parameter:
    def __init__(self, ptr: Any):
        self.ptr = ptr
        self.type = _lib.jackctl_parameter_get_type(self.ptr)

    @property
    def name(self) -> bytes:
        return _lib.jackctl_parameter_get_name(self.ptr)

    @property
    def value(self):
        param_v = _lib.jackctl_parameter_get_value(self.ptr)
        if self.type == 1:
            # JackParamInt
            return param_v.i
        elif self.type == 2:
            # JackParamUInt
            return param_v.ui
        elif self.type == 3:
            # JackParamChar
            return param_v.c
        elif self.type == 4:
            # JackParamString
            return param_v.ss
        elif self.type == 5:
            # JackParamBool
            return param_v.b

    @value.setter
    def value(self, val: Any):
        param_v = _lib.jackctl_parameter_value()
        if self.type == 1:
            # JackParamInt
            param_v.i = int(val)
        elif self.type == 2:
            # JackParamUInt
            param_v.ui = int(val)
        elif self.type == 3:
            # JackParamChar
            assert isinstance(val, str) and len(val) == 1
            param_v.c = val
        elif self.type == 4:
            # JackParamString
            assert isinstance(val, bytes)
            param_v.ss = val
        elif self.type == 5:
            # JackParamBool
            param_v.b = bool(val)
        _lib.jackctl_parameter_set_value(self.ptr, pointer(param_v))

    def __repr__(self) -> str:
        return f"<jack_server.Parameter value={self.value}>"


SampleRate = Literal[44100, 48000]


def _get_params_dict(params_jslist: Any):
    params: dict[bytes, Parameter] = {}

    for param_ptr in _lib.JSIter(params_jslist, POINTER(_lib.jackctl_parameter_t)):
        param = Parameter(param_ptr)
        params[param.name] = param

    return params


class Driver:
    def __init__(self, ptr: Any):
        self.ptr = ptr

        params_jslist = _lib.jackctl_driver_get_parameters(self.ptr)
        self.params = _get_params_dict(params_jslist)

    @property
    def name(self) -> str:
        return _lib.jackctl_driver_get_name(self.ptr).decode()

    def set_device(self, name: str):
        self.params[b"device"].value = name.encode()

    def set_rate(self, rate: SampleRate):
        self.params[b"rate"].value = rate


class ServerNotStartedError(RuntimeError):
    pass


class ServerNotOpenedError(RuntimeError):
    pass


class Server:  # TODO: Have to run in sync mode.
    def __init__(
        self,
        *,
        driver: str,
        device: str,
        rate: SampleRate | None = None,
        sync: bool = False,
    ):
        self.ptr = _lib.jackctl_server_create(
            _lib.DeviceAcquireFunc(),  # type: ignore
            _lib.DeviceReleaseFunc(),  # type: ignore
            _lib.DeviceReservationLoop(),  # type: ignore
        )
        self._created = True
        self._opened = False
        self._started = False

        params_jslist = _lib.jackctl_server_get_parameters(self.ptr)
        self.params = _get_params_dict(params_jslist)

        self.driver = self.get_driver_by_name(driver)
        self.driver.set_device(device)

        if rate:
            self.driver.set_rate(rate)
        if sync:
            self.set_sync(sync)

    def get_driver_by_name(self, name: str):
        driver_jslist = _lib.jackctl_server_get_drivers_list(self.ptr)

        for ptr in _lib.JSIter(driver_jslist, POINTER(_lib.jackctl_driver_t)):
            driver = Driver(ptr)
            if driver.name == name:
                return driver

        raise RuntimeError(f"Driver not found: {name}")

    def set_sync(self, sync: bool):
        self.params[b"sync"].value = sync

    def start(self):
        self._opened = _lib.jackctl_server_open(self.ptr, self.driver.ptr)
        if not self._opened:
            raise ServerNotStartedError

        self._started = _lib.jackctl_server_start(self.ptr)
        if not self._started:
            raise ServerNotOpenedError

    def stop(self):
        if self._started:
            _lib.jackctl_server_stop(self.ptr)
        self._started = False

        if self._opened:
            _lib.jackctl_server_close(self.ptr)
        self._opened = False

    def __del__(self):
        if getattr(self, "_created", None):
            _lib.jackctl_server_destroy(self.ptr)


_dont_garbage_collect: list[Any] = []


def _wrap_error_or_info_callback(
    callback: Callable[[str], None] | None,
):
    if callback:

        def wrapped_callback(message: bytes):
            callback(message.decode())

        cb = _lib.PrintFunction(wrapped_callback)
    else:
        cb = _lib.PrintFunction()  # type: ignore

    _dont_garbage_collect.append(cb)
    return cb


def set_info_function(callback: Callable[[str], None] | None):
    _lib.jack_set_info_function(_wrap_error_or_info_callback(callback))


def set_error_function(callback: Callable[[str], None] | None):
    _lib.jack_set_error_function(_wrap_error_or_info_callback(callback))
