from __future__ import annotations

import argparse
import random
from collections import defaultdict
from statistics import mean

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--splits", default="test")
    parser.add_argument("--comparisons", required=True, help="Comma-separated pairs like method_a:method_b.")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def bootstrap_ci(values: list[float], samples: int, seed: int) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(samples):
        means.append(mean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    return (means[int(0.025 * samples)], means[int(0.975 * samples)])


def parse_comparisons(text: str) -> list[tuple[str, str]]:
    pairs = []
    for raw_pair in text.split(","):
        raw_pair = raw_pair.strip()
        if not raw_pair:
            continue
        left, sep, right = raw_pair.partition(":")
        if not sep or not left.strip() or not right.strip():
            raise ValueError(f"Invalid comparison {raw_pair!r}; expected method_a:method_b.")
        pairs.append((left.strip(), right.strip()))
    return pairs


def read_result_paths(paths: str) -> list[dict]:
    rows: list[dict] = []
    for path in [part.strip() for part in paths.split(",") if part.strip()]:
        rows.extend(read_jsonl(path))
    return rows


def paired_rows(rows: list[dict], splits: list[str], comparisons: list[tuple[str, str]], samples: int, seed: int) -> str:
    by_split_policy_episode: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for row in rows:
        split = row["split"]
        if split not in splits:
            continue
        by_split_policy_episode[(split, row["policy"])][row["episode_id"]] = float(row["reward"])

    table_rows = []
    for split in splits:
        for method_a, method_b in comparisons:
            rewards_a = by_split_policy_episode[(split, method_a)]
            rewards_b = by_split_policy_episode[(split, method_b)]
            shared_ids = sorted(set(rewards_a) & set(rewards_b))
            diffs = [rewards_a[episode_id] - rewards_b[episode_id] for episode_id in shared_ids]
            lo, hi = bootstrap_ci(diffs, samples=samples, seed=seed)
            table_rows.append(
                [
                    split,
                    method_a,
                    method_b,
                    str(len(shared_ids)),
                    format_float(mean(diffs) if diffs else 0.0),
                    f"[{format_float(lo)}, {format_float(hi)}]",
                ]
            )
    return markdown_table(["Split", "Method A", "Method B", "Shared N", "A - B utility", "95% paired CI"], table_rows)


def main() -> None:
    args = parse_args()
    rows = read_result_paths(args.results)
    splits = [split.strip() for split in args.splits.split(",") if split.strip()]
    comparisons = parse_comparisons(args.comparisons)
    title = "# Paired Net-Utility Differences\n\n"
    body = paired_rows(rows, splits, comparisons, samples=args.bootstrap_samples, seed=args.seed)
    write_text(args.out, title + body)
    print(f"wrote paired differences to {args.out}")


if __name__ == "__main__":
    main()
