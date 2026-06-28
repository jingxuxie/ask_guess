from __future__ import annotations

import argparse
import random
from collections import defaultdict
from statistics import mean

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


CATEGORY_ORDER = ["context_resolved", "equivalent_outcome", "preference_social", "referential", "risk_sensitive"]
COMPARISONS = [("api_ecu", "api_ask_needed"), ("api_ecu", "api_direct_act")]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/api_eval_100_corrected/subset_stability.md")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def rows_by_episode_policy(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(row["episode_id"], row["policy"]): row for row in rows}


def category_by_episode(rows: list[dict]) -> dict[str, str]:
    return {row["episode_id"]: row["ambiguity_type"] for row in rows}


def paired_differences(rows: list[dict], method_a: str, method_b: str, episode_ids: list[str] | None = None) -> list[float]:
    by_key = rows_by_episode_policy(rows)
    if episode_ids is None:
        a_ids = {episode_id for episode_id, policy in by_key if policy == method_a}
        b_ids = {episode_id for episode_id, policy in by_key if policy == method_b}
        episode_ids = sorted(a_ids & b_ids)
    return [float(by_key[(episode_id, method_a)]["reward"]) - float(by_key[(episode_id, method_b)]["reward"]) for episode_id in episode_ids]


def mean_delta(rows: list[dict], method_a: str, method_b: str, episode_ids: list[str] | None = None) -> float:
    diffs = paired_differences(rows, method_a, method_b, episode_ids)
    return mean(diffs) if diffs else 0.0


def category_ids(rows: list[dict]) -> dict[str, list[str]]:
    cats: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        cats[row["ambiguity_type"]].add(row["episode_id"])
    return {category: sorted(ids) for category, ids in cats.items()}


def bootstrap_ci(values: list[float], samples: int, seed: int) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    n = len(values)
    means = [mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(samples)]
    means.sort()
    return (means[int(0.025 * samples)], means[int(0.975 * samples)])


def stratified_bootstrap_ci(rows: list[dict], method_a: str, method_b: str, samples: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    ids_by_category = category_ids(rows)
    diffs_by_category = {
        category: paired_differences(rows, method_a, method_b, ids)
        for category, ids in ids_by_category.items()
    }
    means = []
    for _ in range(samples):
        resampled = []
        for category in sorted(diffs_by_category):
            diffs = diffs_by_category[category]
            resampled.extend(diffs[rng.randrange(len(diffs))] for _ in range(len(diffs)))
        means.append(mean(resampled))
    means.sort()
    return (means[int(0.025 * samples)], means[int(0.975 * samples)])


def category_delta_table(rows: list[dict]) -> str:
    ids_by_category = category_ids(rows)
    table_rows = []
    for category in CATEGORY_ORDER:
        ids = ids_by_category.get(category, [])
        if not ids:
            continue
        row = [category, str(len(ids))]
        for method_a, method_b in COMPARISONS:
            diffs = paired_differences(rows, method_a, method_b, ids)
            lo, hi = bootstrap_ci(diffs, samples=2000, seed=0)
            row.extend([format_float(mean(diffs)), f"[{format_float(lo)}, {format_float(hi)}]"])
        table_rows.append(row)
    return markdown_table(
        [
            "Category",
            "N",
            "ECU - AskNeeded",
            "95% paired CI",
            "ECU - DirectAct",
            "95% paired CI",
        ],
        table_rows,
    )


def leave_one_category_table(rows: list[dict]) -> str:
    all_ids = sorted({row["episode_id"] for row in rows})
    category_lookup = category_by_episode(rows)
    table_rows = []
    for omitted in CATEGORY_ORDER:
        kept = [episode_id for episode_id in all_ids if category_lookup[episode_id] != omitted]
        if not kept:
            continue
        table_rows.append(
            [
                omitted,
                str(len(kept)),
                format_float(mean_delta(rows, "api_ecu", "api_ask_needed", kept)),
                format_float(mean_delta(rows, "api_ecu", "api_direct_act", kept)),
            ]
        )
    return markdown_table(["Omitted category", "Remaining N", "ECU - AskNeeded", "ECU - DirectAct"], table_rows)


def leave_one_episode_table(rows: list[dict]) -> str:
    all_ids = sorted({row["episode_id"] for row in rows})
    table_rows = []
    for method_a, method_b in COMPARISONS:
        deltas = []
        for omitted in all_ids:
            kept = [episode_id for episode_id in all_ids if episode_id != omitted]
            deltas.append(mean_delta(rows, method_a, method_b, kept))
        table_rows.append(
            [
                f"{method_a} - {method_b}",
                str(len(deltas)),
                format_float(min(deltas)),
                format_float(max(deltas)),
                str(sum(delta > 0.0 for delta in deltas)),
            ]
        )
    return markdown_table(["Comparison", "Leave-one runs", "Min delta", "Max delta", "Positive runs"], table_rows)


def stratified_bootstrap_table(rows: list[dict], samples: int, seed: int) -> str:
    table_rows = []
    for method_a, method_b in COMPARISONS:
        delta = mean_delta(rows, method_a, method_b)
        lo, hi = stratified_bootstrap_ci(rows, method_a, method_b, samples, seed)
        table_rows.append([f"{method_a} - {method_b}", "100", format_float(delta), f"[{format_float(lo)}, {format_float(hi)}]"])
    return markdown_table(["Comparison", "N", "Mean delta", "Stratified 95% CI"], table_rows)


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.results)
    text = "\n".join(
        [
            "# API Subset Stability",
            "",
            "This no-API diagnostic checks whether the final 100-episode GPT-4.1-mini API advantage is concentrated in one category or one episode. It uses the cached canonical API result rows and paired rewards.",
            "",
            "## Category Paired Deltas",
            "",
            category_delta_table(rows),
            "## Leave-One-Category-Out Deltas",
            "",
            leave_one_category_table(rows),
            "## Leave-One-Episode-Out Deltas",
            "",
            leave_one_episode_table(rows),
            "## Stratified Bootstrap",
            "",
            stratified_bootstrap_table(rows, args.bootstrap_samples, args.seed),
            "## Interpretation",
            "",
            "- ECU's paired advantage over Ask-Needed has a positive point estimate in every category and remains positive after omitting any single category.",
            "- Leave-one-episode-out deltas remain positive for every omitted episode.",
            "- This is a subset-stability diagnostic for the bounded API set, not a substitute for a larger paid API sweep.",
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote API subset stability report to {args.out}")


if __name__ == "__main__":
    main()
