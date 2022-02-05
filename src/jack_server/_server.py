from __future__ import annotations

from ctypes import POINTER, pointer
from typing import Callable

import jack_server._lib as lib
from jack_server._driver import Driver, SampleRate
from jack_server._jslist import iterate_over_jslist
from jack_server._parameter import Parameter, get_params_from_jslist


class JackServerError(RuntimeError):
    pass


class ServerNotStartedError(JackServerError):
    pass


class ServerNotOpenedError(JackServerError):
    pass


class DriverNotFoundError(JackServerError):
    pass


class Server:
    ptr: pointer[lib.jackctl_server_t]
    params: dict[str, Parameter]
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
            raise ServerNotOpenedError("Server couldn't be opened")

    def _start(self) -> None:
        self._started = lib.jackctl_server_start(self.ptr)
        if not self._started:
            raise ServerNotStartedError("Server couldn't be started")

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
        self.params = get_params_from_jslist(jslist)

    def get_driver_by_name(self, name: str) -> Driver:
        jslist = lib.jackctl_server_get_drivers_list(self.ptr)

        for ptr in iterate_over_jslist(jslist, POINTER(lib.jackctl_driver_t)):
            driver = Driver(ptr)
            if driver.name == name:
                return driver

        raise DriverNotFoundError(f"Driver not found: {name}")

    def set_sync(self, sync: bool) -> None:
        self.params["sync"].value = sync

    def __repr__(self) -> str:
        return f"<jack_server.Server driver={self.driver.name} started={self._started}>"
