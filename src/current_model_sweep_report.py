from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from statistics import mean

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table


POLICIES = ["api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Model label and comma-separated result paths, formatted as model=path[,path2].",
    )
    parser.add_argument("--out", default="paper/tables/current_model_sweep.md")
    parser.add_argument("--title", default="Current-Model Sweep")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def parse_run_spec(spec: str) -> tuple[str, list[str]]:
    label, sep, paths = spec.partition("=")
    if not sep or not label.strip() or not paths.strip():
        raise ValueError(f"Invalid --run {spec!r}; expected model=path[,path2].")
    return label.strip(), [path.strip() for path in paths.split(",") if path.strip()]


def bootstrap_ci(values: list[float], samples: int, seed: int) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    n = len(values)
    estimates = []
    for _ in range(samples):
        estimates.append(mean(values[rng.randrange(n)] for _ in range(n)))
    estimates.sort()
    return (estimates[int(0.025 * samples)], estimates[int(0.975 * samples)])


def paired_delta(rows: list[dict], method_a: str, method_b: str, samples: int, seed: int) -> tuple[int, float, tuple[float, float]]:
    rewards: dict[str, dict[str, float]] = {}
    for row in rows:
        rewards.setdefault(row["policy"], {})[row["episode_id"]] = float(row["reward"])
    shared_ids = sorted(set(rewards.get(method_a, {})) & set(rewards.get(method_b, {})))
    diffs = [rewards[method_a][episode_id] - rewards[method_b][episode_id] for episode_id in shared_ids]
    delta = mean(diffs) if diffs else 0.0
    return len(shared_ids), delta, bootstrap_ci(diffs, samples=samples, seed=seed)


def response_usage(rows: list[dict]) -> dict[str, int]:
    seen: set[str] = set()
    totals = {"responses": 0, "input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0}
    for row in rows:
        debug = row.get("debug") or {}
        for key in ("api", "api_second", "api_question"):
            meta = debug.get(key)
            if not isinstance(meta, dict):
                continue
            response_id = meta.get("response_id") or meta.get("cache_key")
            if not response_id or response_id in seen:
                continue
            seen.add(str(response_id))
            usage = meta.get("usage") or {}
            output_details = usage.get("output_tokens_details") or {}
            totals["responses"] += 1
            totals["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            totals["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
            totals["reasoning_tokens"] += int(output_details.get("reasoning_tokens", 0) or 0)
    return totals


def load_rows(paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        rows.extend(read_jsonl(path))
    return rows


def model_table(runs: list[tuple[str, list[dict]]], samples: int, seed: int) -> str:
    table_rows = []
    for label, rows in runs:
        by_policy = {policy: [row for row in rows if row["policy"] == policy] for policy in POLICIES}
        stats = {policy: aggregate(policy_rows) for policy, policy_rows in by_policy.items() if policy_rows}
        shared_n, delta, ci = paired_delta(rows, "api_ecu", "api_ask_needed", samples=samples, seed=seed)
        ecu_stats = stats.get("api_ecu")
        table_rows.append(
            [
                label,
                str(shared_n),
                format_float(stats["api_direct_act"]["net_utility"]) if "api_direct_act" in stats else "-",
                format_float(stats["api_ask_needed"]["net_utility"]) if "api_ask_needed" in stats else "-",
                format_float(stats["api_ask_needed_cot"]["net_utility"]) if "api_ask_needed_cot" in stats else "-",
                format_float(stats["api_ecu"]["net_utility"]) if "api_ecu" in stats else "-",
                format_float(delta),
                f"[{format_float(ci[0])}, {format_float(ci[1])}]",
                format_float(ecu_stats["missed_clarification_rate"]) if ecu_stats else "-",
                format_float(ecu_stats["unnecessary_clarification_rate"]) if ecu_stats else "-",
            ]
        )
    return markdown_table(
        [
            "Model",
            "Paired N",
            "Direct utility",
            "Ask-Needed utility",
            "CoT Ask-Needed utility",
            "ECU utility",
            "ECU - AskNeeded",
            "95% paired CI",
            "ECU missed",
            "ECU unnecessary",
        ],
        table_rows,
    )


def usage_table(runs: list[tuple[str, list[dict]]]) -> str:
    table_rows = []
    for label, rows in runs:
        usage = response_usage(rows)
        table_rows.append(
            [
                label,
                str(usage["responses"]),
                str(usage["input_tokens"]),
                str(usage["output_tokens"]),
                str(usage["reasoning_tokens"]),
            ]
        )
    return markdown_table(["Model", "Responses", "Input tokens", "Output tokens", "Reasoning tokens"], table_rows)


def main() -> None:
    args = parse_args()
    runs = [(label, load_rows(paths)) for label, paths in (parse_run_spec(spec) for spec in args.run)]
    body = [
        f"# {args.title}\n\n",
        "## Main Comparison\n\n",
        model_table(runs, samples=args.bootstrap_samples, seed=args.seed),
        "\n\n## API Usage\n\n",
        usage_table(runs),
        "\n",
    ]
    write_text(args.out, "".join(body))
    print(f"wrote current-model sweep report to {args.out}")


if __name__ == "__main__":
    main()
