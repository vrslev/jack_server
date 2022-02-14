from __future__ import annotations

from ctypes import c_void_p, cast
from typing import TYPE_CHECKING, Iterable, TypeVar

import jack_server._lib as lib

if TYPE_CHECKING:
    from ctypes import _CanCastTo

    _T = TypeVar("_T", bound=_CanCastTo)


def iterate_over_jslist(ptr: lib.JSList_p, type: type[_T] = c_void_p) -> Iterable[_T]:
    cur_ptr = ptr

    while cur_ptr:
        data = cur_ptr.contents.data
        cur_ptr = cur_ptr.contents.next
        yield cast(data, type)
