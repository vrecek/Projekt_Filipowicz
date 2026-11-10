import tkinter as tk
from tkinter import ttk
from ..dialogs import ParamsDialog
from ..widgets import ParamForm, vertical_separator


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

        buttons = ttk.Frame(left)
        buttons.pack(fill="x", pady=(10, 0))
        buttons.columnconfigure(1, weight=1)
        ttk.Button(buttons, text="Ustawienia parametrów",
                   command=self.open_settings).grid(row=0, column=0, padx=(0, 20))
        ttk.Button(buttons, text="Optymalizuj",
                   command=self.optimise).grid(row=0, column=1, sticky="ew")

        vertical_separator(top)

        self.costs = ParamForm(top, [
            ("Koszt C1", "1.00", 0.1),
            ("Koszt C2", "4.00", 0.1),
        ])
        self.costs.pack(side="left")

        output = ttk.LabelFrame(self, text="")
        output.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        self.output = tk.Text(output, state="disabled", relief="flat")
        self.output.pack(fill="both", expand=True)

        self.settings = ParamsDialog.DEFAULTS.copy()

    def open_settings(self):
        dialog = ParamsDialog(self.winfo_toplevel(), self.settings)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.settings = dialog.result



    def optimise(self):
        lam = float(self.params.vars[0][0].get())  # Intensywność strumienia zgłoszeń lam
        mu = float(self.params.vars[1][0].get())  # Średnia intensywność obsługi
        N = int(self.params.vars[2][0].get())  # Maksymalna liczba zgłoszeń

        c1 = float(self.costs.vars[0][0].get())  # Koszt C1
        c2 = float(self.costs.vars[1][0].get())  # Koszt C2

        s = self.settings
        iterations = int(s["iterations"])  # Ilość iteracji algorytmu
        max_m = int(s["max_m"])  # Maksymalna wartość m
        max_n = int(s["max_n"])  # Maksymalna wartość N
        scouts = int(s["scouts"])  # Ilość skautów
        best_sources = int(s["best_sources"])  # Ilość najlepszych źródeł
        elite_sources = int(s["elite_sources"])  # Ilość elitarnych źródeł
        bees_best = int(s["bees_best"])  # Ilość pszczół z najlepszymi źródłami
        bees_elite = int(s["bees_elite"])  # Ilość pszczół z elitarnymi źródłami
        neighbourhood = int(s["neighbourhood_searches"])  # Liczba przeszukiwań w sąsiedztwie

        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "m = 3, N = 6, koszt = 12.5\n")
        self.output.config(state="disabled")
