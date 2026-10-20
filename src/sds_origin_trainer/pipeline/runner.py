from __future__ import annotations

import logging
import threading
import time
from queue import Queue, Empty

from .job import TrainerJob, JobState

log = logging.getLogger("sds.trainer.runner")


class PipelineRunner:
    """Worker pool that drains the job queue through ingest -> process -> drive."""

    def __init__(self, handler, processor, driver, workers: int = 2) -> None:
        self._queue: Queue[TrainerJob] = Queue()
        self._handler = handler
        self._processor = processor
        self._driver = driver
        self._workers = workers
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    def submit(self, job: TrainerJob) -> None:
        log.info("queue job=%s module=%s pid=%d", job.job_id, job.module, job.pid)
        self._queue.put(job)

    def start(self) -> None:
        for i in range(self._workers):
            t = threading.Thread(target=self._loop, name=f"sds-worker-{i}", daemon=True)
            t.start()
            self._threads.append(t)

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                job = self._queue.get(timeout=0.5)
            except Empty:
                continue
            try:
                ctx = self._handler.attach(job)
                job.transition(JobState.RUNNING)
                payload = self._processor.build(ctx, job.params)
                self._driver.push(ctx, payload)
                job.transition(JobState.DONE)
            except Exception as exc:  # noqa: BLE001
                job.errors.append(repr(exc))
                job.state = JobState.FAILED
                log.exception("job %s failed", job.job_id)

    def stop(self) -> None:
        self._stop.set()
        for t in self._threads:
            t.join(timeout=2.0)