"""Modal 'Dialog' with the optimisation algorithm settings."""

import tkinter as tk
from tkinter import ttk

# (section title, [(settings key, label), ...])
SECTIONS = [
    ("Parametry ogólne", [
        ("iterations", "Ilość iteracji algorytmu"),
        ("max_m", "Maksymalna wartość m:"),
        ("max_n", "Maksymalna wartość N:"),
    ]),
    ("Parametry optymalizacji", [
        ("scouts", "Ilość skautów"),
        ("best_sources", "Ilość najlepszych źródeł"),
        ("elite_sources", "Ilość elitarnych źródeł"),
        ("bees_best", "Ilość pszczół z najlepszymi źródłami"),
        ("bees_elite", "Ilość pszczół z elitarnymi źródłami"),
        ("neighbourhood_searches", "Liczba przeszukiwań w sąsiedztwie"),
    ]),
]


class ParamsDialog(tk.Toplevel):
    DEFAULTS = {
        "iterations": 40,
        "max_m": 100,
        "max_n": 100,
        "scouts": 30,
        "best_sources": 15,
        "elite_sources": 5,
        "bees_best": 10,
        "bees_elite": 15,
        "neighbourhood_searches": 10,
    }

    def __init__(self, parent, values=None):
        super().__init__(parent)
        self.title("Dialog")
        self.resizable(False, False)
        self.transient(parent)

        self.result = None  # dict after OK, None after Cancel
        values = values or self.DEFAULTS
        self._vars = {}

        body = ttk.Frame(self, padding=15)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)

        for row, (title, fields) in enumerate(SECTIONS):
            frame = ttk.LabelFrame(body, text=title, padding=(10, 5))
            frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
            frame.columnconfigure(0, weight=1)
            for i, (key, label) in enumerate(fields):
                var = tk.StringVar(value=str(values[key]))
                self._vars[key] = var
                ttk.Label(frame, text=label).grid(row=i, column=0, sticky="e", padx=(0, 8), pady=4)
                ttk.Spinbox(frame, textvariable=var, from_=0, to=9999,
                            width=7).grid(row=i, column=1, pady=4)

        buttons = ttk.Frame(body)
        buttons.grid(row=len(SECTIONS), column=0, pady=(5, 0))
        ttk.Button(buttons, text="OK", command=self._ok).pack(side="left", padx=8)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="left", padx=8)

        self._center_on(parent)
        self.grab_set()

    def _center_on(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + 40
        self.geometry(f"+{x}+{y}")

    def _ok(self):
        self.result = {key: var.get() for key, var in self._vars.items()}
        self.destroy()
