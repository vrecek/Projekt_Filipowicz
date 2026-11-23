import tkinter as tk
from tkinter import ttk

from queue_app.metody.swietlik.optimization import GAMMA_MODES

SECTIONS = [
    ("Parametry ogólne", [
        ("iterations", "Ilość iteracji algorytmu", 40, 1),
        ("min_m", "Minimalna wartość m:", 1, 1),
        ("max_m", "Maksymalna wartość m:", 100, 1),
        ("min_n", "Minimalna wartość N:", 1, 1),
        ("max_n", "Maksymalna wartość N:", 100, 1),
        ("seed", "Ziarno generatora (0 = losowe):", 0, 1),
    ]),
    ("Parametry optymalizacji", [
        ("fireflies", "Rozmiar roju (ilość świetlików):", 30, 1),
        ("beta0", "Maksimum atrakcyjności β0 ∈ [0, 1]:", 1.0, 0.1),
        ("gamma_mode", "Współczynnik absorpcji:", "adaptacyjne γ0 / r_max²",
         list(GAMMA_MODES)),
        ("gamma", "γ (stałe) lub γ0 ∈ [0, 1] (adaptacyjne):", 0.8, 0.1),
        ("u_min", "Krok losowy: min u (ułamek zakresu):", -0.05, 0.01),
        ("u_max", "Krok losowy: max u (ułamek zakresu):", 0.05, 0.01),
    ]),
]


def _build_defaults():
    return {field[0]: field[2] for _, fields in SECTIONS for field in fields}


class ParamsDialog(tk.Toplevel):
    DEFAULTS = _build_defaults()

    def __init__(self, parent, values=None):
        super().__init__(parent)
        self.title("Dialog")
        self.resizable(False, False)
        self.transient(parent)

        self.result = None
        values = values or self.DEFAULTS
        self._vars = {}

        body = ttk.Frame(self, padding=15)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)

        for row, (title, fields) in enumerate(SECTIONS):
            frame = ttk.LabelFrame(body, text=title, padding=(10, 5))
            frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
            frame.columnconfigure(0, weight=1)
            for i, (key, label, default, step) in enumerate(fields):
                var = tk.StringVar(value=str(values[key]))
                self._vars[key] = var
                ttk.Label(frame, text=label).grid(row=i, column=0, sticky="e", padx=(0, 8), pady=4)
                if isinstance(step, list):
                    widget = ttk.Combobox(frame, textvariable=var, values=step,
                                          state="readonly", width=22)
                else:
                    widget = ttk.Spinbox(frame, textvariable=var, from_=-9999, to=9999,
                                         increment=step, width=8)
                widget.grid(row=i, column=1, pady=4, sticky="w")

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
