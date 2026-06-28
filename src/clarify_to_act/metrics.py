from __future__ import annotations

import random
from collections import defaultdict
from statistics import mean


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def bootstrap_mean_ci(values: list[float], seed: int = 0, samples: int = 1000) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    means = []
    n = len(values)
    for _ in range(samples):
        means.append(mean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    lo = means[int(0.025 * samples)]
    hi = means[int(0.975 * samples)]
    return (lo, hi)


def aggregate(rows: list[dict]) -> dict:
    rewards = [float(row["reward"]) for row in rows]
    oracle_ask = [row for row in rows if row["oracle_should_ask"]]
    oracle_act = [row for row in rows if not row["oracle_should_ask"]]
    missed = [row for row in oracle_ask if not row["asked"]]
    unnecessary = [row for row in oracle_act if row["asked"]]
    ci_lo, ci_hi = bootstrap_mean_ci(rewards)
    return {
        "n": len(rows),
        "net_utility": mean(rewards) if rewards else 0.0,
        "net_utility_ci_low": ci_lo,
        "net_utility_ci_high": ci_hi,
        "success": safe_div(sum(1 for row in rows if row["success"]), len(rows)),
        "ask_rate": safe_div(sum(1 for row in rows if row["asked"]), len(rows)),
        "missed_clarification_rate": safe_div(len(missed), len(oracle_ask)),
        "unnecessary_clarification_rate": safe_div(len(unnecessary), len(oracle_act)),
        "oracle_ask_rate": safe_div(len(oracle_ask), len(rows)),
    }


def group_rows(rows: list[dict], keys: tuple[str, ...]) -> dict[tuple, list[dict]]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    return groups


def format_float(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |"]
    out.append("| " + " | ".join(["---" for _ in headers]) + " |")
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out) + "\n"
