from __future__ import annotations

from typing import Callable, Literal, cast

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


class SetByJack:
    def __bool__(self) -> Literal[False]:
        return False


SetByJack_: SetByJack = SetByJack()


class Server:
    ptr: lib.jackctl_server_t_p
    params: dict[str, Parameter]
    available_drivers: list[Driver]
    driver: Driver
    _created: bool
    _opened: bool
    _started: bool
    _dont_garbage_collect: list[object]

    def __init__(
        self,
        *,
        name: str | SetByJack = SetByJack_,
        driver: str,
        device: str | SetByJack = SetByJack_,
        rate: SampleRate | SetByJack = SetByJack_,
        period: int | SetByJack = SetByJack_,
        sync: bool | SetByJack = SetByJack_,
    ) -> None:
        self._created = False
        self._opened = False
        self._started = False
        self._dont_garbage_collect = []

        self._create()
        self._init_params()
        self._init_available_drivers()

        self.driver = self.get_driver_by_name(driver)

        if name:
            self.name = name
        if device:
            self.driver.device = device
        if rate:
            self.driver.rate = rate
        if period:
            self.driver.period = period
        if sync:
            self.sync = sync

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

    def _close(self) -> None:
        if self._opened:
            lib.jackctl_server_close(self.ptr)
            self._opened = False

    def _stop(self) -> None:
        if self._started:
            lib.jackctl_server_stop(self.ptr)
            self._started = False

    def _destroy(self) -> None:
        if self._created:
            lib.jackctl_server_destroy(self.ptr)
            self._created = False

    def start(self) -> None:
        self._open()
        self._start()

    def stop(self) -> None:
        self._stop()
        self._close()

    def __del__(self) -> None:
        self._destroy()

    def _init_params(self) -> None:
        jslist = lib.jackctl_server_get_parameters(self.ptr)
        self.params = get_params_from_jslist(jslist)

    def _init_available_drivers(self) -> None:
        jslist = lib.jackctl_server_get_drivers_list(self.ptr)
        iterator = iterate_over_jslist(jslist, lib.jackctl_driver_t_p)
        self.available_drivers = [Driver(ptr) for ptr in iterator]

    def get_driver_by_name(self, name: str) -> Driver:
        for driver in self.available_drivers:
            if driver.name == name:
                return driver

        raise DriverNotFoundError(f"Driver not found: {name}")

    @property
    def name(self) -> str:
        return cast(bytes, self.params["name"].value).decode()

    @name.setter
    def name(self, __value: str) -> None:
        self.params["name"].value = __value.encode()

    @property
    def sync(self) -> bool:
        return cast(bool, self.params["sync"].value)

    @sync.setter
    def sync(self, __value: bool) -> None:
        self.params["sync"].value = __value

    def __repr__(self) -> str:
        return f"<jack_server.Server driver={self.driver.name} started={self._started}>"
