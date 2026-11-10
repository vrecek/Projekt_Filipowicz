from tkinter import ttk
from ..widgets import ParamForm, RangePanel, ResultsTable, vertical_separator


class CompareTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        self.params = ParamForm(
            top,
            [
                ("Intensywność strumienia zgłoszeń lam", "1.000", 0.1),
                ("Średnia intensywność obsługi mi", "1.000", 0.1),
                ("Liczba kanałów obsługi", 2, 1),
                ("Maksymalna liczba zgłoszeń", 4, 1),
            ],
            columns=2,
            headers=["System 1:", "System 2:"],
        )
        self.params.pack(side="left", fill="x", expand=True)

        vertical_separator(top)

        self.range_panel = RangePanel(top, "Porównaj", self.compare)
        self.range_panel.pack(side="left")

        self.results = ResultsTable(self, columns=2)
        self.results.pack(fill="both", expand=True, padx=10, pady=(5, 10))


    def compare(self):
        lam1 = float(self.params.vars[0][0].get())  # lam, System 1
        lam2 = float(self.params.vars[0][1].get())  # lam, System 2
        mu1 = float(self.params.vars[1][0].get())  # mi,  System 1
        mu2 = float(self.params.vars[1][1].get())  # mi,  System 2
        m1 = int(self.params.vars[2][0].get())  # Liczba kanałów obsługi, System 1
        m2 = int(self.params.vars[2][1].get())  # Liczba kanałów obsługi, System 2
        N1 = int(self.params.vars[3][0].get())  # Maksymalna liczba zgłoszeń, System 1
        N2 = int(self.params.vars[3][1].get())  # Maksymalna liczba zgłoszeń, System 2

        calc_probs = self.range_panel.calc_probabilities.get()  # "Oblicz prawdopodobieństwa" checkbox (bool)
        k_from = int(self.range_panel.range_from.get())  # "od"
        k_to = int(self.range_panel.range_to.get())  # "do"


        ro1 = 1
        ro2 = 2
        p01 = 3
        p02 = 4
        p11 = 5
        p12 = 6
        p21 = 7
        p22 = 8
        A1 = 9
        A2 = 10
        n_sr1 = 11
        n_sr2 = 12
        v_sr1 = 13
        v_sr2 = 14
        tf_sr1 = 15
        tf_sr2 = 16
        ts_sr1 = 17
        ts_sr2 = 18
        m0_sr1 = 19
        m0_sr2 = 20

        self.results.set("ro", ro1, ro2)
        self.results.set("p0", p01, p02)
        self.results.set("p1", p11, p12)
        self.results.set("p2", p21, p22)
        self.results.set("A", A1, A2)
        self.results.set("n_śr", n_sr1, n_sr2)
        self.results.set("v_śr", v_sr1, v_sr2)
        self.results.set("tf_śr", tf_sr1, tf_sr2)
        self.results.set("ts_śr", ts_sr1, ts_sr2)
        self.results.set("m0_śr", m0_sr1, m0_sr2)
