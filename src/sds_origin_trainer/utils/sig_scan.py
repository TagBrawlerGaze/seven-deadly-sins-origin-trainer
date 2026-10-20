from __future__ import annotations

import re

from ..handlers.process_attach import AttachedContext
from ..handlers.memory_reader import MemoryReaderHandler

_SIG_RE = re.compile(rb"[0-9A-F?]{2}")


def parse_pattern(pattern: str) -> bytes:
    return b"".join(b"\x00" if p == "?" else bytes([int(p, 16)])
                     for p in pattern.split())


def scan_signature(reader: MemoryReaderHandler, ctx: AttachedContext,
                   pattern: str, size: int = 0x200000) -> int:
    """Locate a byte signature inside the main module's .text section."""
    needle = parse_pattern(pattern)
    haystack = reader.read(ctx, ctx.module_base, size)
    idx = haystack.find(needle)
    if idx == -1:
        raise LookupError(f"signature not found: {pattern}")
    return ctx.module_base + idx