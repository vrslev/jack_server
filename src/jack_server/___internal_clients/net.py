# type: ignore
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
    c_uint32,
)
from ctypes.util import find_library

lib_name = find_library("libjacknet")

if not lib_name:
    raise RuntimeError("Couldn't find libjacknet")

lib = CDLL(lib_name)


class jack_slave_t(Structure):
    _fields_ = [
        ("audio_input", c_int),
        ("audio_output", c_int),
        ("midi_input", c_int),
        ("midi_output", c_int),
        ("mtu", c_int),
        ("time_out", c_int),
        ("encoder", c_int),
        ("kbps", c_int),
        ("latency", c_int),
    ]


class jack_master_t(Structure):
    _fields_ = [
        ("audio_input", c_int),
        ("audio_output", c_int),
        ("midi_input", c_int),
        ("midi_output", c_int),
        ("buffer_size", c_uint32),
        ("sample_rate", c_uint32),
        ("master_name", c_char * 256),
        ("time_out", c_int),
        ("partial_cycle", c_int),
    ]


class jack_net_slave_t(Structure):
    pass


class jack_net_master_t(Structure):
    pass


jack_net_slave_open = lib.jack_net_slave_open
jack_net_slave_open.argtypes = [c_char_p, c_int, c_char_p, jack_slave_t, jack_master_t]
jack_net_slave_open.restype = POINTER(jack_net_slave_t)

jack_net_master_open = lib.jack_net_master_open
jack_net_master_open.argtypes = [
    c_char_p,
    c_int,
    POINTER(jack_master_t),
    POINTER(jack_slave_t),
]
jack_net_master_open.restype = POINTER(jack_net_master_t)

master = jack_master_t(
    audio_input=1,
    audio_output=1,
    midi_input=1,
    midi_output=2,
    buffer_size=10,
    sample_rate=10,
    master_name=b"tt",
    time_out=1,
    partial_cycle=10,
)
slave = jack_slave_t(
    audio_input=1,
    audio_output=1,
    midi_input=1,
    midi_output=2,
    mtu=1,
    time_out=1,
    encoder=1,
    kbps=1,
    latency=1,
)

jack_net_master_open(b"", 1, master, slave)
