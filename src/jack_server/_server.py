from __future__ import annotations

from ctypes import POINTER, pointer
from typing import Any, Callable, Literal

import jack_server._lib as lib


class Parameter:
    def __init__(self, ptr: Any) -> None:
        self.ptr = ptr
        self.type = lib.jackctl_parameter_get_type(self.ptr)

    @property
    def name(self) -> bytes:
        return lib.jackctl_parameter_get_name(self.ptr)

    @property
    def value(self) -> int | str | bytes | bool | None:
        param_v = lib.jackctl_parameter_get_value(self.ptr)
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
    def value(self, val: Any) -> None:
        param_v = lib.jackctl_parameter_value()
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
        lib.jackctl_parameter_set_value(self.ptr, pointer(param_v))

    def __repr__(self) -> str:
        return f"<jack_server.Parameter value={self.value}>"


SampleRate = Literal[44100, 48000]


def _get_params_dict(params_jslist: Any) -> dict[bytes, Parameter]:
    params: dict[bytes, Parameter] = {}

    for param_ptr in lib.JSIter(params_jslist, POINTER(lib.jackctl_parameter_t)):
        param = Parameter(param_ptr)
        params[param.name] = param

    return params


class Driver:
    def __init__(self, ptr: Any) -> None:
        self.ptr = ptr

        params_jslist = lib.jackctl_driver_get_parameters(self.ptr)
        self.params = _get_params_dict(params_jslist)

    @property
    def name(self) -> str:
        return lib.jackctl_driver_get_name(self.ptr).decode()

    def set_device(self, name: str) -> None:
        self.params[b"device"].value = name.encode()

    def set_rate(self, rate: SampleRate) -> None:
        self.params[b"rate"].value = rate


class ServerNotStartedError(RuntimeError):
    pass


class ServerNotOpenedError(RuntimeError):
    pass


class Server:
    def __init__(
        self,
        *,
        driver: str,
        device: str,
        rate: SampleRate | None = None,
        sync: bool = False,
    ) -> None:
        self.ptr = lib.jackctl_server_create(
            lib.DeviceAcquireFunc(),  # type: ignore
            lib.DeviceReleaseFunc(),  # type: ignore
            lib.DeviceReservationLoop(),  # type: ignore
        )
        self._created = True
        self._opened = False
        self._started = False

        params_jslist = lib.jackctl_server_get_parameters(self.ptr)
        self.params = _get_params_dict(params_jslist)

        self.driver = self.get_driver_by_name(driver)
        self.driver.set_device(device)

        if rate:
            self.driver.set_rate(rate)
        if sync:
            self.set_sync(sync)

    def get_driver_by_name(self, name: str) -> Driver:
        driver_jslist = lib.jackctl_server_get_drivers_list(self.ptr)

        for ptr in lib.JSIter(driver_jslist, POINTER(lib.jackctl_driver_t)):
            driver = Driver(ptr)
            if driver.name == name:
                return driver

        raise RuntimeError(f"Driver not found: {name}")

    def set_sync(self, sync: bool) -> None:
        self.params[b"sync"].value = sync

    def start(self) -> None:
        self._opened = lib.jackctl_server_open(self.ptr, self.driver.ptr)
        if not self._opened:
            raise ServerNotStartedError

        self._started = lib.jackctl_server_start(self.ptr)
        if not self._started:
            raise ServerNotOpenedError

    def stop(self) -> None:
        if self._started:
            lib.jackctl_server_stop(self.ptr)
        self._started = False

        if self._opened:
            lib.jackctl_server_close(self.ptr)
        self._opened = False

    def __del__(self) -> None:
        if getattr(self, "_created", None):
            lib.jackctl_server_destroy(self.ptr)


_dont_garbage_collect: list[Any] = []


def _wrap_error_or_info_callback(
    callback: Callable[[str], None] | None,
) -> lib.PrintFunction:
    if callback:

        def wrapped_callback(message: bytes):
            callback(message.decode())

        cb = lib.PrintFunction(wrapped_callback)
    else:
        cb = lib.PrintFunction()  # type: ignore

    _dont_garbage_collect.append(cb)
    return cb


def set_info_function(callback: Callable[[str], None] | None) -> None:
    lib.jack_set_info_function(_wrap_error_or_info_callback(callback))


def set_error_function(callback: Callable[[str], None] | None) -> None:
    lib.jack_set_error_function(_wrap_error_or_info_callback(callback))
