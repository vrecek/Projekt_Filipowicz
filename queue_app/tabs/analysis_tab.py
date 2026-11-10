from tkinter import ttk
from ..widgets import ParamForm, RangePanel, ResultsTable, vertical_separator


class AnalysisTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        self.params = ParamForm(top, [
            ("Intensywność strumienia zgłoszeń lam", "1.000", 0.1),
            ("Średnia intensywność obsługi mi", "1.000", 0.1),
            ("Liczba kanałów obsługi", 4, 1),
            ("Maksymalna liczba zgłoszeń", 6, 1),
        ])
        self.params.pack(side="left", fill="x", expand=True)

        vertical_separator(top)

        self.range_panel = RangePanel(top, "Analizuj", self.analyse)
        self.range_panel.pack(side="left")

        self.results = ResultsTable(self, columns=1)
        self.results.pack(fill="both", expand=True, padx=10, pady=(5, 10))


    def analyse(self):
        lam = float(self.params.vars[0][0].get())  # Intensywność strumienia zgłoszeń lam
        mu  = float(self.params.vars[1][0].get())  # Średnia intensywność obsługi mi
        m   = int(self.params.vars[2][0].get())  # Liczba kanałów obsługi
        N   = int(self.params.vars[3][0].get())  # Maksymalna liczba zgłoszeń

        calc_probs = self.range_panel.calc_probabilities.get()  # Oblicz prawdopodobieństwa checkbox (bool)
        k_from     = int(self.range_panel.range_from.get())  # od
        k_to       = int(self.range_panel.range_to.get())  # do



        print(lam, mu, m, N, calc_probs, k_from, k_to)

        ro = 1
        p0 = 2
        p1 = 3
        p2 = 4
        A = 5
        n_sr = 6
        v_sr = 7
        tf_sr = 8
        ts_sr = 9
        m0_sr = 10

        self.results.set("ro", ro)
        self.results.set("p0", p0)
        self.results.set("p1", p1)
        self.results.set("p2", p2)
        self.results.set("A", A)
        self.results.set("n_śr", n_sr)
        self.results.set("v_śr", v_sr)
        self.results.set("tf_śr", tf_sr)
        self.results.set("ts_śr", ts_sr)
        self.results.set("m0_śr", m0_sr)
