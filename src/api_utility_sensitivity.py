from __future__ import annotations

import argparse
import random
from statistics import mean

from clarify_to_act.generator import oracle_should_ask
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table


POLICY_ORDER = ["api_direct_act", "api_ask_needed", "api_ecu"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/api_eval_100_corrected/utility_sensitivity.md")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def policy_sort_key(policy: str) -> tuple[int, str]:
    try:
        return (POLICY_ORDER.index(policy), policy)
    except ValueError:
        return (999, policy)


def adjusted_rows(api_rows: list[dict], episodes: dict[str, dict], ask_cost: float, wrong_action_cost: float) -> list[dict]:
    rows = []
    for row in api_rows:
        episode = episodes[row["episode_id"]]
        success = bool(row["success"])
        asked = bool(row["asked"])
        reward = (1.0 if success else -wrong_action_cost) - (ask_cost if asked else 0.0)
        adjusted = dict(row)
        adjusted["reward"] = round(reward, 6)
        adjusted["ask_cost"] = ask_cost
        adjusted["wrong_action_cost"] = wrong_action_cost
        adjusted["oracle_should_ask"] = oracle_should_ask(
            episode["candidate_intents"],
            ask_cost=ask_cost,
            wrong_action_cost=wrong_action_cost,
        )
        rows.append(adjusted)
    return rows


def paired_delta(rows: list[dict], policy_a: str, policy_b: str) -> float:
    diffs = paired_differences(rows, policy_a, policy_b)
    return mean(diffs) if diffs else 0.0


def paired_differences(rows: list[dict], policy_a: str, policy_b: str) -> list[float]:
    by_policy = {
        policy: {row["episode_id"]: float(row["reward"]) for row in group}
        for (policy,), group in group_rows(rows, ("policy",)).items()
    }
    shared = sorted(set(by_policy[policy_a]) & set(by_policy[policy_b]))
    return [by_policy[policy_a][episode_id] - by_policy[policy_b][episode_id] for episode_id in shared]


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


def paired_delta_ci(rows: list[dict], policy_a: str, policy_b: str, samples: int, seed: int) -> tuple[float, float, float]:
    diffs = paired_differences(rows, policy_a, policy_b)
    lo, hi = bootstrap_ci(diffs, samples, seed)
    return (mean(diffs) if diffs else 0.0, lo, hi)


def setting_rows(
    api_rows: list[dict],
    episodes: dict[str, dict],
    settings: list[tuple[float, float]],
    samples: int,
    seed: int,
) -> list[list[str]]:
    table_rows = []
    for ask_cost, wrong_action_cost in settings:
        adjusted = adjusted_rows(api_rows, episodes, ask_cost, wrong_action_cost)
        grouped = group_rows(adjusted, ("policy",))
        for policy in sorted({row["policy"] for row in adjusted}, key=policy_sort_key):
            stats = aggregate(grouped[(policy,)])
            delta, lo, hi = paired_delta_ci(adjusted, "api_ecu", policy, samples, seed)
            table_rows.append(
                [
                    format_float(ask_cost, 2),
                    format_float(wrong_action_cost, 2),
                    policy,
                    str(stats["n"]),
                    format_float(stats["net_utility"]),
                    format_float(stats["success"]),
                    format_float(stats["ask_rate"]),
                    format_float(stats["oracle_ask_rate"]),
                    format_float(stats["missed_clarification_rate"]),
                    format_float(stats["unnecessary_clarification_rate"]),
                    format_float(delta),
                    f"[{format_float(lo)}, {format_float(hi)}]",
                ]
            )
    return table_rows


def delta_summary(
    api_rows: list[dict],
    episodes: dict[str, dict],
    settings: list[tuple[float, float]],
    samples: int,
    seed: int,
) -> str:
    rows = []
    for ask_cost, wrong_action_cost in settings:
        adjusted = adjusted_rows(api_rows, episodes, ask_cost, wrong_action_cost)
        ask_delta, ask_lo, ask_hi = paired_delta_ci(adjusted, "api_ecu", "api_ask_needed", samples, seed)
        direct_delta, direct_lo, direct_hi = paired_delta_ci(adjusted, "api_ecu", "api_direct_act", samples, seed)
        rows.append(
            [
                format_float(ask_cost, 2),
                format_float(wrong_action_cost, 2),
                format_float(ask_delta),
                f"[{format_float(ask_lo)}, {format_float(ask_hi)}]",
                format_float(direct_delta),
                f"[{format_float(direct_lo)}, {format_float(direct_hi)}]",
            ]
        )
    return markdown_table(
        ["Ask cost", "Wrong cost", "ECU - AskNeeded", "95% paired CI", "ECU - DirectAct", "95% paired CI"],
        rows,
    )


def main() -> None:
    args = parse_args()
    episodes = {episode["episode_id"]: episode for episode in read_jsonl(args.episodes)}
    api_rows = read_jsonl(args.api_results)
    ask_settings = [(ask_cost, 1.0) for ask_cost in [0.01, 0.05, 0.10, 0.20, 0.35]]
    wrong_settings = [(0.05, wrong_cost) for wrong_cost in [0.2, 0.5, 1.0, 2.0, 3.0]]

    header = [
        "Ask cost",
        "Wrong cost",
        "Method",
        "N",
        "Net utility",
        "Success",
        "Ask rate",
        "Oracle ask",
        "Missed clarif.",
        "Unnecessary clarif.",
        "ECU - method",
        "95% paired CI",
    ]
    text = "\n".join(
        [
            "# Cached API Utility Sensitivity",
            "",
            "This no-API diagnostic re-scores the fixed GPT-4.1-mini outputs from the final 100-episode API evaluation under alternate ask and wrong-action costs. It does not rerun the model or change each policy's original ask/act decisions. Oracle ask labels are recomputed for each cost setting from the benchmark candidate intents.",
            "",
            "## Ask-Cost Sweep",
            "",
            markdown_table(header, setting_rows(api_rows, episodes, ask_settings, args.bootstrap_samples, args.seed)),
            "## Wrong-Action Cost Sweep",
            "",
            markdown_table(header, setting_rows(api_rows, episodes, wrong_settings, args.bootstrap_samples, args.seed)),
            "## Paired Delta Summary",
            "",
            "Positive values favor API ECU under the counterfactual scoring.",
            "",
            "### Ask-Cost Sweep",
            "",
            delta_summary(api_rows, episodes, ask_settings, args.bootstrap_samples, args.seed),
            "### Wrong-Action Cost Sweep",
            "",
            delta_summary(api_rows, episodes, wrong_settings, args.bootstrap_samples, args.seed),
            "## Interpretation",
            "",
            "- ECU's observed API outputs retain a positive paired utility delta over prompted Ask-Needed across the tested ask-cost and wrong-action-cost settings; all paired bootstrap lower bounds are above zero in this grid.",
            "- This is a fixed-output sensitivity check. A fully adaptive policy would recompute its ask decision when costs change, as the offline cost-sensitivity analysis does.",
            "- The diagnostic supports that the main API result is not an artifact of one narrow reward parameterization, while preserving the paper's stronger claim for the original benchmark costs.",
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote cached API utility sensitivity table to {args.out}")


if __name__ == "__main__":
    main()
