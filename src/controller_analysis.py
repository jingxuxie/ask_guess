from __future__ import annotations

import argparse
from collections import defaultdict

from clarify_to_act.controller import LogisticAskController
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table
from clarify_to_act.policies import ECUThresholdPolicy


FEATURE_NAMES = [
    "intercept",
    "num candidates / 4",
    "success-class ratio",
    "top prior",
    "normalized entropy",
    "ask cost x10",
    "wrong-action cost / 3",
    "salience gap",
    "EU ask-act margin",
    "context resolves",
    "candidates equivalent",
    "risk level",
]

POLICY_ORDER = ["prompted_heuristic", "ecu", "ecu_threshold", "learned_controller"]
CATEGORY_ORDER = ["context_resolved", "equivalent_outcome", "preference_social", "referential", "risk_sensitive"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--offline-results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--out", default="paper/tables/controller_analysis.md")
    return parser.parse_args()


def split_episodes(episodes: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    train = [episode for episode in episodes if episode["split"] == "train"]
    dev = [episode for episode in episodes if episode["split"] == "dev"]
    eval_episodes = [episode for episode in episodes if episode["split"] in {"test", "ood_test"}]
    return train, dev, eval_episodes


def fit_controllers(train: list[dict], dev: list[dict]) -> tuple[ECUThresholdPolicy, LogisticAskController]:
    ecu_threshold = ECUThresholdPolicy()
    ecu_threshold.fit(train, dev)
    learned = LogisticAskController()
    learned.fit(train, dev)
    return ecu_threshold, learned


def threshold_table(ecu_threshold: ECUThresholdPolicy, learned: LogisticAskController) -> str:
    rows = [
        ["ECU threshold", "EU(ask)-EU(act)", format_float(ecu_threshold.threshold)],
        ["Learned controller", "P(ask)", format_float(learned.threshold)],
    ]
    return markdown_table(["Controller", "Decision score", "Tuned threshold"], rows)


def weight_table(learned: LogisticAskController) -> str:
    rows = []
    for name, weight in sorted(zip(FEATURE_NAMES, learned.weights), key=lambda item: abs(item[1]), reverse=True):
        direction = "ask" if weight > 0 else "act"
        rows.append([name, format_float(weight), direction])
    return markdown_table(["Feature", "Weight", "Positive direction"], rows)


def policy_sort_key(policy: str) -> tuple[int, str]:
    try:
        return (POLICY_ORDER.index(policy), policy)
    except ValueError:
        return (999, policy)


def offline_metric_table(rows: list[dict]) -> str:
    selected = [row for row in rows if row["policy"] in set(POLICY_ORDER)]
    grouped = group_rows(selected, ("split", "policy"))
    table_rows = []
    for split, policy in sorted(grouped, key=lambda key: (key[0], policy_sort_key(key[1]))):
        stats = aggregate(grouped[(split, policy)])
        table_rows.append(
            [
                split,
                policy,
                str(stats["n"]),
                format_float(stats["net_utility"]),
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["missed_clarification_rate"]),
                format_float(stats["unnecessary_clarification_rate"]),
            ]
        )
    return markdown_table(
        ["Split", "Method", "N", "Net utility", "Success", "Ask rate", "Missed clarif.", "Unnecessary clarif."],
        table_rows,
    )


def learned_category_table(rows: list[dict]) -> str:
    selected = [row for row in rows if row["policy"] == "learned_controller"]
    grouped = group_rows(selected, ("split", "ambiguity_type"))
    table_rows = []
    for split in ["test", "ood_test"]:
        for category in CATEGORY_ORDER:
            group = grouped.get((split, category), [])
            if not group:
                continue
            stats = aggregate(group)
            table_rows.append(
                [
                    split,
                    category,
                    str(stats["n"]),
                    format_float(stats["ask_rate"]),
                    format_float(stats["oracle_ask_rate"]),
                    format_float(stats["net_utility"]),
                    format_float(stats["success"]),
                ]
            )
    return markdown_table(["Split", "Category", "N", "Ask rate", "Oracle ask", "Net utility", "Success"], table_rows)


def probability_summary(learned: LogisticAskController, eval_episodes: list[dict]) -> str:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for episode in eval_episodes:
        grouped[(episode["split"], episode["ambiguity_type"])].append(learned.predict_proba_one(episode))
    rows = []
    for split in ["test", "ood_test"]:
        for category in CATEGORY_ORDER:
            values = grouped.get((split, category), [])
            if not values:
                continue
            rows.append([split, category, str(len(values)), format_float(sum(values) / len(values)), format_float(min(values)), format_float(max(values))])
    return markdown_table(["Split", "Category", "N", "Mean P(ask)", "Min", "Max"], rows)


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    offline_rows = read_jsonl(args.offline_results)
    train, dev, eval_episodes = split_episodes(episodes)
    ecu_threshold, learned = fit_controllers(train, dev)

    text = "\n".join(
        [
            "# Controller Analysis",
            "",
            "This generated report documents the lightweight interaction-supervised ask/act controller trained from automatic oracle labels.",
            "",
            "## Tuned Thresholds",
            "",
            threshold_table(ecu_threshold, learned),
            "## Learned Logistic Weights",
            "",
            "Weights are shown in descending absolute value. Positive weights increase the probability of asking.",
            "",
            weight_table(learned),
            "## Offline Controller Metrics",
            "",
            offline_metric_table(offline_rows),
            "## Learned Controller by Category",
            "",
            learned_category_table(offline_rows),
            "## Learned Ask Probability by Category",
            "",
            probability_summary(learned, eval_episodes),
        ]
    )
    write_text(args.out, text)
    print(f"wrote controller analysis to {args.out}")


if __name__ == "__main__":
    main()
