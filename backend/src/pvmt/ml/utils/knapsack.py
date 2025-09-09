from __future__ import annotations
from typing import List, Dict


def select_under_budget(items: List[Dict], capacity: int | float) -> List[Dict]:
    """
    Exact 0/1 knapsack (dynamic programming) on 'time' vs 'profit'.

    Parameters
    ----------
    items : list of dict
        Each item must have:
          - 't'      : float  -> time in minutes (weight)
          - 'profit' : float  -> expected EUR (value)
        Other keys are carried through untouched.

        NOTE: Items with non-positive 'profit' should be filtered out upstream.

    capacity : int | float
        Total time budget in minutes.

    Returns
    -------
    chosen : list of dict
        The optimal subset (by total 'profit') not exceeding capacity.
        Items are returned in their original order of appearance.
    """
    # Quick exits
    if not items:
        return []
    cap = int(max(0, round(float(capacity))))
    if cap == 0:
        return []

    # Integer weights for DP
    weights = [max(0, int(round(float(it["t"])))) for it in items]
    values  = [float(it["profit"]) for it in items]
    n = len(items)

    # DP tables
    dp   = [[0.0] * (cap + 1) for _ in range(n + 1)]
    take = [[False] * (cap + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        row_prev = dp[i - 1]
        row_cur  = dp[i]
        take_row = take[i]
        for c in range(cap + 1):
            # skip
            best = row_prev[c]
            choose = False
            # take
            if w <= c:
                cand = row_prev[c - w] + v
                if cand > best:  # strictly better profit
                    best = cand
                    choose = True
            row_cur[c] = best
            take_row[c] = choose

    # Reconstruct chosen items (preserve original order)
    chosen: List[Dict] = []
    c = cap
    for i in range(n, 0, -1):
        if take[i][c]:
            chosen.append(items[i - 1])
            c -= weights[i - 1]
    chosen.reverse()
    return chosen
