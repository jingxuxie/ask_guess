from __future__ import annotations

import argparse
import random
from statistics import mean

from clarify_to_act.environment import action_success, compute_reward
from clarify_to_act.generator import eu_advantage
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table


API_ECU_MARGIN = 0.075


ABLATIONS = [
    {
        "name": "current_rule_replay",
        "label": "Current rule replay",
        "equivalence": "guarded",
        "margin": API_ECU_MARGIN,
        "context_override": True,
        "description": "Guarded equivalence collapse, context override, margin 0.075.",
    },
    {
        "name": "accept_model_equivalence",
        "label": "No equivalence guard",
        "equivalence": "accept_model",
        "margin": API_ECU_MARGIN,
        "context_override": True,
        "description": "Accept every model-declared equivalent-success flag.",
    },
    {
        "name": "never_collapse_equivalence",
        "label": "No equivalence collapse",
        "equivalence": "never",
        "margin": API_ECU_MARGIN,
        "context_override": True,
        "description": "Treat all model candidates as distinct success classes.",
    },
    {
        "name": "no_context_override",
        "label": "No context override",
        "equivalence": "guarded",
        "margin": API_ECU_MARGIN,
        "context_override": False,
        "description": "Use guarded equivalence and margin, but ignore context-resolved flag.",
    },
    {
        "name": "no_margin_or_context",
        "label": "No margin/context dampening",
        "equivalence": "guarded",
        "margin": 0.0,
        "context_override": False,
        "description": "Ask on any positive utility advantage without context override.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/api_eval_100_corrected/ecu_ablation.md")
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def api_equivalence_allowed(episode: dict) -> bool:
    instruction = episode["user_instruction"].lower()
    if any(cue in instruction for cue in [" spare ", " any ", " a spare ", " one of "]):
        return True
    objects = {obj["id"]: obj for obj in episode["scene"]["objects"]}
    candidate_objects = [objects.get(intent["target_id"], {}) for intent in episode["candidate_intents"]]
    return bool(candidate_objects) and all(obj.get("state") == "spare" for obj in candidate_objects)


def normalize_candidates(raw_first: dict, episode: dict, equivalence_mode: str) -> list[dict]:
    candidates = []
    total_probability = 0.0
    for idx, candidate in enumerate(raw_first.get("candidates", [])):
        if not isinstance(candidate, dict):
            continue
        probability = max(float(candidate.get("probability", 0.0) or 0.0), 0.0)
        total_probability += probability
        target_id = str(candidate.get("target_id", ""))
        candidates.append(
            {
                "intent_id": f"api_{idx}",
                "target_id": target_id,
                "action": str(candidate.get("action", "")),
                "prior": probability,
                "success_equivalence_class": target_id,
            }
        )
    if not candidates:
        return []
    if total_probability <= 0.0:
        for candidate in candidates:
            candidate["prior"] = 1.0 / len(candidates)
    else:
        for candidate in candidates:
            candidate["prior"] /= total_probability

    model_says_equivalent = raw_first.get("candidates_equivalent_for_success") is True
    if equivalence_mode == "guarded":
        collapse = model_says_equivalent and api_equivalence_allowed(episode)
    elif equivalence_mode == "accept_model":
        collapse = model_says_equivalent
    elif equivalence_mode == "never":
        collapse = False
    else:
        raise ValueError(f"Unknown equivalence mode: {equivalence_mode}")

    if collapse:
        for candidate in candidates:
            candidate["success_equivalence_class"] = "api_equivalent_success"
    return candidates


def replay_row(api_row: dict, episode: dict, ablation: dict) -> dict:
    raw_first = api_row["debug"]["raw_first"]
    candidates = normalize_candidates(raw_first, episode, ablation["equivalence"])
    if not candidates:
        raise ValueError(f"No candidates for {api_row['episode_id']}")
    advantage = eu_advantage(candidates, episode["ask_cost"], episode["wrong_action_cost"])
    best = max(candidates, key=lambda candidate: candidate["prior"])
    context_resolved_enough = (
        ablation["context_override"]
        and raw_first.get("context_resolves_instruction") is True
        and best["prior"] >= 0.85
        and advantage <= 0.20
    )
    asked = advantage > float(ablation["margin"]) and not context_resolved_enough
    if asked:
        success = True
        final_action = {"type": "ACT", "action": "oracle_after_clarification", "target_id": "hidden_success_class"}
    else:
        final_action = {"type": "ACT", "action": best["action"], "target_id": best["target_id"]}
        success = action_success(episode, final_action)
    return {
        "episode_id": api_row["episode_id"],
        "split": api_row["split"],
        "ambiguity_type": api_row["ambiguity_type"],
        "policy": ablation["name"],
        "asked": asked,
        "success": success,
        "reward": compute_reward(episode, success=success, asked=asked),
        "oracle_should_ask": episode["oracle_should_ask"],
        "advantage": advantage,
        "final_action": final_action,
    }


def bootstrap_ci(values: list[float], samples: int, seed: int) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(samples):
        means.append(mean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    return (means[int(0.025 * samples)], means[int(0.975 * samples)])


def paired_delta(rows: list[dict], baseline: str, policy: str, samples: int, seed: int) -> tuple[float, float, float]:
    by_policy = {
        name: {row["episode_id"]: row["reward"] for row in group}
        for name, group in group_rows(rows, ("policy",)).items()
    }
    baseline_rewards = by_policy[(baseline,)]
    policy_rewards = by_policy[(policy,)]
    shared = sorted(set(baseline_rewards) & set(policy_rewards))
    diffs = [policy_rewards[episode_id] - baseline_rewards[episode_id] for episode_id in shared]
    lo, hi = bootstrap_ci(diffs, samples, seed)
    return (mean(diffs) if diffs else 0.0, lo, hi)


def main_table(rows: list[dict], samples: int, seed: int) -> str:
    table_rows = []
    descriptions = {ablation["name"]: ablation["description"] for ablation in ABLATIONS}
    labels = {ablation["name"]: ablation["label"] for ablation in ABLATIONS}
    for ablation in ABLATIONS:
        policy_rows = [row for row in rows if row["policy"] == ablation["name"]]
        stats = aggregate(policy_rows)
        if ablation["name"] == "current_rule_replay":
            delta_text = "0.000"
        else:
            delta, lo, hi = paired_delta(rows, "current_rule_replay", ablation["name"], samples, seed)
            delta_text = f"{format_float(delta)} [{format_float(lo)}, {format_float(hi)}]"
        table_rows.append(
            [
                labels[ablation["name"]],
                descriptions[ablation["name"]],
                str(stats["n"]),
                format_float(stats["net_utility"]),
                delta_text,
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["missed_clarification_rate"]),
                format_float(stats["unnecessary_clarification_rate"]),
            ]
        )
    return markdown_table(
        [
            "Decision rule",
            "Change",
            "N",
            "Net utility",
            "Delta vs current",
            "Success",
            "Ask rate",
            "Missed clarif.",
            "Unnecessary clarif.",
        ],
        table_rows,
    )


def category_table(rows: list[dict]) -> str:
    keep = {"current_rule_replay", "accept_model_equivalence", "never_collapse_equivalence"}
    table_rows = []
    labels = {ablation["name"]: ablation["label"] for ablation in ABLATIONS}
    grouped = group_rows([row for row in rows if row["policy"] in keep], ("ambiguity_type", "policy"))
    for category, policy in sorted(grouped):
        stats = aggregate(grouped[(category, policy)])
        table_rows.append(
            [
                category,
                labels[policy],
                str(stats["n"]),
                format_float(stats["net_utility"]),
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["missed_clarification_rate"]),
                format_float(stats["unnecessary_clarification_rate"]),
            ]
        )
    return markdown_table(
        ["Category", "Decision rule", "N", "Net utility", "Success", "Ask rate", "Missed clarif.", "Unnecessary clarif."],
        table_rows,
    )


