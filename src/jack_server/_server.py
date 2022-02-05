from __future__ import annotations

from ctypes import POINTER, c_void_p, cast, pointer
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator, Literal, TypeVar

import jack_server._lib as lib

if TYPE_CHECKING:
    from ctypes import _CanCastTo

    _T = TypeVar("_T", bound=_CanCastTo)


def iter_jslist(
    ptr: pointer[lib.JSList], type_: type[_T] = c_void_p
) -> Generator[_T, None, None]:
    cur_ptr = ptr
    while True:
        if not cur_ptr:
            return

        data = cur_ptr.contents.data
        cur_ptr = cur_ptr.contents.next

        yield cast(data, type_)


class Parameter:
    ptr: pointer[lib.jackctl_parameter_t]
    type: Literal[1, 2, 3, 4, 5]

    def __init__(self, ptr: pointer[lib.jackctl_parameter_t]) -> None:
        self.ptr = ptr
        self.type = lib.jackctl_parameter_get_type(self.ptr)

    @property
    def name(self) -> bytes:
        return lib.jackctl_parameter_get_name(self.ptr)

    @property
    def value(self) -> int | str | bytes | bool:
        val = lib.jackctl_parameter_get_value(self.ptr)

        if self.type == 1:
            # JackParamInt
            return val.i
        elif self.type == 2:
            # JackParamUInt
            return val.ui
        elif self.type == 3:
            # JackParamChar
            return val.c
        elif self.type == 4:
            # JackParamString
            return val.ss
        elif self.type == 5:
            # JackParamBool
            return val.b
        else:
            raise NotImplementedError

    @value.setter
    def value(self, val: int | str | bytes | bool) -> None:
        val_obj = lib.jackctl_parameter_value()

        if self.type == 1:
            # JackParamInt
            val_obj.i = int(val)
        elif self.type == 2:
            # JackParamUInt
            val_obj.ui = int(val)
        elif self.type == 3:
            # JackParamChar
            assert isinstance(val, str) and len(val) == 1
            val_obj.c = val
        elif self.type == 4:
            # JackParamString
            assert isinstance(val, bytes)
            val_obj.ss = val
        elif self.type == 5:
            # JackParamBool
            val_obj.b = bool(val)
        else:
            raise NotImplementedError

        lib.jackctl_parameter_set_value(self.ptr, pointer(val_obj))

    def __repr__(self) -> str:
        return f"<jack_server.Parameter name={self.name.decode()!r} value={self.value}>"


def _get_params_from_jslist(jslist: pointer[lib.JSList]) -> dict[bytes, Parameter]:
    params: dict[bytes, Parameter] = {}

    for ptr in iter_jslist(jslist, POINTER(lib.jackctl_parameter_t)):
        param = Parameter(ptr)
        params[param.name] = param

    return params


SampleRate = Literal[44100, 48000]


class Driver:
    ptr: pointer[lib.jackctl_driver_t]
    params: dict[bytes, Parameter]

    def __init__(self, ptr: pointer[lib.jackctl_driver_t]) -> None:
        self.ptr = ptr
        self._set_params()

    def _set_params(self) -> None:
        params_jslist = lib.jackctl_driver_get_parameters(self.ptr)
        self.params = _get_params_from_jslist(params_jslist)

    @property
    def name(self) -> str:
        return lib.jackctl_driver_get_name(self.ptr).decode()

    def set_device(self, name: str) -> None:
        self.params[b"device"].value = name.encode()

    def set_rate(self, rate: SampleRate) -> None:
        self.params[b"rate"].value = rate

    def __repr__(self) -> str:
        return f"<jack_server.Driver name={self.name}>"


class ServerNotStartedError(RuntimeError):  # TODO: Add base jackservererror
    pass


class ServerNotOpenedError(RuntimeError):
    pass


