from __future__ import annotations

from ctypes import pointer

import jack_server._lib as lib
from jack_server._parameter import Parameter, get_params_from_jslist


class Internal:
    ptr: pointer[lib.jackctl_internal_t]  # TODO: Params generic
    params: dict[str, Parameter]

    def __init__(self, ptr: pointer[lib.jackctl_internal_t]) -> None:
        self.ptr = ptr
        self._set_params()

    def _set_params(self) -> None:
        jslist = lib.jackctl_internal_get_parameters(self.ptr)
        self.params = get_params_from_jslist(jslist)

    @property
    def name(self) -> str:
        return lib.jackctl_internal_get_name(self.ptr).decode()

    def set_param_values(self, values: dict[str, int | str | bytes | bool]) -> None:
        for key, value in values.items():
            self.params[key].value = value

    def __repr__(self) -> str:
        return f"<jack_server.Internal name={self.name}>"
