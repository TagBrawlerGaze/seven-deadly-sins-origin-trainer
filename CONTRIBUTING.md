# Contributing to seven-deadly-sins-origin-trainer

Thanks for helping improve the trainer. A few ground rules so PRs land fast:

## Ground rules
- Reverse-engineering notes for new offsets go in `docs/offsets/` (PR-only, no binary dumps).
- Every new processor must ship with a test in `tests/` and a sample profile in `config/`.
- Do **not** commit `SDSOrigin-Win64-Shipping.exe`, dumps, or any copyrighted assets from the game.
- Keep PRs scoped: one module (`godmode`, `esp_actors`, `drop_rate`, ...) per PR.

## Dev environment
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
python -m cmd.trainer_cli --profile config/default_profile.json
```

## Style
- `ruff check src cmd tests` must be clean.
- Public functions get type hints; keep processors pure (no I/O besides the injected reader).
- Log through `logging.getLogger("sds.trainer.<area>")` — never `print()` inside `src/`.

## Reporting offset drift
When a game patch breaks a signature, open an issue with:
1. Game build string from the launcher.
2. The failing signature/pattern.
3. `trainer.log` excerpt showing the lookup failure.