from __future__ import annotations

import json
import socket
import struct
import time

DISCORD_IPC = r"\\.\pipe\discord-ipc-0"


class DiscordRpcDriver:
    """Reports trainer activity in Rich Presence so the repo demo looks alive."""

    OP_HANDSHAKE = 0
    OP_FRAME = 1

    def __init__(self, client_id: str = "1284025588997492736") -> None:
        self._client_id = client_id
        self._sock: socket.socket | None = None
        self._connected_at = 0.0

    def connect(self) -> None:
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.connect(DISCORD_IPC)
        self._send(self.OP_HANDSHAKE, {"v": 1, "client_id": self._client_id})
        self._connected_at = time.time()

    def push(self, _ctx, payload) -> None:
        if not self._sock:
            return
        detail = f"{len(payload)} targets" if isinstance(payload, list) else "patched"
        self._send(self.OP_FRAME, {
            "cmd": "SET_ACTIVITY",
            "args": {"pid": 0, "activity": {
                "details": "SDS: Origin Trainer",
                "state": detail,
                "timestamps": {"start": int(self._connected_at)},
            }},
            "nonce": str(time.time()),
        })

    def _send(self, op: int, data: dict) -> None:
        raw = json.dumps(data).encode()
        header = struct.pack("<II", op, len(raw))
        self._sock.sendall(header + raw)  # type: ignore[union-attr]