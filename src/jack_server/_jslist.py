from __future__ import annotations

from ctypes import c_void_p, cast, pointer
from typing import TYPE_CHECKING, Generator, TypeVar

import jack_server._lib as lib

if TYPE_CHECKING:
    from ctypes import _CanCastTo

    _T = TypeVar("_T", bound=_CanCastTo)


def iter_jslist(
    ptr: pointer[lib.JSList], type_: type[_T] = c_void_p
) -> Generator[_T, None, None]:
    cur_ptr = ptr
    while True:
        if not cur_ptr:
            return

        data = cur_ptr.contents.data
        cur_ptr = cur_ptr.contents.next

        yield cast(data, type_)
