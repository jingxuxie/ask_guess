from __future__ import annotations

import argparse
from collections import Counter

from clarify_to_act.generator import generate_dataset
from clarify_to_act.io import write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=int, default=600)
    parser.add_argument("--dev", type=int, default=200)
    parser.add_argument("--test", type=int, default=400)
    parser.add_argument("--ood-test", type=int, default=0)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--out", default="data/generated/episodes.jsonl")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    episodes = generate_dataset(args.train, args.dev, args.test, args.ood_test, args.seed)
    write_jsonl(args.out, episodes)
    by_split = Counter(ep["split"] for ep in episodes)
    by_category = Counter(ep["ambiguity_type"] for ep in episodes)
    ask_rate = sum(1 for ep in episodes if ep["oracle_should_ask"]) / max(len(episodes), 1)
    print(f"wrote {len(episodes)} episodes to {args.out}")
    print(f"splits: {dict(sorted(by_split.items()))}")
    print(f"categories: {dict(sorted(by_category.items()))}")
    print(f"oracle ask rate: {ask_rate:.3f}")


if __name__ == "__main__":
    main()
