import tkinter as tk
from tkinter import ttk

from .constants import APP_TITLE, BANNER_BG, BANNER_FG, MODEL_NAME, WINDOW_BG, WINDOW_RESOLUTION
from .tabs import AnalysisTab, CompareTab, OptimizationTab


class QueueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_RESOLUTION)
        self.configure(bg=WINDOW_BG)

        tk.Label(self, text=MODEL_NAME, bg=BANNER_BG, fg=BANNER_FG,
                 font=("Segoe UI", 20), pady=14).pack(fill="x", padx=10, pady=(10, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.analysis_tab = AnalysisTab(notebook)
        self.compare_tab = CompareTab(notebook)
        self.optimization_tab = OptimizationTab(notebook)

        notebook.add(self.analysis_tab, text="Analiza")
        notebook.add(self.compare_tab, text="Porównanie")
        notebook.add(self.optimization_tab, text="Optymalizacja")
