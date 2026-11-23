# # https://home.agh.edu.pl/~slukasik/pub/021_Lukasik_KAEiOG2011(presentation).pdf

import math
import random
from dataclasses import dataclass, field

GAMMA_FIXED = "fixed"
GAMMA_RMAX = "rmax"      # gamma = gamma0 / r_max
GAMMA_RMAX2 = "rmax2"    # gamma = gamma0 / r_max^2


@dataclass
class FireflyResult:
    best_position: list
    best_value: float
    history: list = field(default_factory=list)
    evaluations: int = 0
    gamma: float = 0.0


def firefly_algorithm(objective, lower, upper, n_fireflies=30, iterations=40,
                      beta0=1.0, gamma=0.8, gamma_mode=GAMMA_RMAX2,
                      u_min=-0.05, u_max=0.05, rng=None):

    rng = rng or random.Random()
    dim = len(lower)
    span = [hi - lo for lo, hi in zip(lower, upper)]
    r_max = math.sqrt(sum(s * s for s in span))

    if gamma_mode == GAMMA_FIXED:
        g = gamma
    elif r_max == 0:
        g = 0.0
    elif gamma_mode == GAMMA_RMAX:
        g = gamma / r_max
    elif gamma_mode == GAMMA_RMAX2:
        g = gamma / r_max ** 2
    else:
        raise ValueError(f"Unknown gamma_mode: {gamma_mode!r}")

    calls = 0

    def evaluate(x):
        nonlocal calls
        calls += 1
        return objective(x)

    def clip(x):
        return [min(max(v, lo), hi) for v, lo, hi in zip(x, lower, upper)]

    def random_step():
        return [rng.uniform(u_min, u_max) * span[k] for k in range(dim)]

    pop = [[rng.uniform(lo, hi) for lo, hi in zip(lower, upper)]
           for _ in range(n_fireflies)]
    cost = [evaluate(x) for x in pop]

    best_i = min(range(n_fireflies), key=cost.__getitem__)
    best_x, best_c = pop[best_i][:], cost[best_i]
    history = [(best_c, best_x[:])]

    for _ in range(iterations):
        i_min = min(range(n_fireflies), key=cost.__getitem__)

        for i in range(n_fireflies):
            if i == i_min:
                continue
            for j in range(n_fireflies):
                if cost[j] < cost[i]:
                    r2 = sum((pop[i][k] - pop[j][k]) ** 2 for k in range(dim))
                    beta = beta0 * math.exp(-g * r2)
                    u = random_step()
                    pop[i] = clip([(1 - beta) * pop[i][k] + beta * pop[j][k] + u[k]
                                   for k in range(dim)])
                    cost[i] = evaluate(pop[i])
                    if cost[i] < best_c:
                        best_x, best_c = pop[i][:], cost[i]

        u = random_step()
        pop[i_min] = clip([pop[i_min][k] + u[k] for k in range(dim)])
        cost[i_min] = evaluate(pop[i_min])
        if cost[i_min] < best_c:
            best_x, best_c = pop[i_min][:], cost[i_min]

        history.append((best_c, best_x[:]))

    return FireflyResult(best_x, best_c, history, calls, g)
