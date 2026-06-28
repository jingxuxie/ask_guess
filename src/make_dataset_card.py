from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


CATEGORY_DESCRIPTIONS = {
    "referential": "Multiple visible candidates match the instruction and wrong target matters.",
    "context_resolved": "Language is underspecified, but reachability, salience, or local context makes one action utility-dominant.",
    "equivalent_outcome": "Multiple candidates exist, but they share one success-equivalence class.",
    "risk_sensitive": "One candidate may be likely, but wrong-action cost makes asking utility-dominant.",
    "preference_social": "Owner or user preference determines whether to infer from visible context or ask.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--style-episodes", default="data/generated/style_stress_episodes.jsonl")
    parser.add_argument("--ambiguity-mix-episodes", default="data/generated/ambiguity_mix_shift_episodes.jsonl")
    parser.add_argument("--out", default="paper/dataset_card.md")
    return parser.parse_args()


def split_table(episodes: list[dict]) -> str:
    rows = []
    by_split = Counter(ep["split"] for ep in episodes)
    for split, count in sorted(by_split.items()):
        split_eps = [ep for ep in episodes if ep["split"] == split]
        rows.append(
            [
                split,
                str(count),
                format_float(sum(1 for ep in split_eps if ep["oracle_should_ask"]) / count),
                str(len({ep["ambiguity_type"] for ep in split_eps})),
            ]
        )
    return markdown_table(["Split", "Episodes", "Oracle ask rate", "Categories"], rows)


def category_table(episodes: list[dict]) -> str:
    rows = []
    by_category: dict[str, list[dict]] = defaultdict(list)
    for ep in episodes:
        by_category[ep["ambiguity_type"]].append(ep)
    for category, eps in sorted(by_category.items()):
        variants = ", ".join(sorted({ep["variant"] for ep in eps}))
        rows.append(
            [
                category,
                str(len(eps)),
                format_float(sum(1 for ep in eps if ep["oracle_should_ask"]) / len(eps)),
                variants,
                CATEGORY_DESCRIPTIONS.get(category, ""),
            ]
        )
    return markdown_table(["Category", "Episodes", "Oracle ask rate", "Variants", "Diagnostic purpose"], rows)


def field_table(episodes: list[dict]) -> str:
    episode_keys = sorted({key for ep in episodes for key in ep})
    scene_keys = sorted({key for ep in episodes for key in ep["scene"]})
    object_keys = sorted({key for ep in episodes for obj in ep["scene"]["objects"] for key in obj})
    intent_keys = sorted({key for ep in episodes for intent in ep["candidate_intents"] for key in intent})
    rows = [
        ["Episode", ", ".join(episode_keys)],
        ["Scene", ", ".join(scene_keys)],
        ["Object", ", ".join(object_keys)],
        ["Candidate intent", ", ".join(intent_keys)],
    ]
    return markdown_table(["Record", "Fields"], rows)


def action_cost_table(episodes: list[dict]) -> str:
    actions = sorted({intent["action"] for ep in episodes for intent in ep["candidate_intents"]})
    ask_costs = sorted({float(ep["ask_cost"]) for ep in episodes})
    wrong_costs = sorted({float(ep["wrong_action_cost"]) for ep in episodes})
    object_types = sorted({obj["type"] for ep in episodes for obj in ep["scene"]["objects"]})
    rows = [
        ["Actions", ", ".join(actions)],
        ["Ask costs", ", ".join(format_float(value, 2) for value in ask_costs)],
        ["Wrong-action costs", ", ".join(format_float(value, 2) for value in wrong_costs)],
        ["Object types", ", ".join(object_types)],
    ]
    return markdown_table(["Dimension", "Values"], rows)


def leakage_control_table(episodes: list[dict]) -> str:
    preference = [ep for ep in episodes if ep["ambiguity_type"] == "preference_social"]
    hidden_owner = [ep for ep in preference if ep["variant"] == "owner_hidden"]
    visible_owner = [ep for ep in preference if ep["variant"] == "owner_visible"]
    hidden_objects = [obj for ep in hidden_owner for obj in ep["scene"]["objects"]]
    visible_objects = [obj for ep in visible_owner for obj in ep["scene"]["objects"]]
    neutral_hidden_states = sorted({obj["state"] for obj in hidden_objects})
    rows = [
        ["Hidden-owner preference episodes", str(len(hidden_owner)), "Owners are present in the canonical JSON for scoring but marked `visible_owner=false` for API prompts."],
        ["Visible-owner preference episodes", str(len(visible_owner)), "`current_user` is included and object owners are visible, so `my` can be resolved without asking."],
        ["Hidden-owner object states", ", ".join(neutral_hidden_states), "Hidden-owner states are neutral rather than labels such as personal or guest."],
        ["Hidden-owner object owner visibility", str(all(obj.get("visible_owner") is False for obj in hidden_objects)), "API prompts replace hidden owners with `unknown`."],
        ["Visible-owner object owner visibility", str(all(obj.get("visible_owner") is True for obj in visible_objects)), "Visible cases keep owner information available."],
    ]
    return markdown_table(["Check", "Value", "Purpose"], rows)


