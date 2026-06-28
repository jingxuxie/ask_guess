from __future__ import annotations

import argparse
import copy
from collections import Counter

from clarify_to_act.io import read_jsonl, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--source-split", default="test")
    parser.add_argument("--out-split", default="style_test")
    parser.add_argument("--limit-per-category", type=int, default=10)
    parser.add_argument("--out", default="data/generated/style_stress_episodes.jsonl")
    return parser.parse_args()


def humanize(value: object) -> str:
    return str(value).replace("_", " ")


def target_object(episode: dict, intent: dict | None = None) -> dict:
    objects = {obj["id"]: obj for obj in episode["scene"]["objects"]}
    if intent is None:
        intent = episode["candidate_intents"][0]
    return objects[intent["target_id"]]


def hidden_target(episode: dict) -> dict:
    hidden_intent = next(intent for intent in episode["candidate_intents"] if intent["intent_id"] == episode["hidden_intent_id"])
    return target_object(episode, hidden_intent)


def paraphrased_instruction(episode: dict) -> str:
    obj = target_object(episode)
    obj_type = humanize(obj["type"])
    color = humanize(obj.get("color", ""))
    category = episode["ambiguity_type"]
    if category == "referential":
        return f"Could you grab the {color} {obj_type} for me when you get a chance?"
    if category == "context_resolved":
        return f"Please pass me the {obj_type} I'm using right now."
    if category == "equivalent_outcome":
        return f"Please move any spare {obj_type} to the table."
    if category == "risk_sensitive":
        return f"Delete the old {obj_type}, but make sure it's the right one."
    if category == "preference_social":
        return f"Can you tidy away my {obj_type}?"
    return str(episode["user_instruction"])


def style_shifted_answers(episode: dict) -> dict:
    target = hidden_target(episode)
    state = humanize(target["state"])
    location = humanize(target["location"])
    owner = str(target["owner"])
    return {
        "default": f"The {state} one, over at the {location}.",
        "state": f"The {state} one.",
        "location": f"Over at the {location}.",
        "owner": f"It belongs to {owner}.",
    }


def transform_episode(episode: dict) -> dict:
    transformed = copy.deepcopy(episode)
    transformed["stress_original_episode_id"] = episode["episode_id"]
    transformed["stress_type"] = "instruction_paraphrase_and_answer_style"
    transformed["episode_id"] = f"{episode['episode_id']}_style"
    transformed["split"] = "style_test"
    transformed["user_instruction"] = paraphrased_instruction(episode)
    transformed["oracle_clarifying_answers"] = style_shifted_answers(episode)
    return transformed


def select_stratified(episodes: list[dict], source_split: str, limit_per_category: int) -> list[dict]:
    counts: Counter[str] = Counter()
    selected = []
    for episode in episodes:
        if episode["split"] != source_split:
            continue
        category = episode["ambiguity_type"]
        if counts[category] >= limit_per_category:
            continue
        selected.append(episode)
        counts[category] += 1
    return selected


def main() -> None:
    args = parse_args()
    selected = select_stratified(read_jsonl(args.episodes), args.source_split, args.limit_per_category)
    transformed = []
    for episode in selected:
        new_episode = transform_episode(episode)
        new_episode["split"] = args.out_split
        transformed.append(new_episode)
    write_jsonl(args.out, transformed)
    print(f"wrote {len(transformed)} style-stress episodes to {args.out}")
    print(f"source split: {args.source_split}; output split: {args.out_split}")
    print(f"categories: {dict(sorted(Counter(ep['ambiguity_type'] for ep in transformed).items()))}")


if __name__ == "__main__":
    main()
