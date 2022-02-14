from __future__ import annotations

from typing import Literal, cast

import jack_server._lib as lib
from jack_server._parameter import Parameter, get_params_from_jslist

SampleRate = Literal[44100, 48000]


class Driver:
    ptr: lib.jackctl_driver_t_p
    params: dict[str, Parameter]

    def __init__(self, ptr: lib.jackctl_driver_t_p) -> None:
        self.ptr = ptr
        self._init_params()

    def _init_params(self) -> None:
        params_jslist = lib.jackctl_driver_get_parameters(self.ptr)
        self.params = get_params_from_jslist(params_jslist)

    @property
    def name(self) -> str:
        return lib.jackctl_driver_get_name(self.ptr).decode()

    @property
    def device(self) -> str:
        return cast(bytes, self.params["device"].value).decode()

    @device.setter
    def device(self, __value: str) -> None:
        self.params["device"].value = __value.encode()

    @property
    def rate(self) -> SampleRate:
        return cast(SampleRate, self.params["rate"].value)

    @rate.setter
    def rate(self, __value: SampleRate) -> None:
        self.params["rate"].value = __value

    @property
    def period(self) -> int:
        return cast(int, self.params["period"].value)

    @period.setter
    def period(self, __value: int) -> None:
        self.params["period"].value = __value

    def __repr__(self) -> str:
        return f"<jack_server.Driver name={self.name}>"