def style_table(style_episodes: list[dict]) -> str:
    by_category = Counter(ep["ambiguity_type"] for ep in style_episodes)
    rows = []
    for category, count in sorted(by_category.items()):
        eps = [ep for ep in style_episodes if ep["ambiguity_type"] == category]
        rows.append([category, str(count), format_float(sum(1 for ep in eps if ep["oracle_should_ask"]) / count)])
    return markdown_table(["Category", "Style-stress episodes", "Oracle ask rate"], rows)


def ambiguity_mix_table(episodes: list[dict]) -> str:
    counts = Counter((ep["split"], ep["ambiguity_type"]) for ep in episodes)
    rows = []
    for split, category in sorted(counts):
        eps = [ep for ep in episodes if ep["split"] == split and ep["ambiguity_type"] == category]
        rows.append([split, category, str(counts[(split, category)]), format_float(sum(1 for ep in eps if ep["oracle_should_ask"]) / len(eps))])
    return markdown_table(["Split", "Category", "Episodes", "Oracle ask rate"], rows)


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    style_episodes = read_jsonl(args.style_episodes)
    ambiguity_mix_episodes = read_jsonl(args.ambiguity_mix_episodes)
    total_oracle_ask_rate = sum(1 for ep in episodes if ep["oracle_should_ask"]) / len(episodes)

    text = "\n".join(
        [
            "# Clarify-to-Act Dataset Card",
            "",
            "This generated card summarizes the canonical synthetic benchmark data used by the current paper draft.",
            "",
            "## Overview",
            "",
            markdown_table(
                ["Item", "Value"],
                [
                    ["Canonical file", args.episodes],
                    ["Total episodes", str(len(episodes))],
                    ["Overall oracle ask rate", format_float(total_oracle_ask_rate)],
                    ["Style-stress file", args.style_episodes],
                    ["Style-stress episodes", str(len(style_episodes))],
                    ["Ambiguity-mix shift file", args.ambiguity_mix_episodes],
                    ["Ambiguity-mix shift episodes", str(len(ambiguity_mix_episodes))],
                ],
            ),
            "## Intended Use",
            "",
            "The dataset is intended for controlled evaluation of first-turn clarify-versus-act policies in situated instruction following. It isolates context resolution, outcome equivalence, ask cost, wrong-action cost, and hidden user intent under deterministic scoring.",
            "",
            "## Not Intended Use",
            "",
            "The dataset is not evidence for real household deployment, perception, long-horizon planning, or unconstrained human dialogue. It should not be used to claim broad embodied robustness without external validation.",
            "",
            "## Splits",
            "",
            split_table(episodes),
            "## Categories",
            "",
            category_table(episodes),
            "## Schema",
            "",
            field_table(episodes),
            "## Actions, Costs, and Object Types",
            "",
            action_cost_table(episodes),
            "## Leakage Controls",
            "",
            leakage_control_table(episodes),
            "## Style-Stress Set",
            "",
            "The style-stress set preserves hidden intents and utility labels while paraphrasing instructions and changing simulated user answer style.",
            "",
            style_table(style_episodes),
            "## Held-Out Ambiguity-Mix Diagnostic",
            "",
            "This auxiliary no-API diagnostic trains and tunes offline policies on referential, context-resolved, and equivalent-outcome episodes, then tests transfer to risk-sensitive and preference/social episodes.",
            "",
            ambiguity_mix_table(ambiguity_mix_episodes),
            "## Scoring",
            "",
            "The agent receives the visible scene and instruction, then either acts immediately or asks one clarifying question. A final action succeeds if it matches the hidden intent's success-equivalence class. Net reward is task success minus clarification cost and wrong-action cost.",
            "",
            "## Known Limitations",
            "",
            "- Synthetic scenes and deterministic simulated answers.",
            "- No perception, physics, or long-horizon planning.",
            "- Generated candidate priors and costs are part of the controlled benchmark design.",
            "- Author audits are sanity checks, not independent human-subject validation.",
        ]
    )
    write_text(args.out, text)
    print(f"wrote dataset card to {args.out}")


if __name__ == "__main__":
    main()
