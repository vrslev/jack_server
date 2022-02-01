# TODO: Use CFFI
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
    cast,
)
from ctypes.util import find_library
from typing import Any, Callable, Literal

lib_name = find_library("libjackserver")

if not lib_name:
    lib_name = find_library("jackserver")

if not lib_name:
    raise RuntimeError("Couldn't find libjackserver")

lib = CDLL(lib_name)


class JSList(Structure):
    pass


JSList._fields_ = [("data", c_void_p), ("next", POINTER(JSList))]


class JSIter:
    def __init__(self, ptr: Any, type_: Any = c_void_p) -> None:
        self.ptr = ptr
        self.type = type_

    def __iter__(self):
        return self

    def __next__(self):
        if not self.ptr:
            raise StopIteration

        retval = self.ptr.contents.data
        self.ptr = self.ptr.contents.next
        return cast(retval, self.type)


class jackctl_parameter_t(Structure):
    pass


jackctl_parameter_get_type: Callable[
    [Any], Literal[1, 2, 3, 4, 5]
] = lib.jackctl_parameter_get_type
jackctl_parameter_get_type.argtypes = [POINTER(jackctl_parameter_t)]
jackctl_parameter_get_type.restype = c_uint

jackctl_parameter_get_name: Callable[[Any], bytes] = lib.jackctl_parameter_get_name
jackctl_parameter_get_name.argtypes = [POINTER(jackctl_parameter_t)]
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


jackctl_parameter_set_value: Callable[
    [Any, Any], bool
] = lib.jackctl_parameter_set_value
jackctl_parameter_set_value.argtypes = [
    POINTER(jackctl_parameter_t),
    POINTER(jackctl_parameter_value),
]
jackctl_parameter_set_value.restype = c_bool

jackctl_parameter_get_value: Callable[
    [Any], jackctl_parameter_value
] = lib.jackctl_parameter_get_value
jackctl_parameter_get_value.argtypes = [POINTER(jackctl_parameter_t)]
jackctl_parameter_get_value.restype = jackctl_parameter_value


class jackctl_driver_t(Structure):
    pass


jackctl_driver_get_parameters: Callable[[Any], Any] = lib.jackctl_driver_get_parameters
jackctl_driver_get_parameters.argtypes = [POINTER(jackctl_driver_t)]
jackctl_driver_get_parameters.restype = POINTER(JSList)

jackctl_driver_get_name: Callable[[Any], bytes] = lib.jackctl_driver_get_name
jackctl_driver_get_name.argtypes = [POINTER(jackctl_driver_t)]
jackctl_driver_get_name.restype = c_char_p


class jackctl_server_t(Structure):
    pass


jackctl_server_get_drivers_list: Callable[
    [Any], Any
] = lib.jackctl_server_get_drivers_list
jackctl_server_get_drivers_list.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_get_drivers_list.restype = POINTER(JSList)

jackctl_server_start: Callable[[Any], bool] = lib.jackctl_server_start
jackctl_server_start.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_start.restype = c_bool

jackctl_server_open: Callable[[Any, Any], bool] = lib.jackctl_server_open
jackctl_server_open.argtypes = [POINTER(jackctl_server_t), POINTER(jackctl_driver_t)]
jackctl_server_open.restype = c_bool

DeviceAcquireFunc = CFUNCTYPE(c_bool, c_char_p)
DeviceReleaseFunc = CFUNCTYPE(None, c_char_p)
DeviceReservationLoop = CFUNCTYPE(None)

jackctl_server_create: Callable[
    [Callable[..., Any], Callable[..., Any], Callable[..., Any]], Any
] = lib.jackctl_server_create2
jackctl_server_create.argtypes = [
    DeviceAcquireFunc,
    DeviceReleaseFunc,
    DeviceReservationLoop,
]
jackctl_server_create.restype = POINTER(jackctl_server_t)

jackctl_server_stop: Callable[[Any], bool] = lib.jackctl_server_stop
jackctl_server_stop.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_stop.restype = c_bool

jackctl_server_close: Callable[[Any], bool] = lib.jackctl_server_close
jackctl_server_close.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_close.restype = c_bool

jackctl_server_destroy: Callable[[Any], None] = lib.jackctl_server_destroy
jackctl_server_destroy.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_destroy.restype = c_void_p

jackctl_server_get_parameters: Callable[[Any], Any] = lib.jackctl_server_get_parameters
jackctl_server_get_parameters.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_get_parameters.restype = POINTER(JSList)


PrintFunction = CFUNCTYPE(None, c_char_p)

jack_set_error_function: Callable[
    [Callable[[bytes], None]], None
] = lib.jack_set_error_function
jack_set_error_function.argtypes = [PrintFunction]
jack_set_error_function.restype = None

jack_set_info_function: Callable[
    [Callable[[bytes], None]], None
] = lib.jack_set_info_function
jack_set_info_function.argtypes = [PrintFunction]
jack_set_info_function.restype = None
