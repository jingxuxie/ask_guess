from __future__ import annotations

import argparse
import random
from collections.abc import Callable

from clarify_to_act.generator import (
    EVERYDAY_TYPES,
    HELDOUT_TYPES,
    make_context_resolved,
    make_equivalent_outcome,
    make_preference_social,
    make_referential,
    make_risk_sensitive,
)
from clarify_to_act.io import write_jsonl


Maker = Callable[[int, str, random.Random, list[str]], dict]

SEEN_MAKERS: list[Maker] = [
    make_referential,
    make_context_resolved,
    make_equivalent_outcome,
]

HELDOUT_MAKERS: list[Maker] = [
    make_risk_sensitive,
    make_preference_social,
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-per-seen-category", type=int, default=200)
    parser.add_argument("--dev-per-seen-category", type=int, default=60)
    parser.add_argument("--test-per-seen-category", type=int, default=100)
    parser.add_argument("--ood-per-heldout-category", type=int, default=100)
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--out", default="data/generated/ambiguity_mix_shift_episodes.jsonl")
    return parser.parse_args()


def make_split(
    split: str,
    makers: list[Maker],
    per_category: int,
    rng: random.Random,
    object_pool: list[str],
    id_offset: int,
) -> list[dict]:
    episodes = []
    for maker_index, maker in enumerate(makers):
        for local_idx in range(per_category):
            idx = id_offset + maker_index * per_category + local_idx
            episodes.append(maker(idx, split, rng, object_pool))
    rng.shuffle(episodes)
    return episodes


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    episodes = []
    episodes.extend(make_split("train", SEEN_MAKERS, args.train_per_seen_category, rng, EVERYDAY_TYPES, 0))
    episodes.extend(make_split("dev", SEEN_MAKERS, args.dev_per_seen_category, rng, EVERYDAY_TYPES, 100_000))
    episodes.extend(make_split("test", SEEN_MAKERS, args.test_per_seen_category, rng, EVERYDAY_TYPES, 200_000))
    episodes.extend(
        make_split(
            "ood_ambiguity_mix",
            HELDOUT_MAKERS,
            args.ood_per_heldout_category,
            rng,
            HELDOUT_TYPES,
            300_000,
        )
    )
    write_jsonl(args.out, episodes)
    print(f"wrote {len(episodes)} ambiguity-mix shift episodes to {args.out}")
    print(
        "splits: "
        f"train={args.train_per_seen_category * len(SEEN_MAKERS)}, "
        f"dev={args.dev_per_seen_category * len(SEEN_MAKERS)}, "
        f"test={args.test_per_seen_category * len(SEEN_MAKERS)}, "
        f"ood_ambiguity_mix={args.ood_per_heldout_category * len(HELDOUT_MAKERS)}"
    )


if __name__ == "__main__":
    main()
