"""Entry point: python -m cmd.trainer_cli --profile config/default_profile.json"""
from __future__ import annotations

import argparse
import time

from sds_origin_trainer.config import load_profile
from sds_origin_trainer.drivers import MemoryWriterDriver, OverlayDriver
from sds_origin_trainer.handlers import ProcessAttachHandler, MemoryReaderHandler
from sds_origin_trainer.pipeline import PipelineRunner, TrainerJob
from sds_origin_trainer.processors import StatProcessor, EspProcessor, DropRateProcessor
from sds_origin_trainer.utils import iter_game_pids, setup_logging


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sds-trainer")
    ap.add_argument("--profile", default="config/default_profile.json")
    ap.add_argument("--pid", type=int, default=0)
    args = ap.parse_args(argv)

    setup_logging()
    profile = load_profile(args.profile)

    pid = args.pid or next(iter_game_pids(), 0)
    if not pid:
        print("[!] SDS: Origin not running - launch the game first")
        return 1

    reader = MemoryReaderHandler()
    handler = ProcessAttachHandler()
    processors = {
        "godmode": StatProcessor(reader),
        "inf_mana": StatProcessor(reader),
        "esp_actors": EspProcessor(reader),
        "drop_rate": DropRateProcessor(reader),
    }
    driver = MemoryWriterDriver()

    runner = PipelineRunner(handler, processor=_NullProcessor(), driver=driver,
                            workers=profile.workers)
    runner.start()
    for mod_name, cfg in profile.modules.items():
        if not cfg.get("enabled"):
            continue
        proc = processors[mod_name]
        runner._processor = proc  # swap per-job processor for the demo
        runner.submit(TrainerJob(module=mod_name, pid=pid, params=cfg.get("params", {})))
    time.sleep(1.5)
    runner.stop()
    return 0


class _NullProcessor:
    def build(self, ctx, params):
        return []


if __name__ == "__main__":
    raise SystemExit(main())