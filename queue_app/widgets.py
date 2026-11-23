import tkinter as tk
from tkinter import ttk

from .constants import RESULT_ROWS


class ParamForm(ttk.Frame):
    def __init__(self, parent, fields, columns=1, headers=None):
        super().__init__(parent)
        self.vars = []

        first_row = 0
        if headers:
            for j, text in enumerate(headers):
                ttk.Label(self, text=text).grid(row=0, column=j, sticky="w", padx=(0 if j == 0 else 10, 0))
            first_row = 1

        for i, (label, default, step) in enumerate(fields):
            row_vars = []
            for j in range(columns):
                var = tk.StringVar(value=str(default))
                ttk.Spinbox(self, textvariable=var, from_=0, to=9999,
                            increment=step, width=10).grid(
                    row=first_row + i, column=j, pady=5, sticky="w",
                    padx=(0, 10))
                row_vars.append(var)
            self.vars.append(row_vars)
            ttk.Label(self, text=label).grid(row=first_row + i, column=columns, sticky="w")


class RangePanel(ttk.Frame):
    def __init__(self, parent, button_text, command):
        super().__init__(parent)

        self.calc_probabilities = tk.BooleanVar(value=True)
        self.range_from = tk.StringVar(value="1")
        self.range_to = tk.StringVar(value="2")

        ttk.Checkbutton(self, text="Oblicz prawdopodobieństwa",
                        variable=self.calc_probabilities).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        ttk.Label(self, text="od").grid(row=1, column=0, sticky="e", padx=4)
        ttk.Spinbox(self, textvariable=self.range_from, from_=0, to=9999,
                    width=6).grid(row=1, column=1, pady=3)
        ttk.Label(self, text="Max do:").grid(row=1, column=2, sticky="w", padx=8)

        ttk.Label(self, text="do").grid(row=2, column=0, sticky="e", padx=4)
        ttk.Spinbox(self, textvariable=self.range_to, from_=0, to=9999,
                    width=6).grid(row=2, column=1, pady=3)
        ttk.Label(self, text="∞").grid(row=2, column=2, sticky="w", padx=8)

        ttk.Button(self, text=button_text, command=command).grid(
            row=3, column=0, columnspan=4, sticky="ew", pady=(14, 0))


class ResultsTable(ttk.LabelFrame):
    def __init__(self, parent, columns=1):
        super().__init__(parent, text="")
        self.columnconfigure(0, weight=1)
        self.vars = {}

        for r, item in enumerate(RESULT_ROWS):
            if item is None:
                ttk.Label(self, text="").grid(row=r, column=0)
                continue
            label, key = item
            ttk.Label(self, text=label).grid(row=r, column=0, sticky="w", padx=6, pady=2)
            ttk.Label(self, text=key).grid(row=r, column=1, sticky="e", padx=6)
            row_vars = []
            for c in range(columns):
                var = tk.StringVar(value="0")
                ttk.Entry(self, textvariable=var, state="readonly",
                          width=24 if columns == 1 else 18,
                          justify="right").grid(row=r, column=2 + c, padx=4, pady=2)
                row_vars.append(var)
            self.vars[key] = row_vars

    def set(self, key, *values):
        for var, value in zip(self.vars[key], values):
            var.set(str(value))


def vertical_separator(parent):
    ttk.Separator(parent, orient="vertical").pack(side="left", fill="y", padx=15)
