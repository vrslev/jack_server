from __future__ import annotations

from functools import wraps
from typing import Callable

import jack_server._lib as lib

_dont_garbage_collect: list[object] = []


def _wrap_error_or_info_callback(
    callback: Callable[[str], None] | None
) -> lib.PrintFunction:
    if callback:

        @wraps(callback)
        def wrapped_callback(message: bytes) -> None:
            callback(message.decode())

    else:

        def wrapped_callback(message: bytes) -> None:
            pass

    c_callback = lib.PrintFunction(wrapped_callback)
    _dont_garbage_collect.append(c_callback)
    return c_callback


def set_info_function(callback: Callable[[str], None] | None) -> None:
    lib.jack_set_info_function(_wrap_error_or_info_callback(callback))


def set_error_function(callback: Callable[[str], None] | None) -> None:
    lib.jack_set_error_function(_wrap_error_or_info_callback(callback))
