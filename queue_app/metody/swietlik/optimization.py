# Z(m, N) = C1 * m + C2 * v_śr - R * A

import random
from dataclasses import dataclass, field

from .firefly import GAMMA_FIXED, GAMMA_RMAX, GAMMA_RMAX2, firefly_algorithm
from ...model import compute

EXACT_SEARCH_LIMIT = 50_000

GAMMA_MODES = {
    "stałe γ": GAMMA_FIXED,
    "adaptacyjne γ0 / r_max": GAMMA_RMAX,
    "adaptacyjne γ0 / r_max²": GAMMA_RMAX2,
}


# ------------------------------------------------------------- settings --
def _number(value, name, kind=float):
    try:
        return kind(float(str(value).replace(",", ".")))
    except ValueError:
        raise ValueError(f"Nieprawidłowa wartość: {name}.") from None


@dataclass
class FireflySettings:
    iterations: int
    min_m: int
    max_m: int
    min_n: int
    max_n: int
    seed: int
    fireflies: int
    beta0: float
    gamma_mode: str
    gamma: float
    u_min: float
    u_max: float

    @classmethod
    def from_dict(cls, d):
        s = cls(
            iterations=_number(d["iterations"], "ilość iteracji", int),
            min_m=_number(d["min_m"], "minimalna wartość m", int),
            max_m=_number(d["max_m"], "maksymalna wartość m", int),
            min_n=_number(d["min_n"], "minimalna wartość N", int),
            max_n=_number(d["max_n"], "maksymalna wartość N", int),
            seed=_number(d["seed"], "ziarno generatora", int),
            fireflies=_number(d["fireflies"], "rozmiar roju", int),
            beta0=_number(d["beta0"], "maksimum atrakcyjności β0"),
            gamma_mode=str(d["gamma_mode"]),
            gamma=_number(d["gamma"], "współczynnik absorpcji γ"),
            u_min=_number(d["u_min"], "min u"),
            u_max=_number(d["u_max"], "max u"),
        )
        s.validate()
        return s

    def validate(self):
        if self.iterations < 1 or self.fireflies < 2:
            raise ValueError("Ilość iteracji musi być ≥ 1, a ilość świetlików ≥ 2.")
        if self.min_m < 1 or self.min_n < 1:
            raise ValueError("Minimalne wartości m i N muszą być ≥ 1.")
        if self.min_m > self.max_m or self.min_n > self.max_n:
            raise ValueError("Wartość minimalna nie może przekraczać maksymalnej.")
        if not 0 <= self.beta0 <= 1:
            raise ValueError("Maksimum atrakcyjności β0 musi należeć do przedziału [0, 1].")
        if self.gamma < 0:
            raise ValueError("Współczynnik absorpcji γ nie może być ujemny.")
        if self.gamma_mode not in GAMMA_MODES:
            raise ValueError("Nieprawidłowy tryb współczynnika absorpcji.")
        if self.u_min > self.u_max:
            raise ValueError("Dolna granica kroku losowego (min u) przekracza górną (max u).")

    def summary_parts(self):
        gamma = {GAMMA_FIXED: f"γ = {self.gamma:g}",
                 GAMMA_RMAX: f"γ = {self.gamma:g} / r_max",
                 GAMMA_RMAX2: f"γ = {self.gamma:g} / r_max²"}[GAMMA_MODES[self.gamma_mode]]
        return [f"rój m = {self.fireflies}", f"iteracje = {self.iterations}",
                f"β0 = {self.beta0:g}", gamma,
                f"krok losowy u ∈ [{self.u_min:g}, {self.u_max:g}]",
                f"ziarno = {self.seed if self.seed else 'losowe'}"]


# --------------------------------------------------------------- result --
@dataclass
class OptimizationResult:
    lam: float
    mu: float
    c1: float
    c2: float
    revenue: float
    optimise_n: bool
    settings: FireflySettings
    m_range: tuple
    n_range: tuple
    m: int = 0
    N: int = 0
    cost: float = 0.0
    metrics: dict = field(default_factory=dict)
    improvements: list = field(default_factory=list)
    history: list = field(default_factory=list)
    designs_evaluated: int = 0
    search_space: int = 0
    exact: tuple = None


