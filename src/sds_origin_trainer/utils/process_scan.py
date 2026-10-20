from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
from typing import Iterator

TARGET = "sdsorigin-win64-shipping.exe"


def iter_game_pids() -> Iterator[int]:
    """Yield PIDs whose executable matches the Seven Deadly Sins: Origin client."""
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    TH32CS_SNAPPROCESS = 0x02
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == wt.HANDLE(-1).value:
        return
    try:
        entry = (ctypes.c_byte * 568)()
        ctypes.memmove(entry, ctypes.byref(ctypes.c_uint32(568)), 4)
        if not k32.Process32First(snap, entry):
            return
        while True:
            name = bytes(entry[44:44 + 260]).split(b"\x00", 1)[0].decode("ascii", "ignore")
            if name.lower() == TARGET:
                yield int.from_bytes(bytes(entry[8:12]), "little")
            if not k32.Process32Next(snap, entry):
                break
    finally:
        k32.CloseHandle(snap)