from __future__ import annotations

from ctypes import pointer
from typing import Literal

import jack_server._lib as lib
from jack_server._parameter import Parameter, get_params_from_jslist

SampleRate = Literal[44100, 48000]


class Driver:
    ptr: pointer[lib.jackctl_driver_t]
    params: dict[str, Parameter]

    def __init__(self, ptr: pointer[lib.jackctl_driver_t]) -> None:
        self.ptr = ptr
        self._set_params()

    def _set_params(self) -> None:
        params_jslist = lib.jackctl_driver_get_parameters(self.ptr)
        self.params = get_params_from_jslist(params_jslist)

    @property
    def name(self) -> str:
        return lib.jackctl_driver_get_name(self.ptr).decode()

    def set_device(self, name: str) -> None:
        self.params["device"].value = name.encode()

    def set_rate(self, rate: SampleRate) -> None:
        self.params["rate"].value = rate

    def __repr__(self) -> str:
        return f"<jack_server.Driver name={self.name}>"