# ----------------------------------------------------------------- run --
def optimise_system(lam, mu, n_fixed, c1, c2, revenue, optimise_n, settings):
    if lam <= 0 or mu <= 0:
        raise ValueError("Intensywności muszą być dodatnie.")
    if c1 < 0 or c2 < 0 or revenue < 0:
        raise ValueError("Koszty i zysk nie mogą być ujemne.")

    s = settings
    if optimise_n:
        n_lo, n_hi = s.min_n, s.max_n
        m_lo, m_hi = s.min_m, s.max_m
    else:
        if n_fixed < 1:
            raise ValueError("Maksymalna liczba zgłoszeń musi być ≥ 1.")
        n_lo = n_hi = n_fixed
        m_lo, m_hi = s.min_m, min(s.max_m, n_fixed)
        if m_lo > m_hi:
            raise ValueError("Minimalna wartość m przekracza dopuszczalny zakres "
                             "(max m lub liczbę zgłoszeń N).")

    cache = {}

    def evaluate(m, N):
        m = min(m, N)
        key = (m, N)
        if key not in cache:
            r = compute(lam, mu, m, N)
            cache[key] = (c1 * m + c2 * r["v"] - revenue * r["A"], r)
        return cache[key][0]

    def decode(x):
        m = int(round(x[0]))
        N = int(round(x[1])) if optimise_n else n_fixed
        return min(m, N), N

    lower, upper = [m_lo], [m_hi]
    if optimise_n:
        lower.append(n_lo)
        upper.append(n_hi)

    rng = random.Random(s.seed) if s.seed else random.Random()
    ff = firefly_algorithm(
        lambda x: evaluate(*decode(x)), lower, upper,
        n_fireflies=s.fireflies, iterations=s.iterations, beta0=s.beta0,
        gamma=s.gamma, gamma_mode=GAMMA_MODES[s.gamma_mode],
        u_min=s.u_min, u_max=s.u_max, rng=rng)

    best_m, best_n = decode(ff.best_position)
    res = OptimizationResult(
        lam=lam, mu=mu, c1=c1, c2=c2, revenue=revenue, optimise_n=optimise_n,
        settings=s, m_range=(m_lo, m_hi), n_range=(n_lo, n_hi),
        m=best_m, N=best_n, cost=cache[(best_m, best_n)][0],
        metrics=cache[(best_m, best_n)][1], designs_evaluated=len(cache))

    res.history = [value for value, _ in ff.history]

    previous = float("inf")
    for it, (value, pos) in enumerate(ff.history):
        if value < previous - 1e-12:
            m, N = decode(pos)
            res.improvements.append((it, value, m, N))
            previous = value

    designs = {(m, N) for N in range(n_lo, n_hi + 1)
               for m in range(min(m_lo, N), min(m_hi, N) + 1)}
    res.search_space = len(designs)
    if len(designs) <= EXACT_SEARCH_LIMIT:
        best = min(designs, key=lambda d: (evaluate(*d), d))
        res.exact = (best[0], best[1], cache[best][0])
    return res


# --------------------------------------------------------------- report --
def format_report(r):
    s = r.settings
    line = "-" * 62
    out = ["OPTYMALIZACJA METODĄ ŚWIETLIKA  (M/M/m/FIFO/N/F)", line]

    n_text = (f"N ∈ [{r.n_range[0]}, {r.n_range[1]}]" if r.optimise_n
              else f"N = {r.n_range[0]} (stałe)")
    out += [
        f"Dane:    lam = {r.lam:g},  mi = {r.mu:g},  {n_text}",
        f"Koszty:  C1 = {r.c1:g} (kanał),  C2 = {r.c2:g} (kolejka),  "
        f"zysk R = {r.revenue:g} (obsłużone zgłoszenie)",
        "Cel:     min Z = C1·m + C2·v_śr − R·A      (zysk netto = −Z)",
        f"Szukane: m ∈ [{r.m_range[0]}, {r.m_range[1]}]"
        + (f",  N ∈ [{r.n_range[0]}, {r.n_range[1]}]" if r.optimise_n else ""),
        "Metoda:  " + ",  ".join(s.summary_parts()),
        "",
        "Przebieg (iteracje, w których poprawiono najlepsze rozwiązanie):",
        f"  {'iter':>5} {'m':>5} {'N':>5} {'Z':>14}",
    ]
    for it, value, m, N in r.improvements:
        out.append(f"  {('start' if it == 0 else it)!s:>5} {m:>5} {N:>5} {value:>14.6f}")

    m = r.metrics
    out += [
        "",
        line,
        "WYNIK",
        f"  Optymalna liczba kanałów     m* = {r.m}",
        f"  Liczba zgłoszeń              N* = {r.N}",
        f"  Funkcja celu                  Z = {r.cost:.6f}",
        f"  Zysk netto                       {-r.cost:.6f}",
        "",
        f"  p0      = {m['p'][0]:.10f}",
        f"  A       = {m['A']:.10f}",
        f"  n_śr    = {m['n']:.10f}",
        f"  v_śr    = {m['v']:.10f}",
        f"  tf_śr   = {m['tf']:.10f}",
        f"  ts_śr   = {m['ts']:.10f}",
        f"  m0_śr   = {m['m0']:.10f}",
        f"  wykorzystanie kanałów = {m['util']:.2%}",
        "",
        f"Ocenionych rozwiązań: {r.designs_evaluated} z {r.search_space} możliwych",
    ]
    if r.exact:
        em, en, ez = r.exact
        verdict = "zgodne" if abs(ez - r.cost) < 1e-9 else "RÓŻNE (algorytm nie znalazł optimum)"
        out.append(f"Przegląd zupełny: m = {em}, N = {en}, Z = {ez:.6f}  → {verdict}")
    else:
        out.append(f"Przegląd zupełny pominięty (przestrzeń > {EXACT_SEARCH_LIMIT} rozwiązań).")
    return "\n".join(out)