class Server:
    ptr: pointer[lib.jackctl_server_t]
    params: dict[bytes, Parameter]
    driver: Driver
    _created: bool
    _opened: bool
    _started: bool
    _dont_garbage_collect: list[object]

    def __init__(
        self,
        *,
        driver: str,
        device: str | None = None,
        rate: SampleRate | None = None,
        sync: bool = False,
    ) -> None:
        self._created = False
        self._opened = False
        self._started = False
        self._dont_garbage_collect = []

        self._create()
        self._set_params()

        self.driver = self.get_driver_by_name(driver)

        if device:
            self.driver.set_device(device)
        if rate:
            self.driver.set_rate(rate)
        if sync:
            self.set_sync(sync)

    def _create(
        self,
        on_device_acquire: Callable[[bytes], bool] | None = None,
        on_device_release: Callable[[bytes], None] | None = None,
        on_device_reservation_loop: Callable[[], None] | None = None,
    ) -> None:
        if not on_device_acquire:
            on_device_acquire = lambda _: True
        if not on_device_release:
            on_device_release = lambda _: None
        if not on_device_reservation_loop:
            on_device_reservation_loop = lambda: None

        c_on_device_acquire = lib.OnDeviceAcquire(on_device_acquire)
        c_on_device_release = lib.OnDeviceRelease(on_device_release)
        c_on_device_reservation_loop = lib.OnDeviceReservationLoop(
            on_device_reservation_loop
        )

        args = (c_on_device_acquire, c_on_device_release, c_on_device_reservation_loop)
        self._dont_garbage_collect.extend(args)

        self.ptr = lib.jackctl_server_create2(*args)
        self._created = True

    def _open(self) -> None:
        self._opened = lib.jackctl_server_open(self.ptr, self.driver.ptr)
        if not self._opened:
            raise ServerNotOpenedError

    def _start(self) -> None:
        self._started = lib.jackctl_server_start(self.ptr)
        if not self._started:
            raise ServerNotStartedError

    def start(self) -> None:
        self._open()
        self._start()

    def _close(self) -> None:
        if self._opened:
            lib.jackctl_server_close(self.ptr)
            self._opened = False

    def _stop(self) -> None:
        if self._started:
            lib.jackctl_server_stop(self.ptr)
            self._started = False

    def stop(self) -> None:
        self._stop()
        self._close()

    def _destroy(self) -> None:
        if self._created:
            lib.jackctl_server_destroy(self.ptr)

    def __del__(self) -> None:
        self._destroy()

    def _set_params(self) -> None:
        jslist = lib.jackctl_server_get_parameters(self.ptr)
        self.params = _get_params_from_jslist(jslist)

    def get_driver_by_name(self, name: str) -> Driver:
        jslist = lib.jackctl_server_get_drivers_list(self.ptr)

        for ptr in iter_jslist(jslist, POINTER(lib.jackctl_driver_t)):
            driver = Driver(ptr)
            if driver.name == name:
                return driver

        raise RuntimeError(f"Driver not found: {name}")  # TODO: Custom error

    def set_sync(self, sync: bool) -> None:
        self.params[b"sync"].value = sync

    def __repr__(self) -> str:
        return f"<jack_server.Server driver={self.driver.name} started={self._started}>"


_dont_garbage_collect: list[object] = []


def _wrap_error_or_info_callback(
    callback: Callable[[str], None] | None,
) -> lib.PrintFunction:
    if callback:

        @wraps(callback)
        def wrapped_callback(message: bytes):
            callback(message.decode())

    else:

        def wrapped_callback(message: bytes):
            pass

    c_callback = lib.PrintFunction(wrapped_callback)
    _dont_garbage_collect.append(c_callback)
    return c_callback


def set_info_function(callback: Callable[[str], None] | None) -> None:
    lib.jack_set_info_function(_wrap_error_or_info_callback(callback))


def set_error_function(callback: Callable[[str], None] | None) -> None:
    lib.jack_set_error_function(_wrap_error_or_info_callback(callback))
