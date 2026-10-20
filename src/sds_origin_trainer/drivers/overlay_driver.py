from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class OverlayDriver:
    """Minimal top-most overlay used by the ESP processor to draw boxes."""

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-transparentcolor", "black")
        self._root.configure(bg="black")
        self._canvas = tk.Canvas(self._root, bg="black", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)
        self._root.geometry(f"{self._root.winfo_screenwidth()}x{self._root.winfo_screenheight()}+0+0")
        self._items: list[int] = []

    def push(self, _ctx, boxes: list[dict]) -> None:
        for item in self._items:
            self._canvas.delete(item)
        self._items.clear()
        for box in boxes:
            x, y = self._project(box["pos"])
            self._items.append(self._canvas.create_text(x, y, text=box.get("name", "mob"),
                                                         fill="#e63946", font=("Consolas", 9)))
            self._items.append(self._canvas.create_rectangle(x - 20, y - 40, x + 20, y + 4,
                                                             outline="#e63946"))

    def _project(self, pos) -> tuple[int, int]:
        w = self._root.winfo_screenwidth()
        h = self._root.winfo_screenheight()
        return int(w / 2 + pos[0] * 4), int(h / 2 - pos[1] * 4)

    def pump(self) -> None:
        self._root.update_idletasks()
        self._root.update()