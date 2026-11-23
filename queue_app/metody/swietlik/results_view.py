import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from ...constants import (ACCENT, BAD_BG, BAD_FG, BORDER, CARD_BG, GOOD_BG, GOOD_FG, MUTED,
                        NEUTRAL_BG, NEUTRAL_FG, PANEL_BG, ROW_ALT_BG, TEXT)
from .optimization import EXACT_SEARCH_LIMIT, format_report

PAD = 12
PREFERRED_FONTS = ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter", "Noto Sans",
                   "DejaVu Sans")


def _make_fonts(root):
    base = tkfont.nametofont("TkDefaultFont")
    available = set(tkfont.families(root))
    family = next((f for f in PREFERRED_FONTS if f in available), base.actual("family"))
    size = max(abs(int(base.cget("size"))), 10)

    def make(delta=0, weight="normal"):
        return tkfont.Font(root=root, family=family, size=size + delta, weight=weight)

    return {
        "body": make(), "bold": make(weight="bold"), "small": make(-1),
        "head": make(2, "bold"), "big": make(14, "bold"), "title": make(4, "bold"),
    }


class ConvergenceChart(tk.Canvas):
    def __init__(self, parent, fonts):
        super().__init__(parent, height=170, bg=CARD_BG, highlightthickness=1,
                         highlightbackground=BORDER)
        self.fonts = fonts
        self.values = []
        self.bind("<Configure>", lambda _e: self.redraw())

    def set_values(self, values):
        self.values = list(values)
        self.redraw()

    def redraw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        values = self.values
        if w < 120 or len(values) < 2:
            return
        left, right, top, bottom = 64, 18, 14, 28
        lo, hi = min(values), max(values)
        if hi - lo < 1e-12:  # flat line
            pad = abs(hi) * 0.05 or 1.0
            lo, hi = lo - pad, hi + pad
        n = len(values)

        def x(i):
            return left + (w - left - right) * i / (n - 1)

        def y(v):
            return top + (h - top - bottom) * (1 - (v - lo) / (hi - lo))

        digits = 4 if hi - lo < 1 else 2
        for k in range(4):
            val = lo + (hi - lo) * k / 3
            self.create_line(left, y(val), w - right, y(val), fill="#e5e9ed")
            self.create_text(left - 8, y(val), text=f"{val:.{digits}f}", anchor="e",
                             fill=MUTED, font=self.fonts["small"])
        self.create_text(left, h - 10, text="start", anchor="w", fill=MUTED,
                         font=self.fonts["small"])
        self.create_text(w - right, h - 10, text=f"iteracja {n - 1}", anchor="e",
                         fill=MUTED, font=self.fonts["small"])

        points = [x(0), y(values[0])]
        for i in range(1, n):
            points += [x(i), y(values[i - 1]), x(i), y(values[i])]
        self.create_line(*points, fill=ACCENT, width=2)
        r = 4
        self.create_oval(x(n - 1) - r, y(values[-1]) - r, x(n - 1) + r, y(values[-1]) + r,
                         fill=ACCENT, outline=CARD_BG, width=2)


class ResultsPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=PANEL_BG, highlightthickness=1,
                         highlightbackground=BORDER)
        self.fonts = _make_fonts(self)
        self._result = None

        body = tk.Frame(self, bg=PANEL_BG)
        body.pack(fill="both", expand=True, pady=(6, 0))
        self.canvas = tk.Canvas(body, bg=PANEL_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=PANEL_BG)
        window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(window, width=e.width))
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(sequence, self._on_wheel, add="+")

        self.clear()

    # ---------------------------------------------------------- public --
    def clear(self):
        self._result = None
        self._reset_body()

    def show(self, result):
        self._result = result
        self._reset_body()
        self._cards(result)
        self._characteristics(result.metrics)
        self._convergence(result)
        self.canvas.yview_moveto(0)

    # --------------------------------------------------------- helpers --
    def _reset_body(self):
        for child in self.inner.winfo_children():
            child.destroy()

    def _section(self, text):
        tk.Label(self.inner, text=text, bg=PANEL_BG, fg=TEXT, font=self.fonts["head"],
                 anchor="w").pack(fill="x", padx=PAD, pady=(16, 5))

    def _box(self):
        box = tk.Frame(self.inner, bg=CARD_BG, highlightthickness=1,
                       highlightbackground=BORDER)
        box.pack(fill="x", padx=PAD)
        return box

    def _on_wheel(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        while widget is not None and widget is not self:
            if isinstance(widget, ttk.Treeview):
                return
            widget = widget.master
        if widget is None:
            return
        if event.num == 4:
            step = -2
        elif event.num == 5:
            step = 2
        else:
            step = -2 if event.delta > 0 else 2
        self.canvas.yview_scroll(step, "units")

    # -------------------------------------------------------- sections --
    def _cards(self, r):
        row = tk.Frame(self.inner, bg=PANEL_BG)
        row.pack(fill="x", padx=PAD, pady=(8, 0))
        profit = -r.cost
        cards = [
            ("Optymalna liczba kanałów  m*", str(r.m), ACCENT),
            ("Liczba zgłoszeń  N*", str(r.N), ACCENT),
            ("Zysk netto  (−Z)", f"{profit:.2f}", GOOD_FG if profit >= 0 else BAD_FG),
        ]
        for col, (caption, value, colour) in enumerate(cards):
            row.columnconfigure(col, weight=1, uniform="cards")
            card = tk.Frame(row, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0))
            tk.Frame(card, bg=colour, height=4).pack(fill="x")
            tk.Label(card, text=caption, bg=CARD_BG, fg=MUTED, font=self.fonts["small"],
                     anchor="w").pack(fill="x", padx=PAD, pady=(10, 0))
            tk.Label(card, text=value, bg=CARD_BG, fg=colour, font=self.fonts["big"],
                     anchor="w").pack(fill="x", padx=PAD, pady=(0, 10))

    def _characteristics(self, m):
        self._section("Charakterystyki systemu dla rozwiązania optymalnego")
        box = self._box()
        rows = [
            ("p0", "Prawdopodobieństwo pustego systemu", f"{m['p'][0]:.6f}"),
            ("A", "Absolutna przepustowość systemu", f"{m['A']:.6f}"),
            ("n_śr", "Średnia liczba zgłoszeń w systemie", f"{m['n']:.6f}"),
            ("v_śr", "Średnia długość kolejki", f"{m['v']:.6f}"),
            ("tf_śr", "Średni czas oczekiwania w kolejce", f"{m['tf']:.6f}"),
            ("ts_śr", "Średni czas oczekiwania w systemie", f"{m['ts']:.6f}"),
            ("m0_śr", "Średnia liczba kanałów obsługujących", f"{m['m0']:.6f}"),
            ("wykorz.", "Wykorzystanie kanałów", f"{m['util']:.2%}"),
        ]
        for i, (symbol, description, value) in enumerate(rows):
            bg = CARD_BG if i % 2 == 0 else ROW_ALT_BG
            line = tk.Frame(box, bg=bg)
            line.pack(fill="x")
            line.columnconfigure(1, weight=1)
            tk.Label(line, text=symbol, bg=bg, fg=ACCENT, font=self.fonts["bold"],
                     width=8, anchor="w").grid(row=0, column=0, padx=(PAD, 0), pady=4)
            tk.Label(line, text=description, bg=bg, fg=TEXT, font=self.fonts["body"],
                     anchor="w").grid(row=0, column=1, sticky="w")
            tk.Label(line, text=value, bg=bg, fg=TEXT, font=self.fonts["bold"],
                     anchor="e").grid(row=0, column=2, padx=PAD, sticky="e")

    def _convergence(self, r):
        self._section("Przebieg algorytmu")
        chart = ConvergenceChart(self.inner, self.fonts)
        chart.pack(fill="x", padx=PAD)
        chart.set_values(r.history)

        tk.Label(self.inner, text="Iteracje, w których poprawiono najlepsze rozwiązanie",
                 bg=PANEL_BG, fg=MUTED, font=self.fonts["small"], anchor="w"
                 ).pack(fill="x", padx=PAD, pady=(10, 3))
        holder = tk.Frame(self.inner, bg=PANEL_BG)
        holder.pack(fill="x", padx=PAD)
        columns = ("iter", "m", "N", "Z")
        table = ttk.Treeview(holder, columns=columns, show="headings",
                             height=min(max(len(r.improvements), 1), 6))
        for column, title, width in (("iter", "Iteracja", 90), ("m", "m", 80),
                                     ("N", "N", 80), ("Z", "Z", 160)):
            table.heading(column, text=title)
            table.column(column, width=width, anchor="e" if column != "iter" else "center")
        for it, value, m, N in r.improvements:
            table.insert("", "end", values=("start" if it == 0 else it, m, N, f"{value:.6f}"))
        scrollbar = ttk.Scrollbar(holder, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        if len(r.improvements) > 6:
            scrollbar.pack(side="right", fill="y")
        table.pack(side="left", fill="x", expand=True)
