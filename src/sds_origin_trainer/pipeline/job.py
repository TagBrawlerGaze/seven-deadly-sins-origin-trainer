from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class JobState(Enum):
    QUEUED = auto()
    ATTACHING = auto()
    RUNNING = auto()
    PAUSED = auto()
    FAILED = auto()
    DONE = auto()


@dataclass
class TrainerJob:
    """A single cheat module run against a live SDS: Origin process."""

    module: str                      # e.g. "godmode", "inf_mana", "esp_actors"
    pid: int
    params: dict[str, Any] = field(default_factory=dict)
    state: JobState = JobState.QUEUED
    job_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: float = field(default_factory=time.time)
    errors: list[str] = field(default_factory=list)

    def transition(self, new_state: JobState) -> None:
        allowed = {
            JobState.QUEUED: {JobState.ATTACHING, JobState.FAILED},
            JobState.ATTACHING: {JobState.RUNNING, JobState.FAILED},
            JobState.RUNNING: {JobState.PAUSED, JobState.DONE, JobState.FAILED},
            JobState.PAUSED: {JobState.RUNNING, JobState.DONE},
        }
        if new_state not in allowed.get(self.state, set()):
            raise ValueError(f"illegal transition {self.state.name} -> {new_state.name}")
        self.state = new_state