from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TrainerProfile:
    name: str
    modules: dict[str, dict] = field(default_factory=dict)
    overlay_driver: str = "tk"
    workers: int = 2
    hotkey_attach: str = "F8"
    hotkey_detach: str = "F9"


def load_profile(path: str | Path) -> TrainerProfile:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return TrainerProfile(
        name=raw.get("name", "default"),
        modules=raw.get("modules", {}),
        overlay_driver=raw.get("overlay_driver", "tk"),
        workers=int(raw.get("workers", 2)),
        hotkey_attach=raw.get("hotkey_attach", "F8"),
        hotkey_detach=raw.get("hotkey_detach", "F9"),
    )