def sanity_check(replayed: list[dict], api_rows: list[dict]) -> str:
    actual = {row["episode_id"]: row for row in api_rows if row["policy"] == "api_ecu"}
    current = [row for row in replayed if row["policy"] == "current_rule_replay"]
    decision_matches = sum(1 for row in current if row["asked"] == actual[row["episode_id"]]["asked"])
    reward_matches = sum(1 for row in current if row["reward"] == actual[row["episode_id"]]["reward"])
    return (
        f"Sanity check: current-rule replay matches actual API ECU ask decisions on "
        f"{decision_matches}/{len(current)} episodes and rewards on {reward_matches}/{len(current)} episodes.\n"
    )


def main() -> None:
    args = parse_args()
    episodes = {episode["episode_id"]: episode for episode in read_jsonl(args.episodes)}
    api_rows = read_jsonl(args.api_results)
    ecu_rows = [row for row in api_rows if row["policy"] == "api_ecu"]
    replayed = []
    for ablation in ABLATIONS:
        for row in ecu_rows:
            replayed.append(replay_row(row, episodes[row["episode_id"]], ablation))

    text = "\n".join(
        [
            "# API ECU Decision Ablations",
            "",
            "This no-API ablation replays the cached GPT-4.1-mini candidate interpretations from the final 100-episode API evaluation. It isolates the first-turn ask/act decision; when an ablated rule asks, the simulator answer is assumed to resolve the hidden intent, matching the benchmark interaction model.",
            "",
            sanity_check(replayed, api_rows),
            "## Main Ablation",
            "",
            main_table(replayed, args.bootstrap_samples, args.seed),
            "## Category Breakdown for Equivalence Ablations",
            "",
            category_table(replayed),
        ]
    )
    write_text(args.out, text)
    print(f"wrote API ECU ablation to {args.out}")


if __name__ == "__main__":
    main()
