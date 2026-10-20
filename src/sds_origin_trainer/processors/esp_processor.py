from __future__ import annotations

import struct

from ..handlers.process_attach import AttachedContext
from ..handlers.memory_reader import MemoryReaderHandler

ENTITY_LIST_OFFSET = 0x0311C4A0
ENTITY_STRIDE = 0x1C0
MAX_ENTITIES = 512


class EspProcessor:
    """Walks the actor list and emits ESP boxes + name tags for nearby mobs/NPCs."""

    def __init__(self, reader: MemoryReaderHandler) -> None:
        self._reader = reader

    def build(self, ctx: AttachedContext, params: dict) -> list[dict]:
        max_dist = float(params.get("max_dist", 150.0))
        show_names = bool(params.get("names", True))
        world = self._reader.read_u64(ctx, ctx.module_base + ENTITY_LIST_OFFSET)
        if not world:
            return []
        out: list[dict] = []
        for i in range(MAX_ENTITIES):
            slot = self._reader.read(ctx, world + i * ENTITY_STRIDE, 0x40)
            actor = struct.unpack_from("<Q", slot, 0x00)[0]
            if not actor:
                continue
            pos = struct.unpack_from("<fff", slot, 0x10)
            hp = struct.unpack_from("<f", slot, 0x28)[0]
            dist = (pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2) ** 0.5
            if dist > max_dist:
                continue
            entry = {"addr": actor, "pos": pos, "hp": hp, "dist": round(dist, 2)}
            if show_names:
                entry["name"] = self._read_name(ctx, actor)
            out.append(entry)
        return out

    def _read_name(self, ctx: AttachedContext, actor: int) -> str:
        try:
            name_ptr = self._reader.read_u64(ctx, actor + 0x48)
            raw = self._reader.read(ctx, name_ptr, 64)
            return raw.split(b"\x00", 1)[0].decode("utf-16-le", "ignore")
        except OSError:
            return "?"