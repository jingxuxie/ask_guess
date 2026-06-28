from __future__ import annotations

import argparse
import math
from statistics import mean

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--out", default="paper/tables/situated_contrast_analysis.md")
    return parser.parse_args()


def normalized_entropy(episode: dict) -> float:
    features = episode["features"]
    num_candidates = max(float(features["num_candidates"]), 1.0)
    max_entropy = math.log(num_candidates) if num_candidates > 1 else 1.0
    return float(features["prior_entropy"]) / max(max_entropy, 1e-8)


def action_name(episode: dict) -> str:
    return str(episode["candidate_intents"][0]["action"])


def visible_owner(episode: dict) -> bool:
    return all(bool(obj.get("visible_owner", True)) for obj in episode["scene"]["objects"])


def summarize_slice(label: str, rows: list[dict]) -> list[str]:
    return [
        label,
        str(len(rows)),
        format_float(sum(1 for row in rows if row["oracle_should_ask"]) / max(len(rows), 1)),
        format_float(mean(float(row["features"]["top_prior"]) for row in rows)),
        format_float(mean(normalized_entropy(row) for row in rows)),
        format_float(mean(float(row["features"]["num_success_classes"]) for row in rows)),
        format_float(mean(float(row["ask_cost"]) for row in rows)),
        format_float(mean(float(row["wrong_action_cost"]) for row in rows)),
        format_float(mean(float(row["features"]["eu_ask_minus_act"]) for row in rows)),
    ]


def contrast_slices(test_episodes: list[dict]) -> dict[str, list[dict]]:
    return {
        "bring / 2 candidates / context-resolved": [
            episode
            for episode in test_episodes
            if action_name(episode) == "bring"
            and episode["ambiguity_type"] == "context_resolved"
            and episode["features"]["num_candidates"] == 2
        ],
        "bring / 2 candidates / referential": [
            episode
            for episode in test_episodes
            if action_name(episode) == "bring"
            and episode["ambiguity_type"] == "referential"
            and episode["features"]["num_candidates"] == 2
        ],
        "put-away preference / owner visible": [
            episode
            for episode in test_episodes
            if episode["ambiguity_type"] == "preference_social" and episode["variant"] == "owner_visible"
        ],
        "put-away preference / owner hidden": [
            episode
            for episode in test_episodes
            if episode["ambiguity_type"] == "preference_social" and episode["variant"] == "owner_hidden"
        ],
        "high entropy / equivalent outcomes": [
            episode for episode in test_episodes if episode["ambiguity_type"] == "equivalent_outcome"
        ],
        "high top-prior / high wrong-action cost": [
            episode
            for episode in test_episodes
            if episode["ambiguity_type"] == "risk_sensitive" and float(episode["features"]["top_prior"]) >= 0.75
        ],
    }


def example_key_factors(episode: dict) -> str:
    features = episode["features"]
    parts = [
        f"candidates={features['num_candidates']}",
        f"classes={features['num_success_classes']}",
        f"top_prior={format_float(float(features['top_prior']))}",
        f"norm_entropy={format_float(normalized_entropy(episode))}",
        f"ask_cost={format_float(float(episode['ask_cost']))}",
        f"wrong_cost={format_float(float(episode['wrong_action_cost']))}",
    ]
    if episode.get("context_resolves_instruction"):
        parts.append("context_resolves=true")
    if episode.get("candidates_equivalent_for_success"):
        parts.append("equivalent_success=true")
    if episode["ambiguity_type"] == "preference_social":
        parts.append(f"owner_visible={str(visible_owner(episode)).lower()}")
    if episode.get("risk_level") == "high":
        parts.append("risk=high")
    return "; ".join(parts)


def choose_example(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("cannot choose example from empty rows")
    return sorted(rows, key=lambda row: row["episode_id"])[0]


def example_rows(slices: dict[str, list[dict]]) -> list[list[str]]:
    rows = []
    for label, episodes in slices.items():
        episode = choose_example(episodes)
        rows.append(
            [
                label,
                episode["episode_id"],
                episode["user_instruction"],
                "ASK" if episode["oracle_should_ask"] else "ACT",
                format_float(float(episode["features"]["eu_ask_minus_act"])),
                example_key_factors(episode),
            ]
        )
    return rows


def render_report(episodes: list[dict]) -> str:
    test_episodes = [episode for episode in episodes if episode["split"] == "test"]
    slices = contrast_slices(test_episodes)
    missing = [label for label, rows in slices.items() if not rows]
    if missing:
        raise ValueError(f"missing required contrast slices: {missing}")
    slice_rows = [summarize_slice(label, rows) for label, rows in slices.items()]
    return "\n".join(
        [
            "# Situated Contrast Analysis",
            "",
            "This no-API diagnostic makes the paper's situated-decision thesis concrete: similar surface ambiguity can imply different ask/act decisions once context, equivalence, risk, and interaction cost are included.",
            "",
            "## Aggregate Contrasts",
            "",
            markdown_table(
                [
                    "Slice",
                    "N",
                    "Oracle ask",
                    "Mean top prior",
                    "Mean norm. entropy",
                    "Mean success classes",
                    "Mean ask cost",
                    "Mean wrong cost",
                    "Mean EU ask-act",
                ],
                slice_rows,
            ),
            "## Representative Episodes",
            "",
            markdown_table(
                ["Contrast slice", "Episode", "Instruction", "Oracle", "EU ask-act", "Key factors"],
                example_rows(slices),
            ),
            "## Interpretation",
            "",
            "- The same two-candidate `bring` action family splits cleanly: context-resolved cases should act, while referential cases should ask.",
            "- Preference/social examples use the same instruction family, but visible ownership makes acting optimal while hidden ownership makes asking optimal.",
            "- Equivalent-outcome cases have high entropy and three candidates, yet acting is optimal because all candidates share one success class.",
            "- Risk-sensitive cases can have high top-prior confidence, yet asking is still optimal because the wrong-action cost is high.",
            "",
        ]
    )


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    write_text(args.out, render_report(episodes))
    print(f"wrote situated contrast analysis to {args.out}")


if __name__ == "__main__":
    main()
