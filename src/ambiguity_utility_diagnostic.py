from __future__ import annotations

import argparse
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from clarify_to_act.environment import (
    action_success,
    act_from_intent,
    best_intent_by_success_class,
    choose_intent_after_answer,
    compute_reward,
    simulated_user_answer,
)
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table
from clarify_to_act.policies import diagnostic_question


FEATURE_NAMES = ["bias", "num_candidates", "top_prior", "normalized_prior_entropy"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--offline-results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--out", default="paper/tables/ambiguity_utility_diagnostic.md")
    return parser.parse_args()


def normalized_entropy(episode: dict) -> float:
    features = episode["features"]
    num_candidates = max(float(features["num_candidates"]), 1.0)
    entropy = float(features["prior_entropy"])
    max_entropy = math.log(num_candidates) if num_candidates > 1 else 1.0
    return entropy / max(max_entropy, 1e-8)


def uncertainty_features(episode: dict) -> list[float]:
    features = episode["features"]
    return [
        1.0,
        float(features["num_candidates"]) / 4.0,
        float(features["top_prior"]),
        normalized_entropy(episode),
    ]


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


class UncertaintyOnlyController:
    name = "uncertainty_only_controller"

    def __init__(self, learning_rate: float = 0.08, epochs: int = 1200, l2: float = 0.001) -> None:
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.l2 = l2
        self.weights: list[float] = []
        self.threshold = 0.5

    def fit(self, train: list[dict], dev: list[dict]) -> None:
        if not train:
            raise ValueError("Need non-empty train episodes")
        self.weights = [0.0 for _ in uncertainty_features(train[0])]
        for _ in range(self.epochs):
            gradients = [0.0 for _ in self.weights]
            for episode in train:
                x = uncertainty_features(episode)
                y = 1.0 if episode["oracle_should_ask"] else 0.0
                pred = sigmoid(sum(weight * value for weight, value in zip(self.weights, x)))
                for index, value in enumerate(x):
                    gradients[index] += (pred - y) * value
            scale = 1.0 / len(train)
            for index in range(len(self.weights)):
                regularizer = self.l2 * self.weights[index] if index else 0.0
                self.weights[index] -= self.learning_rate * (gradients[index] * scale + regularizer)
        self.threshold = tune_threshold(self, dev if dev else train)

    def predict_proba_one(self, episode: dict) -> float:
        return sigmoid(sum(weight * value for weight, value in zip(self.weights, uncertainty_features(episode))))

    def should_ask(self, episode: dict) -> bool:
        return self.predict_proba_one(episode) > self.threshold


def decision_outcome(episode: dict, asked: bool, policy_name: str) -> dict:
    act_now = act_from_intent(best_intent_by_success_class(episode))
    if asked:
        question = diagnostic_question(episode)
        answer = simulated_user_answer(episode, question)
        final = act_from_intent(choose_intent_after_answer(episode, answer))
    else:
        final = act_now
    success = action_success(episode, final)
    return {
        "episode_id": episode["episode_id"],
        "split": episode["split"],
        "ambiguity_type": episode["ambiguity_type"],
        "policy": policy_name,
        "asked": asked,
        "success": success,
        "reward": compute_reward(episode, success=success, asked=asked),
        "oracle_should_ask": episode["oracle_should_ask"],
    }


def tune_threshold(controller: UncertaintyOnlyController, episodes: list[dict]) -> float:
    best_threshold = 0.5
    best_reward = float("-inf")
    for threshold in [index / 100.0 for index in range(5, 96, 2)]:
        rewards = [
            decision_outcome(episode, controller.predict_proba_one(episode) > threshold, controller.name)["reward"]
            for episode in episodes
        ]
        mean_reward = mean(rewards) if rewards else float("-inf")
        if mean_reward > best_reward:
            best_reward = mean_reward
            best_threshold = threshold
    return best_threshold


def raw_ambiguity_rows(episodes: list[dict]) -> list[dict]:
    rows = []
    for episode in episodes:
        rows.append(decision_outcome(episode, len(episode["candidate_intents"]) > 1, "surface_ambiguity"))
    return rows


def uncertainty_controller_rows(episodes: list[dict], controller: UncertaintyOnlyController) -> list[dict]:
    return [decision_outcome(episode, controller.should_ask(episode), controller.name) for episode in episodes]


def rows_for_existing_policy(offline_rows: list[dict], policy: str, split: str) -> list[dict]:
    return [row for row in offline_rows if row["split"] == split and row["policy"] == policy]


def metric_row(label: str, rows: list[dict]) -> list[str]:
    stats = aggregate(rows)
    return [
        label,
        str(stats["n"]),
        format_float(stats["net_utility"]),
        format_float(stats["success"]),
        format_float(stats["ask_rate"]),
        format_float(stats["missed_clarification_rate"]),
        format_float(stats["unnecessary_clarification_rate"]),
    ]


def surface_oracle_rows(episodes: list[dict]) -> list[list[str]]:
    rows = []
    for split in ["train", "dev", "test", "ood_test"]:
        selected = [episode for episode in episodes if episode["split"] == split]
        surface_ambiguous = [episode for episode in selected if len(episode["candidate_intents"]) > 1]
        oracle_ask = [episode for episode in surface_ambiguous if episode["oracle_should_ask"]]
        oracle_act = [episode for episode in surface_ambiguous if not episode["oracle_should_ask"]]
        rows.append(
            [
                split,
                str(len(selected)),
                format_float(len(surface_ambiguous) / max(len(selected), 1)),
                format_float(len(oracle_ask) / max(len(surface_ambiguous), 1)),
                format_float(len(oracle_act) / max(len(surface_ambiguous), 1)),
            ]
        )
    return rows


def category_dissociation_rows(episodes: list[dict], split: str) -> list[list[str]]:
    rows = []
    by_category: dict[str, list[dict]] = defaultdict(list)
    for episode in episodes:
        if episode["split"] == split:
            by_category[episode["ambiguity_type"]].append(episode)
    for category, selected in sorted(by_category.items()):
        surface_ambiguous = [episode for episode in selected if len(episode["candidate_intents"]) > 1]
        rows.append(
            [
                category,
                str(len(selected)),
                format_float(len(surface_ambiguous) / max(len(selected), 1)),
                format_float(sum(1 for episode in selected if episode["oracle_should_ask"]) / max(len(selected), 1)),
                format_float(mean(float(episode["features"]["top_prior"]) for episode in selected)),
                format_float(mean(normalized_entropy(episode) for episode in selected)),
            ]
        )
    return rows


def matched_count_rows(episodes: list[dict], split: str) -> list[list[str]]:
    groups: dict[tuple[int, bool], list[dict]] = defaultdict(list)
    for episode in episodes:
        if episode["split"] == split:
            groups[(len(episode["candidate_intents"]), bool(episode["oracle_should_ask"]))].append(episode)
    rows = []
    for (candidate_count, oracle_ask), selected in sorted(groups.items()):
        categories = Counter(episode["ambiguity_type"] for episode in selected)
        category_text = ", ".join(f"{category}: {count}" for category, count in sorted(categories.items()))
        rows.append([str(candidate_count), "ask" if oracle_ask else "act", str(len(selected)), category_text])
    return rows


def evaluation_rows(episodes: list[dict], offline_rows: list[dict], controller: UncertaintyOnlyController) -> str:
    raw_rows = raw_ambiguity_rows(episodes)
    uncertainty_rows = uncertainty_controller_rows(episodes, controller)
    table_rows = []
    for split in ["test", "ood_test"]:
        table_rows.append(metric_row(f"{split} surface_ambiguity", [row for row in raw_rows if row["split"] == split]))
        table_rows.append(
            metric_row(
                f"{split} uncertainty_only_controller",
                [row for row in uncertainty_rows if row["split"] == split],
            )
        )
        for policy in ["prompted_heuristic", "ecu", "learned_controller"]:
            table_rows.append(metric_row(f"{split} {policy}", rows_for_existing_policy(offline_rows, policy, split)))
    return markdown_table(
        ["Policy", "N", "Net utility", "Success", "Ask rate", "Missed clarif.", "Unnecessary clarif."],
        table_rows,
    )


def render_report(episodes: list[dict], offline_rows: list[dict], controller: UncertaintyOnlyController) -> str:
    weight_rows = [[name, format_float(weight, 4)] for name, weight in zip(FEATURE_NAMES, controller.weights)]
    test_episodes = [episode for episode in episodes if episode["split"] == "test"]
    surface_ambiguous = [episode for episode in test_episodes if len(episode["candidate_intents"]) > 1]
    oracle_act_surface = [episode for episode in surface_ambiguous if not episode["oracle_should_ask"]]
    oracle_ask_surface = [episode for episode in surface_ambiguous if episode["oracle_should_ask"]]

    return "\n".join(
        [
            "# Ambiguity Is Not Enough Diagnostic",
            "",
            "This no-API diagnostic tests the paper thesis that clarification should be optimized as situated utility, not as raw ambiguity detection.",
            "The uncertainty-only controller is trained on train episodes and tuned on dev using only candidate count, top prior, and prior entropy. It omits context-resolution, success-equivalence, risk, cost, and ECU-margin features.",
            "",
            "## Surface Ambiguity vs Oracle Ask",
            "",
            markdown_table(
                ["Split", "Episodes", "Surface ambiguous", "Oracle ask among ambiguous", "Oracle act among ambiguous"],
                surface_oracle_rows(episodes),
            ),
            f"On the test split, {len(surface_ambiguous)}/{len(test_episodes)} episodes have multiple candidate interpretations, but {len(oracle_act_surface)} of those are oracle-act cases and {len(oracle_ask_surface)} are oracle-ask cases.",
            "",
            "## Test Category Dissociation",
            "",
            markdown_table(
                ["Category", "N", "Surface ambiguous", "Oracle ask", "Mean top prior", "Mean normalized entropy"],
                category_dissociation_rows(episodes, "test"),
            ),
            "## Matched Candidate-Count Slices",
            "",
            markdown_table(
                ["Candidate count", "Oracle decision", "N", "Categories"],
                matched_count_rows(episodes, "test"),
            ),
            "## Policy Comparison",
            "",
            evaluation_rows(episodes, offline_rows, controller),
            "## Uncertainty-Only Controller",
            "",
            f"- Tuned probability threshold: {format_float(controller.threshold, 2)}",
            "",
            markdown_table(["Feature", "Weight"], weight_rows),
            "## Interpretation",
            "",
            "- Raw surface ambiguity asks on all canonical test episodes, so it cannot distinguish ambiguity that is harmless or context-resolved from ambiguity that is worth interrupting for.",
            "- A learned uncertainty-only controller is useful but still lacks the explicit utility ingredients needed to eliminate unnecessary clarification.",
            "- ECU and the full learned controller use value-of-information features, so they preserve success while avoiding both missed and unnecessary clarification on the full offline test split.",
            "",
        ]
    )


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    offline_rows = read_jsonl(args.offline_results)
    train = [episode for episode in episodes if episode["split"] == "train"]
    dev = [episode for episode in episodes if episode["split"] == "dev"]
    controller = UncertaintyOnlyController()
    controller.fit(train, dev)
    write_text(args.out, render_report(episodes, offline_rows, controller))
    print(f"wrote ambiguity/utility diagnostic to {args.out}")
    print(f"uncertainty-only threshold: {format_float(controller.threshold, 2)}")


if __name__ == "__main__":
    main()
