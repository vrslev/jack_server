from __future__ import annotations

from copy import copy
from ctypes import POINTER, pointer
from typing import Callable

import jack_server._lib as lib
from jack_server._driver import Driver, SampleRate
from jack_server._internal import Internal
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


class InternalNotFoundError(JackServerError):
    pass


class InternalNotLoadedError(JackServerError):
    pass


class Server:
    ptr: pointer[lib.jackctl_server_t]
    params: dict[str, Parameter]
    available_drivers: list[Driver]
    available_internals: list[Internal]
    driver: Driver
    _created: bool
    _opened: bool
    _started: bool
    _dont_garbage_collect: list[object]

    def __init__(  # TODO: Allow to change name
        self,
        *,
        name: str = "default",
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
        self.set_name(name)
        self._set_available_drivers()
        self._set_internals()

        # self._set_params()
        # print(self.params["name"])
        self.driver = self._get_driver_by_name(driver)

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

    def _set_available_drivers(self) -> None:
        jslist = lib.jackctl_server_get_drivers_list(self.ptr)
        iterator = iterate_over_jslist(jslist, POINTER(lib.jackctl_driver_t))
        self.available_drivers = [Driver(ptr) for ptr in iterator]

    def _set_internals(self) -> None:
        jslist = lib.jackctl_server_get_internals_list(self.ptr)
        iterator = iterate_over_jslist(jslist, POINTER(lib.jackctl_internal_t))
        self.available_internals = [Internal(ptr) for ptr in iterator]

    def _get_driver_by_name(self, name: str) -> Driver:
        for driver in self.available_drivers:
            if driver.name == name:
                return driver

        raise DriverNotFoundError(f"Driver not found: {name}")

    def set_name(self, name: str) -> None:
        self.params["name"].value = name.encode()

    def set_sync(self, sync: bool) -> None:
        self.params["sync"].value = sync

    def _get_internal_by_name(self, name: str) -> Internal:
        for internal in self.available_internals:
            if internal.name == name:
                return internal

        raise InternalNotFoundError(f"Internal not found: {name}")

    def _load_internal(self, internal: Internal) -> None:
        loaded = lib.jackctl_server_load_internal(self.ptr, internal.ptr)
        if not loaded:
            raise InternalNotLoadedError

    def load_netmanager(
        self,
        *,
        ip: str = "225.3.19.154",
        udp_port: int = 19000,
        auto_connect: bool = False,
        auto_save: bool = False,
    ) -> None:
        internal = copy(self._get_internal_by_name("netmanager"))
        internal.set_param_values(
            {
                "multicast-ip": ip.encode(),
                "udp-net-port": udp_port,
                "auto-connect": auto_connect,
                "auto-save": auto_save,
            }
        )

        self._load_internal(internal)

    def load_netadapter(
        self,
        *,
        ip: str = "225.3.19.154",  # TODO: Check if params are static. Otherwise make DefaultValue()
        udp_port: int = 19000,
        mtu: int = 1500,
        input_ports: int = 2,
        output_ports: int = 2,
        opus: int = -1,
        client_name: str = "'hostname'",
        transport_sync: int = 0,
        latency: int = 5,
        quality: int = 0,
        ring_buffer: int = 32768,
        auto_connect: bool = False,
    ) -> None:
        internal = copy(self._get_internal_by_name("netadapter"))

        if client_name != "'hostname'":
            internal.params["client-name"].value = client_name.encode()

        internal.set_param_values(
            {
                "multicast-ip": ip.encode(),
                "udp-net-port": udp_port,
                "mtu": mtu,
                "input-ports": input_ports,
                "output-ports": output_ports,
                "opus": opus,
                "transport-sync": transport_sync,
                "latency": latency,
                "quality": quality,
                "ring-buffer": ring_buffer,
                "auto-connect": auto_connect,
            }
        )

        self._load_internal(internal)

    def __repr__(self) -> str:
        return f"<jack_server.Server driver={self.driver.name} started={self._started}>"
