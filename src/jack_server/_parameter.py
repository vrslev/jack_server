from __future__ import annotations

from ctypes import pointer
from typing import Literal

import jack_server._lib as lib
from jack_server._jslist import iterate_over_jslist


class Parameter:
    ptr: lib.jackctl_parameter_t_p
    type: Literal[1, 2, 3, 4, 5]

    def __init__(self, ptr: lib.jackctl_parameter_t_p) -> None:
        self.ptr = ptr
        self.type = lib.jackctl_parameter_get_type(self.ptr)

    @property
    def name(self) -> str:
        return lib.jackctl_parameter_get_name(self.ptr).decode()

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
        return f"<jack_server.Parameter name={self.name!r} value={self.value}>"


def get_params_from_jslist(jslist: lib.JSList_p) -> dict[str, Parameter]:
    params: dict[str, Parameter] = {}

    for ptr in iterate_over_jslist(jslist, lib.jackctl_parameter_t_p):
        param = Parameter(ptr)
        params[param.name] = param

    return params
