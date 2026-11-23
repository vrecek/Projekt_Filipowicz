import math


def compute(lam, mu, m, N):
    if lam <= 0 or mu <= 0:
        raise ValueError("Intensywności muszą być dodatnie.")
    if m < 1 or N < 1:
        raise ValueError("Liczba kanałów i zgłoszeń musi być ≥ 1.")
    m = min(m, N)

    log_w = [0.0]
    for k in range(1, N + 1):
        log_w.append(log_w[-1] + math.log((N - k + 1) * lam / (min(k, m) * mu)))
    top = max(log_w)
    w = [math.exp(x - top) for x in log_w]
    total = sum(w)
    p = [x / total for x in w]

    n_avg = sum(k * pk for k, pk in enumerate(p))
    v_avg = sum((k - m) * pk for k, pk in enumerate(p) if k > m)
    A = lam * (N - n_avg)

    return {
        "ro": lam / mu,
        "p": p,
        "A": A,
        "n": n_avg,
        "v": v_avg,
        "tf": v_avg / A if A else float("inf"),
        "ts": n_avg / A if A else float("inf"),
        "m0": A / mu,
        "util": A / (mu * m),
    }
