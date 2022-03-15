from ctypes import (
    CDLL,
    CFUNCTYPE,
    POINTER,
    Structure,
    Union,
    c_bool,
    c_char,
    c_char_p,
    c_int,
    c_uint,
    c_void_p,
    pointer,
)
from ctypes.util import find_library
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ctypes import _CData

_lib_names = ("libjackserver", "jackserver", "libjackserver64")


def get_library_name():
    for name in _lib_names:
        if result := find_library(name):
            return result

    raise RuntimeError("Couldn't find jackserver library")


lib = CDLL(get_library_name())


class JSList(Structure):
    data: "_CData"
    next: "pointer[JSList]"


JSList_p = POINTER(JSList)
JSList._fields_ = [("data", c_void_p), ("next", JSList_p)]


class jackctl_parameter_t(Structure):
    pass


jackctl_parameter_t_p = POINTER(jackctl_parameter_t)

jackctl_parameter_get_type = lib.jackctl_parameter_get_type
jackctl_parameter_get_type.argtypes = [jackctl_parameter_t_p]
jackctl_parameter_get_type.restype = c_uint

jackctl_parameter_get_name = lib.jackctl_parameter_get_name
jackctl_parameter_get_name.argtypes = [jackctl_parameter_t_p]
jackctl_parameter_get_name.restype = c_char_p


class jackctl_parameter_value(Union):
    _fields_ = [
        ("ui", c_uint),
        ("i", c_int),
        ("c", c_char),
        ("ss", c_char * 128),
        ("b", c_bool),
    ]

    i: int
    ui: int
    c: str
    ss: bytes
    b: bool


jackctl_parameter_value_p = POINTER(jackctl_parameter_value)

jackctl_parameter_set_value = lib.jackctl_parameter_set_value
jackctl_parameter_set_value.argtypes = [
    jackctl_parameter_t_p,
    jackctl_parameter_value_p,
]
jackctl_parameter_set_value.restype = c_bool

jackctl_parameter_get_value = lib.jackctl_parameter_get_value
jackctl_parameter_get_value.argtypes = [jackctl_parameter_t_p]
jackctl_parameter_get_value.restype = jackctl_parameter_value


class jackctl_driver_t(Structure):
    pass


jackctl_driver_t_p = POINTER(jackctl_driver_t)

jackctl_driver_get_parameters = lib.jackctl_driver_get_parameters
jackctl_driver_get_parameters.argtypes = [jackctl_driver_t_p]
jackctl_driver_get_parameters.restype = JSList_p

jackctl_driver_get_name = lib.jackctl_driver_get_name
jackctl_driver_get_name.argtypes = [jackctl_driver_t_p]
jackctl_driver_get_name.restype = c_char_p


class jackctl_server_t(Structure):
    pass


jackctl_server_t_p = POINTER(jackctl_server_t)

OnDeviceAcquire = CFUNCTYPE(c_bool, c_char_p)
OnDeviceRelease = CFUNCTYPE(None, c_char_p)
OnDeviceReservationLoop = CFUNCTYPE(None)

jackctl_server_create2 = lib.jackctl_server_create2
jackctl_server_create2.argtypes = [
    OnDeviceAcquire,
    OnDeviceRelease,
    OnDeviceReservationLoop,
]
jackctl_server_create2.restype = jackctl_server_t_p

jackctl_server_open = lib.jackctl_server_open
jackctl_server_open.argtypes = [jackctl_server_t_p, jackctl_driver_t_p]
jackctl_server_open.restype = c_bool

jackctl_server_start = lib.jackctl_server_start
jackctl_server_start.argtypes = [jackctl_server_t_p]
jackctl_server_start.restype = c_bool

jackctl_server_close = lib.jackctl_server_close
jackctl_server_close.argtypes = [jackctl_server_t_p]
jackctl_server_close.restype = c_bool

jackctl_server_stop = lib.jackctl_server_stop
jackctl_server_stop.argtypes = [jackctl_server_t_p]
jackctl_server_stop.restype = c_bool

jackctl_server_destroy = lib.jackctl_server_destroy
jackctl_server_destroy.argtypes = [jackctl_server_t_p]
jackctl_server_destroy.restype = c_void_p

jackctl_server_get_parameters = lib.jackctl_server_get_parameters
jackctl_server_get_parameters.argtypes = [jackctl_server_t_p]
jackctl_server_get_parameters.restype = JSList_p

jackctl_server_get_drivers_list = lib.jackctl_server_get_drivers_list
jackctl_server_get_drivers_list.argtypes = [jackctl_server_t_p]
jackctl_server_get_drivers_list.restype = JSList_p


PrintFunction = CFUNCTYPE(None, c_char_p)

jack_set_error_function = lib.jack_set_error_function
jack_set_error_function.argtypes = [PrintFunction]
jack_set_error_function.restype = None

jack_set_info_function = lib.jack_set_info_function
jack_set_info_function.argtypes = [PrintFunction]
jack_set_info_function.restype = None
