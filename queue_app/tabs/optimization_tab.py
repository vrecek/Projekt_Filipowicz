import tkinter as tk
from tkinter import messagebox, ttk

from ..dialogs import ParamsDialog
from queue_app.metody.swietlik.optimization import FireflySettings, optimise_system
from queue_app.metody.swietlik.results_view import ResultsPanel
from ..widgets import ParamForm, vertical_separator


def _to_float(text, name):
    try:
        return float(str(text).replace(",", "."))
    except ValueError:
        raise ValueError(f"Nieprawidłowa wartość: {name}.") from None


class OptimizationTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        left = ttk.Frame(top)
        left.pack(side="left", fill="x", expand=True)

        self.params = ParamForm(left, [
            ("Intensywność strumienia zgłoszeń lam", "1.000", 0.1),
            ("Średnia intensywność obsługi", "1.000", 0.1),
            ("Maksymalna liczba zgłoszeń", 6, 1),
        ])
        self.params.pack(fill="x")

        self.optimise_n = tk.BooleanVar(value=False)
        ttk.Checkbutton(left, text="Optymalizuj również N (zakres z ustawień parametrów)",
                        variable=self.optimise_n).pack(anchor="w", pady=(4, 0))

        buttons = ttk.Frame(left)
        buttons.pack(fill="x", pady=(10, 0))
        buttons.columnconfigure(1, weight=1)
        ttk.Button(buttons, text="Ustawienia parametrów",
                   command=self.open_settings).grid(row=0, column=0, padx=(0, 20))
        ttk.Button(buttons, text="Optymalizuj",
                   command=self.optimise).grid(row=0, column=1, sticky="ew")

        vertical_separator(top)

        self.costs = ParamForm(top, [
            ("Koszt C1 (kanał)", "1.00", 0.1),
            ("Koszt C2 (kolejka)", "4.00", 0.1),
            ("Zysk R (obsłużone zgł.)", "10.00", 0.1),
        ])
        self.costs.pack(side="left")

        self.results = ResultsPanel(self)
        self.results.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.settings = ParamsDialog.DEFAULTS.copy()

    def open_settings(self):
        dialog = ParamsDialog(self.winfo_toplevel(), self.settings)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.settings = dialog.result

    def optimise(self):
        try:
            lam = _to_float(self.params.vars[0][0].get(), "lam")
            mu = _to_float(self.params.vars[1][0].get(), "intensywność obsługi")
            n_fixed = int(_to_float(self.params.vars[2][0].get(), "liczba zgłoszeń"))
            c1 = _to_float(self.costs.vars[0][0].get(), "koszt C1")
            c2 = _to_float(self.costs.vars[1][0].get(), "koszt C2")
            revenue = _to_float(self.costs.vars[2][0].get(), "zysk R")
            settings = FireflySettings.from_dict(self.settings)
            result = optimise_system(lam, mu, n_fixed, c1, c2, revenue,
                                     self.optimise_n.get(), settings)
        except ValueError as error:
            messagebox.showerror("Błąd", str(error))
            return
        self.results.show(result)
