from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from clarify_to_act.api_client import stable_hash, supports_temperature, uses_reasoning_budget
from clarify_to_act.environment import simulated_user_answer
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table
from run_api_experiment import (
    api_equivalence_allowed,
    candidate_to_action,
    prompt_text,
    scene_text,
    select_stratified,
)
from clarify_to_act.generator import eu_advantage


DEFAULT_RUNS = [
    (
        "gpt-5.4-mini",
        "data/runs/api_gpt_5_4_mini_test100_results.jsonl",
        "data/runs/api_gpt_5_4_mini_cache.jsonl",
    ),
    (
        "gpt-5.5",
        "data/runs/api_gpt_5_5_test100_results.jsonl",
        "data/runs/api_gpt_5_5_cache.jsonl",
    ),
]

TARGET_POLICIES = ["api_ask_needed", "api_ask_needed_cot", "api_ecu"]
POLICY_PROMPTS = {
    "api_ask_needed": ("ask_when_needed.txt", 200),
    "api_ask_needed_cot": ("ask_when_needed_cot.txt", 240),
    "api_ecu": ("candidate_interpretations.txt", 420),
}
STANDARD_PRICES_PER_MTOK = {
    "gpt-5.4-mini": (0.75, 4.50),
    "gpt-5.5": (5.00, 30.00),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--split", default="test")
    parser.add_argument("--limit-per-category", type=int, default=80)
    parser.add_argument("--scene-format", default="json", choices=["json", "shuffled_json", "natural_language"])
    parser.add_argument("--out", default="paper/tables/full_test_expansion_feasibility.md")
    parser.add_argument(
        "--run",
        action="append",
        help="Run spec formatted as model=result_path:cache_path. Defaults to GPT-5.4-mini and GPT-5.5 current-model caches.",
    )
    return parser.parse_args()


def parse_run(spec: str) -> tuple[str, str, str]:
    model, sep, rest = spec.partition("=")
    result_path, sep2, cache_path = rest.partition(":")
    if not model.strip() or not sep or not result_path.strip() or not sep2 or not cache_path.strip():
        raise ValueError(f"Invalid --run {spec!r}; expected model=result_path:cache_path")
    return model.strip(), result_path.strip(), cache_path.strip()


def cache_key_for(model: str, prompt: str, max_output_tokens: int) -> str:
    effective_max_output_tokens = max_output_tokens
    if uses_reasoning_budget(model):
        effective_max_output_tokens = max(max_output_tokens, 512)
    body = {
        "model": model,
        "input": prompt,
        "max_output_tokens": effective_max_output_tokens,
        "store": False,
        "text": {"format": {"type": "json_object"}},
    }
    if supports_temperature(model):
        body["temperature"] = 0
    if uses_reasoning_budget(model):
        body["reasoning"] = {"effort": "none"}
    return stable_hash(body)


def read_cache(path: str) -> dict[str, dict]:
    rows = {}
    cache_path = Path(path)
    if not cache_path.exists():
        return rows
    with cache_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                rows[row["cache_key"]] = row
    return rows


def default_full_result_path(model: str) -> Path:
    safe_model = model.replace(".", "_").replace("-", "_")
    return Path(f"data/runs/api_{safe_model}_test400_results.jsonl")


def first_prompt(policy: str, episode: dict, scene_format: str) -> tuple[str, int]:
    prompt_name, max_tokens = POLICY_PROMPTS[policy]
    prompt = prompt_text(prompt_name, scene_json=scene_text(episode, scene_format), instruction=episode["user_instruction"])
    return prompt, max_tokens


def clean_api_candidates(parsed: dict, episode: dict) -> tuple[list[dict], float, bool]:
    candidates = parsed.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        return [], 0.0, False
    cleaned = []
    total_probability = 0.0
    for idx, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            continue
        probability = max(float(candidate.get("probability", 0.0) or 0.0), 0.0)
        total_probability += probability
        cleaned.append(
            {
                "intent_id": f"api_{idx}",
                "target_id": str(candidate.get("target_id", "")),
                "action": str(candidate.get("action", "")),
                "prior": probability,
                "success_equivalence_class": str(candidate.get("target_id", "")),
            }
        )
    if not cleaned:
        return [], 0.0, False
    if total_probability <= 0:
        for candidate in cleaned:
            candidate["prior"] = 1.0 / len(cleaned)
    else:
        for candidate in cleaned:
            candidate["prior"] = candidate["prior"] / total_probability
    if parsed.get("candidates_equivalent_for_success") is True and api_equivalence_allowed(episode):
        for candidate in cleaned:
            candidate["success_equivalence_class"] = "api_equivalent_success"
    advantage = eu_advantage(cleaned, episode["ask_cost"], episode["wrong_action_cost"])
    best = max(cleaned, key=lambda candidate: candidate["prior"])
    context_resolved = parsed.get("context_resolves_instruction") is True
    context_resolved_enough = context_resolved and best["prior"] >= 0.85 and advantage <= 0.20
    should_ask = advantage > 0.075 and not context_resolved_enough
    return cleaned, advantage, should_ask


def downstream_keys_for_cached_first(
    model: str,
    policy: str,
    episode: dict,
    scene_format: str,
    first_row: dict,
    cache: dict[str, dict],
) -> list[tuple[str, str, bool]]:
    parsed = first_row.get("parsed") or {}
    downstream = []
    if policy in {"api_ask_needed", "api_ask_needed_cot"}:
        if parsed.get("type") != "ASK":
            return downstream
        question = str(parsed.get("question", ""))
    else:
        candidates, _, should_ask = clean_api_candidates(parsed, episode)
        if not should_ask:
            return downstream
        question_prompt = prompt_text(
            "generate_question.txt",
            scene_json=scene_text(episode, scene_format),
            instruction=episode["user_instruction"],
            candidate_json=json.dumps(candidates, sort_keys=True),
        )
        question_key = cache_key_for(model, question_prompt, 120)
        downstream.append(("api_ecu_question", question_key, question_key in cache))
        question_row = cache.get(question_key)
        question = str((question_row.get("parsed") or {}).get("question", "")) if question_row else ""
        if not question:
            return downstream

    answer = simulated_user_answer(episode, question)
    second_prompt = prompt_text(
        "act_after_answer.txt",
        scene_json=scene_text(episode, scene_format),
        instruction=episode["user_instruction"],
        question=question,
        answer=answer,
    )
    second_key = cache_key_for(model, second_prompt, 160)
    downstream.append(("act_after_answer", second_key, second_key in cache))
    return downstream


def response_usage(rows: list[dict]) -> Counter[str]:
    seen = set()
    totals: Counter[str] = Counter()
    for row in rows:
        debug = row.get("debug") or {}
        for key in ("api", "api_second", "api_question"):
            meta = debug.get(key)
            if not isinstance(meta, dict):
                continue
            response_id = meta.get("response_id") or meta.get("cache_key")
            if not response_id or response_id in seen:
                continue
            seen.add(str(response_id))
            usage = meta.get("usage") or {}
            output_details = usage.get("output_tokens_details") or {}
            totals["responses"] += 1
            totals["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            totals["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
            totals["reasoning_tokens"] += int(output_details.get("reasoning_tokens", 0) or 0)
    return totals


def projected_usage_by_category(current_rows: list[dict], target_episodes: list[dict]) -> Counter[str]:
    target_counts = Counter(episode["ambiguity_type"] for episode in target_episodes)
    observed_episode_counts: Counter[str] = Counter()
    for category, rows in group_episode_rows(current_rows).items():
        observed_episode_counts[category] = len({row["episode_id"] for row in rows})

    projected: Counter[str] = Counter()
    rows_by_category: dict[str, list[dict]] = defaultdict(list)
    for row in current_rows:
        rows_by_category[row["ambiguity_type"]].append(row)
    for category, rows in rows_by_category.items():
        observed_count = observed_episode_counts.get(category, 0)
        if not observed_count:
            continue
        scale = target_counts[category] / observed_count
        usage = response_usage(rows)
        for key, value in usage.items():
            projected[key] += value * scale
    return projected


def group_episode_rows(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["ambiguity_type"]].append(row)
    return grouped


def dollars(tokens: Counter[str], model: str) -> str:
    if model not in STANDARD_PRICES_PER_MTOK:
        return "-"
    input_price, output_price = STANDARD_PRICES_PER_MTOK[model]
    cost = tokens["input_tokens"] / 1_000_000 * input_price + tokens["output_tokens"] / 1_000_000 * output_price
    return f"${cost:.2f}"


def int_counter_delta(a: Counter[str], b: Counter[str]) -> Counter[str]:
    out: Counter[str] = Counter()
    for key in set(a) | set(b):
        out[key] = int(round(a[key] - b[key]))
    return out


def analyze_run(model: str, result_path: str, cache_path: str, target_episodes: list[dict], scene_format: str) -> dict:
    baseline_rows_all = read_jsonl(result_path) if Path(result_path).exists() else []
    baseline_rows = [
        row
        for row in baseline_rows_all
        if row["policy"] in TARGET_POLICIES and row.get("scene_format", "json") == scene_format
    ]
    full_result_path = default_full_result_path(model)
    coverage_path = full_result_path if full_result_path.exists() else Path(result_path)
    coverage_rows_all = read_jsonl(coverage_path.as_posix()) if coverage_path.exists() else []
    coverage_rows = [
        row
        for row in coverage_rows_all
        if row["policy"] in TARGET_POLICIES and row.get("scene_format", "json") == scene_format
    ]
    target_ids = {episode["episode_id"] for episode in target_episodes}
    existing_result_rows = [
        row for row in coverage_rows if row["episode_id"] in target_ids and row["policy"] in TARGET_POLICIES
    ]

    cache = read_cache(cache_path)
    first_counts: Counter[str] = Counter()
    downstream_counts: Counter[str] = Counter()
    for episode in target_episodes:
        for policy in TARGET_POLICIES:
            prompt, max_tokens = first_prompt(policy, episode, scene_format)
            key = cache_key_for(model, prompt, max_tokens)
            first_counts["target_first_calls"] += 1
            if key in cache:
                first_counts["cached_first_calls"] += 1
                for family, _, cached in downstream_keys_for_cached_first(model, policy, episode, scene_format, cache[key], cache):
                    downstream_counts[f"{family}_known_calls"] += 1
                    if cached:
                        downstream_counts[f"{family}_cached_calls"] += 1
            else:
                first_counts["first_call_misses"] += 1

    baseline_usage = response_usage(baseline_rows)
    full_coverage_available = len(existing_result_rows) == len(target_episodes) * len(TARGET_POLICIES)
    if full_coverage_available:
        projected_total_usage = response_usage(existing_result_rows)
        projected_incremental_usage = Counter({key: 0 for key in projected_total_usage})
    else:
        projected_total_usage = projected_usage_by_category(baseline_rows, target_episodes)
        projected_incremental_usage = int_counter_delta(projected_total_usage, baseline_usage)
    stats = {policy: aggregate([row for row in baseline_rows if row["policy"] == policy]) for policy in TARGET_POLICIES}
    return {
        "model": model,
        "result_path": result_path,
        "coverage_path": coverage_path.as_posix(),
        "cache_path": cache_path,
        "baseline_rows": baseline_rows,
        "coverage_rows": existing_result_rows,
        "target_rows": len(target_episodes) * len(TARGET_POLICIES),
        "existing_result_rows": len(existing_result_rows),
        "new_result_rows": len(target_episodes) * len(TARGET_POLICIES) - len(existing_result_rows),
        "first_counts": first_counts,
        "downstream_counts": downstream_counts,
        "observed_usage": baseline_usage,
        "projected_total_usage": projected_total_usage,
        "projected_incremental_usage": projected_incremental_usage,
        "stats": stats,
    }


def target_summary(target_episodes: list[dict]) -> str:
    rows = []
    by_category = Counter(episode["ambiguity_type"] for episode in target_episodes)
    for category, count in sorted(by_category.items()):
        oracle_ask = sum(1 for episode in target_episodes if episode["ambiguity_type"] == category and episode["oracle_should_ask"])
        rows.append([category, str(count), format_float(oracle_ask / count if count else 0.0)])
    return markdown_table(["Category", "Target episodes", "Oracle ask rate"], rows)


def cache_table(analyses: list[dict]) -> str:
    rows = []
    for analysis in analyses:
        first = analysis["first_counts"]
        downstream = analysis["downstream_counts"]
        rows.append(
            [
                analysis["model"],
                analysis["coverage_path"],
                str(analysis["target_rows"]),
                str(analysis["existing_result_rows"]),
                str(analysis["new_result_rows"]),
                str(first["target_first_calls"]),
                str(first["cached_first_calls"]),
                str(first["first_call_misses"]),
                str(downstream["api_ecu_question_known_calls"]),
                str(downstream["api_ecu_question_cached_calls"]),
                str(downstream["act_after_answer_known_calls"]),
                str(downstream["act_after_answer_cached_calls"]),
            ]
        )
    return markdown_table(
        [
            "Model",
            "Coverage result path",
            "Target rows",
            "Existing rows",
            "New rows",
            "First calls",
            "Cached first",
            "First misses",
            "Known ECU question calls",
            "Cached ECU question",
            "Known second-turn calls",
            "Cached second-turn",
        ],
        rows,
    )


def usage_table(analyses: list[dict]) -> str:
    rows = []
    for analysis in analyses:
        observed = analysis["observed_usage"]
        projected = analysis["projected_total_usage"]
        incremental = analysis["projected_incremental_usage"]
        rows.append(
            [
                analysis["model"],
                str(int(observed["responses"])),
                str(int(observed["input_tokens"])),
                str(int(observed["output_tokens"])),
                str(int(projected["responses"])),
                str(int(projected["input_tokens"])),
                str(int(projected["output_tokens"])),
                str(int(incremental["responses"])),
                str(int(incremental["input_tokens"])),
                str(int(incremental["output_tokens"])),
                dollars(incremental, analysis["model"]),
            ]
        )
    return markdown_table(
        [
            "Model",
            "Observed 100 responses",
            "Observed input",
            "Observed output",
            "Projected 400 responses",
            "Projected input",
            "Projected output",
            "Incremental responses",
            "Incremental input",
            "Incremental output",
            "Est. incremental cost",
        ],
        rows,
    )


def current_metric_table(analyses: list[dict]) -> str:
    rows = []
    for analysis in analyses:
        for policy in TARGET_POLICIES:
            stats = analysis["stats"][policy]
            rows.append(
                [
                    analysis["model"],
                    policy,
                    str(stats["n"]),
                    format_float(stats["net_utility"]),
                    format_float(stats["ask_rate"]),
                    format_float(stats["missed_clarification_rate"]),
                    format_float(stats["unnecessary_clarification_rate"]),
                ]
            )
    return markdown_table(
        ["Model", "Policy", "Observed N", "Utility", "Ask rate", "Missed", "Unnecessary"],
        rows,
    )


def recommendation(analyses: list[dict]) -> str:
    total_cost = sum(
        (
            analysis["projected_incremental_usage"]["input_tokens"] / 1_000_000 * STANDARD_PRICES_PER_MTOK[analysis["model"]][0]
            + analysis["projected_incremental_usage"]["output_tokens"] / 1_000_000 * STANDARD_PRICES_PER_MTOK[analysis["model"]][1]
        )
        for analysis in analyses
        if analysis["model"] in STANDARD_PRICES_PER_MTOK
    )
    remaining = [analysis["model"] for analysis in analyses if analysis["new_result_rows"] > 0]
    next_step = (
        f"Run {remaining[0]} next with `api_ask_needed,api_ask_needed_cot,api_ecu` if the remaining budget allows."
        if remaining
        else "No remaining full-test API rows are needed for the configured runs."
    )
    return "\n".join(
        [
            f"- Estimated remaining standard-price cost for configured full 400-episode runs: ${total_cost:.2f}.",
            "- For runs without full-test coverage, this estimate extrapolates from the already cached 100-episode current-model rows with the same balanced category mix.",
            f"- {next_step}",
            "- Use cache files already listed here and keep `api_ask_needed,api_ask_needed_cot,api_ecu` as the target policy set.",
            "- No API calls are made by this feasibility script.",
        ]
    )


def main() -> None:
    args = parse_args()
    run_specs = [parse_run(spec) for spec in args.run] if args.run else DEFAULT_RUNS
    episodes = read_jsonl(args.episodes)
    target_episodes = select_stratified(episodes, args.split, args.limit_per_category)
    analyses = [analyze_run(model, result_path, cache_path, target_episodes, args.scene_format) for model, result_path, cache_path in run_specs]
    text = "\n".join(
        [
            "# Full-Test Current-Model Expansion Feasibility",
            "",
            "This no-API report sizes the Priority 2 full 400-episode current-model expansion before spending budget.",
            "",
            "## Target",
            "",
            f"- Split: `{args.split}`",
            f"- Limit per category: `{args.limit_per_category}`",
            f"- Scene format: `{args.scene_format}`",
            f"- Policies: `{', '.join(TARGET_POLICIES)}`",
            f"- Total target episodes: {len(target_episodes)}",
            "",
            target_summary(target_episodes),
            "## Existing Coverage and Exact Cache Hits",
            "",
            cache_table(analyses),
            "## Observed 100-Episode Metrics for Target Policies",
            "",
            current_metric_table(analyses),
            "## Token and Cost Projection",
            "",
            "For completed full-test runs, usage is measured from the full result file and remaining cost is zero. For incomplete runs, projected usage scales the observed 100-episode target-policy usage within each category to 80 episodes per category. Cost uses standard short-context OpenAI API prices per 1M tokens as checked on 2026-06-28: GPT-5.5 input/output $5.00/$30.00; GPT-5.4-mini input/output $0.75/$4.50. Verify prices again immediately before a paid run.",
            "",
            usage_table(analyses),
            "## Recommendation",
            "",
            recommendation(analyses),
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote full-test expansion feasibility report to {args.out}")


if __name__ == "__main__":
    main()
