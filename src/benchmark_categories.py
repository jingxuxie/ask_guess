from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


CATEGORY_ORDER = [
    "referential",
    "context_resolved",
    "equivalent_outcome",
    "risk_sensitive",
    "preference_social",
]

CATEGORY_LABELS = {
    "referential": "Referential ambiguity",
    "context_resolved": "Context-resolved",
    "equivalent_outcome": "Equivalent outcome",
    "risk_sensitive": "Risk-sensitive",
    "preference_social": "Preference/social",
}

CATEGORY_ROLES = {
    "referential": "Multiple matching objects; wrong target matters.",
    "context_resolved": "Language is underspecified, but context/salience resolves it.",
    "equivalent_outcome": "Multiple targets exist, but any choice succeeds.",
    "risk_sensitive": "Moderate uncertainty with high wrong-action cost.",
    "preference_social": "Owner or preference determines whether to ask or act.",
}

CATEGORY_POLICY = {
    "referential": "Ask",
    "context_resolved": "Act",
    "equivalent_outcome": "Act",
    "risk_sensitive": "Ask",
    "preference_social": "Ask iff owner hidden",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--out", default="paper/tables/benchmark_categories.md")
    return parser.parse_args()


def sample_instruction(episodes: list[dict], category: str) -> str:
    for episode in episodes:
        if episode["split"] == "test" and episode["ambiguity_type"] == category:
            return episode["user_instruction"]
    for episode in episodes:
        if episode["ambiguity_type"] == category:
            return episode["user_instruction"]
    return ""


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    counts = Counter(episode["ambiguity_type"] for episode in episodes)
    oracle_by_category: dict[str, list[bool]] = defaultdict(list)
    for episode in episodes:
        oracle_by_category[episode["ambiguity_type"]].append(bool(episode["oracle_should_ask"]))

    rows = []
    for category in CATEGORY_ORDER:
        oracle_values = oracle_by_category[category]
        oracle_ask_rate = sum(oracle_values) / len(oracle_values)
        rows.append(
            [
                CATEGORY_LABELS[category],
                str(counts[category]),
                format_float(oracle_ask_rate),
                CATEGORY_POLICY[category],
                CATEGORY_ROLES[category],
                sample_instruction(episodes, category),
            ]
        )
    text = "\n".join(
        [
            "# Benchmark Categories",
            "",
            "Counts and oracle ask rates are computed from the canonical generated dataset.",
            "",
            markdown_table(["Category", "Episodes", "Oracle ask", "Expected behavior", "Diagnostic role", "Example instruction"], rows),
        ]
    )
    write_text(args.out, text)
    print(f"wrote benchmark category table to {args.out}")


if __name__ == "__main__":
    main()
