from __future__ import annotations

import ctypes

from ..handlers.process_attach import AttachedContext

PAGE_EXECUTE_READWRITE = 0x40
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000


class MemoryWriterDriver:
    """Writes the patches built by processors into the game process."""

    def __init__(self, kernel32=None) -> None:
        self._k32 = kernel32 or ctypes.WinDLL("kernel32", use_last_error=True)

    def push(self, ctx: AttachedContext, payload) -> None:
        if isinstance(payload, list) and payload and hasattr(payload[0], "offset"):
            for patch in payload:
                self._write(ctx, patch.offset, self._pack(patch))
        elif isinstance(payload, list):
            for addr, raw in payload:
                self._write(ctx, addr, raw)
        else:
            raise TypeError(f"unsupported payload {type(payload)!r}")

    @staticmethod
    def _pack(patch) -> bytes:
        import struct
        return struct.pack(patch.fmt, patch.value)

    def _write(self, ctx: AttachedContext, address: int, data: bytes) -> None:
        self._k32.VirtualProtectEx(
            ctx.handle, ctypes.c_void_p(address), len(data),
            PAGE_EXECUTE_READWRITE, ctypes.byref(ctypes.c_uint32())
        )
        written = ctypes.c_size_t(0)
        ok = self._k32.WriteProcessMemory(
            ctx.handle, ctypes.c_void_p(address), data, len(data), ctypes.byref(written)
        )
        if not ok or written.value != len(data):
            raise OSError(ctypes.get_last_error(), f"WPM failed @0x{address:X}")