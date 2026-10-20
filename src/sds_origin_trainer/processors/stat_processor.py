from __future__ import annotations

from dataclasses import dataclass

from ..handlers.process_attach import AttachedContext
from ..handlers.memory_reader import MemoryReaderHandler

# offsets confirmed against SDSOrigin-Win64-Shipping.exe build 2026.02
PLAYER_STATS_CHAIN = [0x02F14A80, 0x18, 0x2B0, 0x48, 0x10]


@dataclass
class StatPatch:
    offset: int
    fmt: str
    value: float | int


class StatProcessor:
    """Builds stat patches for godmode / inf-mana / one-hit-kill modules."""

    def __init__(self, reader: MemoryReaderHandler) -> None:
        self._reader = reader

    def build(self, ctx: AttachedContext, params: dict) -> list[StatPatch]:
        base = self._reader.resolve_chain(ctx, ctx.module_base + PLAYER_STATS_CHAIN[0],
                                          PLAYER_STATS_CHAIN[1:])
        patches: list[StatPatch] = []
        if params.get("godmode"):
            patches.append(StatPatch(0x00, "<f", 9_999_999.0))
        if params.get("inf_mana"):
            patches.append(StatPatch(0x04, "<f", 65_535.0))
        if (mult := params.get("dmg_mult")):
            patches.append(StatPatch(0x08, "<f", float(mult)))
        if not patches:
            raise ValueError("no stat options requested")
        return patches