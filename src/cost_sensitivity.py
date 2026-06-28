from __future__ import annotations

import argparse
import copy

from clarify_to_act.generator import eu_advantage, oracle_should_ask
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table
from clarify_to_act.policies import make_policies
from run_experiment import run_episode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--out", default="paper/tables/cost_sensitivity.md")
    parser.add_argument("--split", default="test")
    return parser.parse_args()


def adjust_episode_costs(episode: dict, ask_cost: float, wrong_action_cost: float) -> dict:
    adjusted = copy.deepcopy(episode)
    adjusted["ask_cost"] = ask_cost
    adjusted["wrong_action_cost"] = wrong_action_cost
    adjusted["oracle_should_ask"] = oracle_should_ask(adjusted["candidate_intents"], ask_cost, wrong_action_cost)
    adjusted["features"]["eu_ask_minus_act"] = round(eu_advantage(adjusted["candidate_intents"], ask_cost, wrong_action_cost), 4)
    return adjusted


def run_setting(episodes: list[dict], split: str, ask_cost: float, wrong_action_cost: float) -> list[list[str]]:
    adjusted = [adjust_episode_costs(ep, ask_cost, wrong_action_cost) for ep in episodes]
    train = [ep for ep in adjusted if ep["split"] == "train"]
    dev = [ep for ep in adjusted if ep["split"] == "dev"]
    test = [ep for ep in adjusted if ep["split"] == split]
    policies = make_policies()
    for policy in policies:
        policy.fit(train, dev)
    rows = []
    for policy in policies:
        policy_rows = [run_episode(policy, ep) for ep in test]
        stats = aggregate(policy_rows)
        rows.append(
            [
                format_float(ask_cost, 2),
                format_float(wrong_action_cost, 2),
                policy.name,
                format_float(stats["net_utility"]),
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["oracle_ask_rate"]),
                format_float(stats["missed_clarification_rate"]),
                format_float(stats["unnecessary_clarification_rate"]),
            ]
        )
    return rows


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    sections = ["# Cost Sensitivity\n\n"]

    wrong_rows: list[list[str]] = []
    for wrong_cost in [0.2, 0.5, 1.0, 2.0, 3.0]:
        wrong_rows.extend(run_setting(episodes, args.split, ask_cost=0.05, wrong_action_cost=wrong_cost))
    sections.append("## Wrong-action cost sweep, ask cost fixed at 0.05\n\n")
    sections.append(
        markdown_table(
            [
                "Ask cost",
                "Wrong cost",
                "Method",
                "Net utility",
                "Success",
                "Ask rate",
                "Oracle ask rate",
                "Missed clarif.",
                "Unnecessary clarif.",
            ],
            wrong_rows,
        )
    )

    ask_rows: list[list[str]] = []
    for ask_cost in [0.01, 0.05, 0.10, 0.20, 0.35]:
        ask_rows.extend(run_setting(episodes, args.split, ask_cost=ask_cost, wrong_action_cost=1.0))
    sections.append("\n## Ask-cost sweep, wrong-action cost fixed at 1.0\n\n")
    sections.append(
        markdown_table(
            [
                "Ask cost",
                "Wrong cost",
                "Method",
                "Net utility",
                "Success",
                "Ask rate",
                "Oracle ask rate",
                "Missed clarif.",
                "Unnecessary clarif.",
            ],
            ask_rows,
        )
    )

    write_text(args.out, "".join(sections))
    print(f"wrote cost sensitivity table to {args.out}")


if __name__ == "__main__":
    main()
