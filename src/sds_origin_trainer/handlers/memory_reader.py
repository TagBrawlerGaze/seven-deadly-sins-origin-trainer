from __future__ import annotations

import ctypes

from .process_attach import AttachedContext

PAGE_READABLE = 0x02 | 0x04 | 0x20 | 0x40


class MemoryReaderHandler:
    """Thin wrapper around ReadProcessMemory for resolving the trainer's pointers."""

    def __init__(self, kernel32=None) -> None:
        self._k32 = kernel32 or ctypes.WinDLL("kernel32", use_last_error=True)

    def read(self, ctx: AttachedContext, address: int, size: int) -> bytes:
        buf = (ctypes.c_char * size)()
        read = ctypes.c_size_t(0)
        ok = self._k32.ReadProcessMemory(
            ctx.handle, ctypes.c_void_p(address), buf, size, ctypes.byref(read)
        )
        if not ok or read.value != size:
            raise OSError(ctypes.get_last_error(), f"RPM failed @0x{address:X}")
        return bytes(buf)

    def read_u64(self, ctx: AttachedContext, address: int) -> int:
        return int.from_bytes(self.read(ctx, address, 8), "little")

    def resolve_chain(self, ctx: AttachedContext, base: int, offsets: list[int]) -> int:
        ptr = base
        for off in offsets[:-1]:
            ptr = self.read_u64(ctx, ptr + off)
        return ptr + offsets[-1]