"""Block-jitter coincidence test: exact p-values of arbitrary resolution under a local-exchangeability null.

The circular-shift test of `coordination.coincidence_scan` compares an account's alignment with the others to its T cyclic shifts, so its
p-values are multiples of 1/T and a Bonferroni threshold alpha/N is out of reach when N > alpha*T; its null also requires the account's timing
to be exchangeable over the whole window.

Here the window of T steps is cut into K blocks of `block` steps and the account's series is shifted cyclically inside each block by an
independent uniform offset (a jitter surrogate); the others are held fixed. The null is invariance of the account's flow under these within-block
shifts given the others. The statistic is the same as in the circular test, the coincidence of the account's flow with the widened flow of all others,
standardised and maximised over tolerances. Because the statistic is a sum over blocks, C(g) = sum_b r_b(s_b), where r_b(s) is the cross-correlation of
the account's block with the others' block at shift s, every surrogate costs K table look-ups, the mean and variance over the surrogates are known in
closed form (sum over blocks of the mean and variance of r_b), and the number of distinct surrogates is block**K, so the p-value (1 + #{surrogates at
least as extreme}) / (B + 1) can be made as fine as wished. With block = T it is the circular-shift test.
"""

from __future__ import annotations

import numpy as np


def _circ_box(x: np.ndarray, tol: int) -> np.ndarray:
    out = x.copy()
    for d in range(1, tol + 1):
        out += np.roll(x, d, axis=-1) + np.roll(x, -d, axis=-1)
    return out


def block_bounds(T: int, block: int):
    starts = list(range(0, T, block))
    return [(s, min(s + block, T)) for s in starts]


def jitter_scan(flow: np.ndarray, tols=(1, 5, 15), block: int = 100, n_surr: int = 999, signed: bool = True,
                rng: np.random.Generator | None = None, active: np.ndarray | None = None, tail: str = "pos",
                chunk: int = 512, reject_alpha: float | None = None, abandon: int | None = None):
    """flow: [side(2), agent, step] counts of one window. Returns (z, p, exceed, used) per agent.

    z is the observed standardised maximum statistic; p = (1 + exceed) / (n_surr + 1) is exact (for `used` = n_surr). With `reject_alpha` set,
    accounts whose number of surrogates at least as extreme as the observation exceeds the value that would keep p <= reject_alpha / (number of tested accounts)
    are dropped from the remaining draws (their p stays above the Bonferroni level, so the decision is unchanged and the cost falls); for them `used` < n_surr
    and p is not exact.
    """
    rng = rng or np.random.default_rng(0)
    ch = ((flow[0] - flow[1])[None] if signed else flow).astype(np.float64)
    C, n, T = ch.shape
    if active is None:
        active = ch.any(axis=(0, 2))
    idx = np.flatnonzero(active)
    m = len(idx)
    total = ch.sum(axis=1)                                          # [C, T]
    bounds = block_bounds(T, block)
    K = len(bounds)
    sgn = -1.0 if tail == "neg" else 1.0
    nt = len(tols)
    # tables[b]: [nt, m, len_b]
    tables = []
    mu = np.zeros((nt, m))
    var = np.zeros((nt, m))
    O = [np.stack([_circ_box(total[c][None] - ch[c], tol) for c in range(C)]) for tol in tols]   # list over tol of [C, n, T]
    for (a, b) in bounds:
        Lb = b - a
        tab = np.zeros((nt, m, Lb))
        for ti in range(nt):
            for c in range(C):
                x = ch[c][idx, a:b]
                o = O[ti][c][idx, a:b]
                # r(s) = sum_t o[t] x[(t + s) mod L]
                r = np.fft.irfft(np.conj(np.fft.rfft(o, axis=1)) * np.fft.rfft(x, axis=1), n=Lb, axis=1)
                tab[ti] += sgn * r
        tables.append(tab)
        mu += tab.mean(axis=2)
        var += tab.var(axis=2)
    sd = np.sqrt(var)
    sd = np.where(sd > 0, sd, 1.0)
    obs_stat = sum(tab[:, :, 0] for tab in tables)                  # [nt, m]
    zobs = ((obs_stat - mu) / sd).max(axis=0)                       # [m]
    exceed = np.zeros(m, dtype=np.int64)
    used = np.zeros(m, dtype=np.int64)
    alive = np.ones(m, dtype=bool)
    k_allowed = None
    if reject_alpha is not None:
        k_allowed = int(np.floor(reject_alpha * (n_surr + 1) / m)) - 1       # exceedances that still allow p <= alpha/m
    done = 0
    while done < n_surr and alive.any():
        bsz = min(chunk, n_surr - done)
        al = np.flatnonzero(alive)
        zmax = np.full((bsz, len(al)), -np.inf)
        stat = np.zeros((nt, bsz, len(al)))
        for k, (a, b) in enumerate(bounds):
            Lb = b - a
            sh = rng.integers(0, Lb, size=(bsz, len(al)))
            for ti in range(nt):
                stat[ti] += tables[k][ti][al[None, :], sh]
        z = ((stat - mu[:, al][:, None, :]) / sd[:, al][:, None, :]).max(axis=0)
        exceed[al] += (z >= zobs[al][None, :]).sum(axis=0)
        used[al] += bsz
        done += bsz
        if k_allowed is not None:
            alive[al] = exceed[al] <= k_allowed
    p_act = (1.0 + exceed) / (used + 1.0)
    zz = np.zeros(n); pp = np.ones(n); ee = np.zeros(n, dtype=np.int64); uu = np.zeros(n, dtype=np.int64)
    zz[idx], pp[idx], ee[idx], uu[idx] = zobs, p_act, exceed, used
    return zz, pp, ee, uu


def bonferroni_rejections(p: np.ndarray, used: np.ndarray, n_surr: int, active: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Accounts with exact p <= alpha / (number of tested accounts); accounts dropped early cannot be rejected."""
    m = int(active.sum())
    return active & (used == n_surr) & (p <= alpha / max(m, 1))
