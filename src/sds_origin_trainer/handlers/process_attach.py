from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import logging

from ..pipeline.job import TrainerJob

log = logging.getLogger("sds.trainer.attach")

PROCESS_ALL_ACCESS = 0x1F0FFF
TARGET_IMAGE = "SDSOrigin-Win64-Shipping.exe"


class AttachedContext:
    __slots__ = ("pid", "handle", "module_base", "job_id")

    def __init__(self, pid: int, handle: int, module_base: int, job_id: str) -> None:
        self.pid = pid
        self.handle = handle
        self.module_base = module_base
        self.job_id = job_id


class ProcessAttachHandler:
    """Opens a handle to the Seven Deadly Sins: Origin game process."""

    def __init__(self, kernel32=None) -> None:
        self._k32 = kernel32 or ctypes.WinDLL("kernel32", use_last_error=True)

    def attach(self, job: TrainerJob) -> AttachedContext:
        handle = self._k32.OpenProcess(PROCESS_ALL_ACCESS, False, job.pid)
        if not handle:
            raise OSError(ctypes.get_last_error(), "OpenProcess failed")
        base = self._module_base(job.pid, TARGET_IMAGE)
        log.info("attached pid=%d base=0x%X", job.pid, base)
        return AttachedContext(job.pid, handle, base, job.job_id)

    def _module_base(self, pid: int, module_name: str) -> int:
        # snapshot-based module walk; returns 0 if not found
        TH32CS_SNAPMODULE = 0x00000008
        snap = self._k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
        if snap == wt.HANDLE(-1).value:
            return 0
        try:
            entry = (ctypes.c_byte * 1084)()
            ctypes.memmove(entry, ctypes.byref(ctypes.c_uint32(1084)), 4)
            if not self._k32.Module32First(snap, entry):
                return 0
            while True:
                name = bytes(entry[32:32 + 260]).split(b"\x00", 1)[0].decode("mbcs", "ignore")
                if name.lower() == module_name.lower():
                    return int.from_bytes(bytes(entry[12:16]), "little")
                if not self._k32.Module32Next(snap, entry):
                    return 0
        finally:
            self._k32.CloseHandle(snap)