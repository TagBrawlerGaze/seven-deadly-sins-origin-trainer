from __future__ import annotations

from ..handlers.process_attach import AttachedContext
from ..handlers.memory_reader import MemoryReaderHandler

DROP_TABLE_OFFSET = 0x02D9A1C0


class DropRateProcessor:
    """Overrides the loot table multiplier used by dungeon and raid rewards."""

    def __init__(self, reader: MemoryReaderHandler) -> None:
        self._reader = reader

    def build(self, ctx: AttachedContext, params: dict) -> list[tuple[int, bytes]]:
        mult = float(params.get("drop_mult", 1.0))
        if not 0.0 <= mult <= 500.0:
            raise ValueError("drop_mult out of supported range")
        table = self._reader.read_u64(ctx, ctx.module_base + DROP_TABLE_OFFSET)
        if not table:
            raise RuntimeError("drop table not resolved - is the player in a dungeon?")
        return [(table + 0x10, mult.to_bytes(4, "little"))]