from __future__ import annotations

import argparse
import json
from collections import defaultdict

from clarify_to_act.io import read_jsonl, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--out", default="paper/tables/scenario_samples.md")
    parser.add_argument("--per-category", type=int, default=2)
    return parser.parse_args()


def object_summary(obj: dict) -> str:
    owner = obj["owner"] if obj.get("visible_owner", True) else "hidden-owner"
    return f"{obj['id']} ({obj['color']} {obj['type']}, {obj['state']}, {obj['location']}, owner={owner}, salience={obj['salience']})"


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for ep in episodes:
        if ep["split"] == "test" and len(grouped[ep["ambiguity_type"]]) < args.per_category:
            grouped[ep["ambiguity_type"]].append(ep)
    parts = ["# Scenario Samples\n"]
    for category in sorted(grouped):
        parts.append(f"## {category}\n")
        for ep in grouped[category]:
            parts.append(f"### {ep['episode_id']}\n")
            parts.append(f"- Instruction: {ep['user_instruction']}\n")
            parts.append(f"- Variant: {ep['variant']}\n")
            parts.append(f"- Oracle should ask: {ep['oracle_should_ask']}\n")
            parts.append(f"- Costs: ask={ep['ask_cost']}, wrong={ep['wrong_action_cost']}\n")
            parts.append("- Objects:\n")
            for obj in ep["scene"]["objects"]:
                parts.append(f"  - {object_summary(obj)}\n")
            parts.append("- Candidate intents:\n")
            for intent in ep["candidate_intents"]:
                parts.append(f"  - `{json.dumps(intent, sort_keys=True)}`\n")
            parts.append("\n")
    write_text(args.out, "".join(parts))
    print(f"wrote samples to {args.out}")


if __name__ == "__main__":
    main()
