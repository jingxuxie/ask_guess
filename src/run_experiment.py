from __future__ import annotations

import argparse
from collections import Counter

from clarify_to_act.environment import action_success, compute_reward, simulated_user_answer
from clarify_to_act.io import read_jsonl, write_jsonl
from clarify_to_act.policies import make_policies


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--out", default="data/runs/offline_results.jsonl")
    parser.add_argument("--policies", default="")
    parser.add_argument("--eval-splits", default="test,ood_test")
    parser.add_argument("--limit-per-split", type=int, default=0)
    return parser.parse_args()


def filtered_episodes(episodes: list[dict], splits: set[str], limit_per_split: int) -> list[dict]:
    counts: Counter[str] = Counter()
    selected = []
    for episode in episodes:
        split = episode["split"]
        if split not in splits:
            continue
        if limit_per_split and counts[split] >= limit_per_split:
            continue
        selected.append(episode)
        counts[split] += 1
    return selected


def run_episode(policy, episode: dict) -> dict:
    first = policy.first_turn(episode)
    asked = first.get("type") == "ASK"
    question = first.get("question") if asked else None
    answer = None
    if asked:
        answer = simulated_user_answer(episode, question or "")
        final = policy.second_turn(episode, question or "", answer)
    else:
        final = first
    success = action_success(episode, final)
    reward = compute_reward(episode, success=success, asked=asked)
    return {
        "episode_id": episode["episode_id"],
        "split": episode["split"],
        "ambiguity_type": episode["ambiguity_type"],
        "variant": episode["variant"],
        "policy": policy.name,
        "asked": asked,
        "question": question,
        "answer": answer,
        "final_action": final,
        "success": success,
        "reward": reward,
        "oracle_should_ask": episode["oracle_should_ask"],
        "ask_cost": episode["ask_cost"],
        "wrong_action_cost": episode["wrong_action_cost"],
        "features": episode["features"],
    }


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    train = [ep for ep in episodes if ep["split"] == "train"]
    dev = [ep for ep in episodes if ep["split"] == "dev"]
    policy_names = [name.strip() for name in args.policies.split(",") if name.strip()] or None
    policies = make_policies(policy_names)
    for policy in policies:
        policy.fit(train, dev)
    eval_splits = {split.strip() for split in args.eval_splits.split(",") if split.strip()}
    eval_episodes = filtered_episodes(episodes, eval_splits, args.limit_per_split)
    rows = []
    for policy in policies:
        for episode in eval_episodes:
            rows.append(run_episode(policy, episode))
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} results to {args.out}")
    print(f"evaluated splits: {sorted(eval_splits)}")
    print(f"episodes per split: {dict(Counter(ep['split'] for ep in eval_episodes))}")
    tuned = {getattr(policy, "name", ""): getattr(policy, "threshold") for policy in policies if hasattr(policy, "threshold")}
    controller_thresholds = {
        policy.name: policy.controller.threshold
        for policy in policies
        if hasattr(policy, "controller") and hasattr(policy.controller, "threshold")
    }
    if tuned:
        print(f"tuned thresholds: {tuned}")
    if controller_thresholds:
        print(f"controller thresholds: {controller_thresholds}")


if __name__ == "__main__":
    main()
