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
from typing import TYPE_CHECKING, Callable, Literal

if TYPE_CHECKING:
    from ctypes import _CData


lib_name = find_library("libjackserver")

if not lib_name:
    lib_name = find_library("jackserver")

if not lib_name:
    raise RuntimeError("Couldn't find libjackserver")

lib = CDLL(lib_name)


class JSList(Structure):
    data: "_CData"
    next: "pointer[JSList]"


JSList._fields_ = [("data", c_void_p), ("next", POINTER(JSList))]


class jackctl_parameter_t(Structure):
    pass


jackctl_parameter_get_type: Callable[
    ["pointer[jackctl_parameter_t]"], Literal[1, 2, 3, 4, 5]
] = lib.jackctl_parameter_get_type
jackctl_parameter_get_type.argtypes = [POINTER(jackctl_parameter_t)]
jackctl_parameter_get_type.restype = c_uint

jackctl_parameter_get_name: Callable[
    ["pointer[jackctl_parameter_t]"], bytes
] = lib.jackctl_parameter_get_name
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
    ["pointer[jackctl_parameter_t]", "pointer[jackctl_parameter_value]"], bool
] = lib.jackctl_parameter_set_value
jackctl_parameter_set_value.argtypes = [
    POINTER(jackctl_parameter_t),
    POINTER(jackctl_parameter_value),
]
jackctl_parameter_set_value.restype = c_bool

jackctl_parameter_get_value: Callable[
    ["pointer[jackctl_parameter_t]"], jackctl_parameter_value
] = lib.jackctl_parameter_get_value
jackctl_parameter_get_value.argtypes = [POINTER(jackctl_parameter_t)]
jackctl_parameter_get_value.restype = jackctl_parameter_value


class jack_driver_desc_t(Structure):
    pass


class jackctl_driver_t(Structure):
    _fields_ = [
        ("desc_ptr", POINTER(jack_driver_desc_t)),
        ("parameters", POINTER(JSList)),
        ("infos", POINTER(JSList)),
    ]

    desc_ptr: "pointer[jack_driver_desc_t]"
    parameters: "pointer[JSList]"
    infos: "pointer[JSList]"


jackctl_driver_get_parameters: Callable[
    ["pointer[jackctl_driver_t]"], "pointer[JSList]"
] = lib.jackctl_driver_get_parameters
jackctl_driver_get_parameters.argtypes = [POINTER(jackctl_driver_t)]
jackctl_driver_get_parameters.restype = POINTER(JSList)

jackctl_driver_get_name: Callable[
    ["pointer[jackctl_driver_t]"], bytes
] = lib.jackctl_driver_get_name
jackctl_driver_get_name.argtypes = [POINTER(jackctl_driver_t)]
jackctl_driver_get_name.restype = c_char_p


class jackctl_internal_t(Structure):
    _fields_ = [
        ("desc_ptr", POINTER(jack_driver_desc_t)),
        ("parameters", POINTER(JSList)),
        ("refnum", c_int),
    ]

    desc_ptr: "pointer[jack_driver_desc_t]"
    parameters: "pointer[JSList]"
    refnum: int


jackctl_internal_get_name: Callable[
    ["pointer[jackctl_internal_t]"], bytes
] = lib.jackctl_internal_get_name
jackctl_internal_get_name.argtypes = [POINTER(jackctl_internal_t)]
jackctl_internal_get_name.restype = c_char_p

jackctl_internal_get_parameters: Callable[
    ["pointer[jackctl_internal_t]"], "pointer[JSList]"
] = lib.jackctl_internal_get_parameters
jackctl_internal_get_parameters.argtypes = [POINTER(jackctl_internal_t)]
jackctl_internal_get_parameters.restype = POINTER(JSList)


class jackctl_server_t(Structure):
    pass


OnDeviceAcquire = CFUNCTYPE(c_bool, c_char_p)
OnDeviceRelease = CFUNCTYPE(None, c_char_p)
OnDeviceReservationLoop = CFUNCTYPE(None)

jackctl_server_create2: Callable[
    [OnDeviceAcquire, OnDeviceRelease, OnDeviceReservationLoop],
    "pointer[jackctl_server_t]",
] = lib.jackctl_server_create2
jackctl_server_create2.argtypes = [
    OnDeviceAcquire,
    OnDeviceRelease,
    OnDeviceReservationLoop,
]
jackctl_server_create2.restype = POINTER(jackctl_server_t)

jackctl_server_open: Callable[
    ["pointer[jackctl_server_t]", "pointer[jackctl_driver_t]"], bool
] = lib.jackctl_server_open
jackctl_server_open.argtypes = [POINTER(jackctl_server_t), POINTER(jackctl_driver_t)]
jackctl_server_open.restype = c_bool

jackctl_server_start: Callable[
    ["pointer[jackctl_server_t]"], bool
] = lib.jackctl_server_start
jackctl_server_start.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_start.restype = c_bool

jackctl_server_close: Callable[
    ["pointer[jackctl_server_t]"], bool
] = lib.jackctl_server_close
jackctl_server_close.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_close.restype = c_bool

jackctl_server_stop: Callable[
    ["pointer[jackctl_server_t]"], bool
] = lib.jackctl_server_stop
jackctl_server_stop.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_stop.restype = c_bool

jackctl_server_destroy: Callable[
    ["pointer[jackctl_server_t]"], None
] = lib.jackctl_server_destroy
jackctl_server_destroy.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_destroy.restype = c_void_p

jackctl_server_get_parameters: Callable[
    ["pointer[jackctl_server_t]"], "pointer[JSList]"
] = lib.jackctl_server_get_parameters
jackctl_server_get_parameters.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_get_parameters.restype = POINTER(JSList)

jackctl_server_get_drivers_list: Callable[
    ["pointer[jackctl_server_t]"], "pointer[JSList]"
] = lib.jackctl_server_get_drivers_list
jackctl_server_get_drivers_list.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_get_drivers_list.restype = POINTER(JSList)

jackctl_server_get_internals_list: Callable[
    ["pointer[jackctl_server_t]"], "pointer[JSList]"
] = lib.jackctl_server_get_internals_list
jackctl_server_get_internals_list.argtypes = [POINTER(jackctl_server_t)]
jackctl_server_get_internals_list.restype = POINTER(JSList)

jackctl_server_load_internal: Callable[
    ["pointer[jackctl_server_t]", "pointer[jackctl_internal_t]"], bool
] = lib.jackctl_server_load_internal
jackctl_server_load_internal.argtypes = [
    POINTER(jackctl_server_t),
    POINTER(jackctl_internal_t),
]
jackctl_server_load_internal.restype = c_bool


PrintFunction = CFUNCTYPE(None, c_char_p)

jack_set_error_function: Callable[[PrintFunction], None] = lib.jack_set_error_function
jack_set_error_function.argtypes = [PrintFunction]
jack_set_error_function.restype = None

jack_set_info_function: Callable[[PrintFunction], None] = lib.jack_set_info_function
jack_set_info_function.argtypes = [PrintFunction]
jack_set_info_function.restype = None
