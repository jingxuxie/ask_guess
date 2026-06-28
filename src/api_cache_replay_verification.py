from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clarify_to_act.api_client import CachedResponsesClient
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table
from run_api_experiment import run_policy, select_stratified


BEHAVIOR_FIELDS = [
    "episode_id",
    "split",
    "ambiguity_type",
    "variant",
    "policy",
    "model",
    "asked",
    "question",
    "answer",
    "final_action",
    "success",
    "reward",
    "oracle_should_ask",
    "ask_cost",
    "wrong_action_cost",
]

STABLE_DEBUG_FIELDS = [
    "raw_first",
    "raw_second",
    "raw_question",
    "api_candidates",
    "api_advantage",
    "api_ecu_margin",
    "api_context_resolved_enough",
]


@dataclass(frozen=True)
class ReplayConfig:
    name: str
    episodes: str
    canonical_results: str
    cache: str
    model: str
    split: str
    limit_per_category: int
    policies: tuple[str, ...]
    scene_format: str = "json"


REPLAY_CONFIGS = [
    ReplayConfig(
        name="main_100_gpt41mini",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_eval_100_corrected_results.jsonl",
        cache="data/runs/api_cache.jsonl",
        model="gpt-4.1-mini",
        split="test",
        limit_per_category=20,
        policies=("api_direct_act", "api_ask_needed", "api_ecu"),
    ),
    ReplayConfig(
        name="cot_100_gpt41mini",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_eval_100_cot_results.jsonl",
        cache="data/runs/api_cache.jsonl",
        model="gpt-4.1-mini",
        split="test",
        limit_per_category=20,
        policies=("api_ask_needed_cot",),
    ),
    ReplayConfig(
        name="style_50_gpt41mini",
        episodes="data/generated/style_stress_episodes.jsonl",
        canonical_results="data/runs/api_style_stress_50_results.jsonl",
        cache="data/runs/api_cache.jsonl",
        model="gpt-4.1-mini",
        split="style_test",
        limit_per_category=10,
        policies=("api_direct_act", "api_ask_needed", "api_ecu"),
    ),
    ReplayConfig(
        name="second_model_25_gpt41nano",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_second_model_25_results.jsonl",
        cache="data/runs/api_second_model_cache.jsonl",
        model="gpt-4.1-nano",
        split="test",
        limit_per_category=5,
        policies=("api_direct_act", "api_ask_needed", "api_ecu"),
    ),
    ReplayConfig(
        name="current_100_gpt54mini",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_gpt_5_4_mini_test100_results.jsonl",
        cache="data/runs/api_gpt_5_4_mini_cache.jsonl",
        model="gpt-5.4-mini",
        split="test",
        limit_per_category=20,
        policies=("api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"),
    ),
    ReplayConfig(
        name="full_test_400_gpt54mini",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_gpt_5_4_mini_test400_results.jsonl",
        cache="data/runs/api_gpt_5_4_mini_cache.jsonl",
        model="gpt-5.4-mini",
        split="test",
        limit_per_category=80,
        policies=("api_ask_needed", "api_ask_needed_cot", "api_ecu"),
    ),
    ReplayConfig(
        name="current_100_gpt55",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_gpt_5_5_test100_results.jsonl",
        cache="data/runs/api_gpt_5_5_cache.jsonl",
        model="gpt-5.5",
        split="test",
        limit_per_category=20,
        policies=("api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"),
    ),
    ReplayConfig(
        name="full_test_400_gpt55",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_gpt_5_5_test400_results.jsonl",
        cache="data/runs/api_gpt_5_5_cache.jsonl",
        model="gpt-5.5",
        split="test",
        limit_per_category=80,
        policies=("api_ask_needed", "api_ask_needed_cot", "api_ecu"),
    ),
    ReplayConfig(
        name="shuffled_scene_100_gpt54mini",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl",
        cache="data/runs/api_gpt_5_4_mini_scene_cache.jsonl",
        model="gpt-5.4-mini",
        split="test",
        limit_per_category=20,
        policies=("api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"),
        scene_format="shuffled_json",
    ),
    ReplayConfig(
        name="natural_language_scene_100_gpt54mini",
        episodes="data/generated/episodes.jsonl",
        canonical_results="data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl",
        cache="data/runs/api_gpt_5_4_mini_nl_cache.jsonl",
        model="gpt-5.4-mini",
        split="test",
        limit_per_category=20,
        policies=("api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"),
        scene_format="natural_language",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="paper/tables/api_cache_replay_verification.md")
    return parser.parse_args()


def cache_rows(path: str) -> int:
    cache_path = Path(path)
    if not cache_path.exists():
        return 0
    with cache_path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def stable_row(row: dict[str, Any]) -> dict[str, Any]:
    stable = {field: row.get(field) for field in BEHAVIOR_FIELDS}
    debug = row.get("debug", {}) if isinstance(row.get("debug"), dict) else {}
    stable["debug"] = {field: debug[field] for field in STABLE_DEBUG_FIELDS if field in debug}
    return stable


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row["episode_id"]), str(row["policy"]))


def replay_rows(config: ReplayConfig) -> list[dict[str, Any]]:
    episodes = read_jsonl(config.episodes)
    selected = select_stratified(episodes, config.split, config.limit_per_category)
    client = CachedResponsesClient(api_key="", model=config.model, cache_path=config.cache, cache_only=True)
    rows = []
    for episode in selected:
        for policy in config.policies:
            rows.append(run_policy(client, policy, episode, config.scene_format))
    return rows


def compare_rows(canonical: list[dict[str, Any]], replayed: list[dict[str, Any]]) -> list[str]:
    canonical_by_key = {row_key(row): stable_row(row) for row in canonical}
    replayed_by_key = {row_key(row): stable_row(row) for row in replayed}
    mismatches = []
    for key in sorted(set(canonical_by_key) | set(replayed_by_key)):
        if key not in canonical_by_key:
            mismatches.append(f"extra replay row {key}")
            continue
        if key not in replayed_by_key:
            mismatches.append(f"missing replay row {key}")
            continue
        if canonical_by_key[key] != replayed_by_key[key]:
            mismatches.append(f"stable row mismatch {key}")
    return mismatches


def replay_check(config: ReplayConfig) -> dict[str, Any]:
    canonical = read_jsonl(config.canonical_results)
    replayed = replay_rows(config)
    mismatches = compare_rows(canonical, replayed)
    return {
        "config": config,
        "canonical_rows": len(canonical),
        "replay_rows": len(replayed),
        "cache_rows": cache_rows(config.cache),
        "mismatches": mismatches,
        "canonical_stats": {policy: aggregate([row for row in canonical if row["policy"] == policy]) for policy in config.policies},
        "replay_stats": {policy: aggregate([row for row in replayed if row["policy"] == policy]) for policy in config.policies},
    }


def run_checks(configs: list[ReplayConfig] | None = None) -> list[dict[str, Any]]:
    return [replay_check(config) for config in (configs or REPLAY_CONFIGS)]


def summary_table(checks: list[dict[str, Any]]) -> str:
    rows = []
    for check in checks:
        config = check["config"]
        ok = check["canonical_rows"] == check["replay_rows"] and not check["mismatches"]
        rows.append(
            [
                config.name,
                "PASS" if ok else "FAIL",
                str(check["canonical_rows"]),
                str(check["replay_rows"]),
                str(check["cache_rows"]),
                str(len(check["mismatches"])),
                config.cache,
            ]
        )
    return markdown_table(["Replay", "Status", "Canonical rows", "Replay rows", "Cache rows", "Mismatches", "Cache"], rows)


def metric_table(checks: list[dict[str, Any]]) -> str:
    rows = []
    for check in checks:
        config = check["config"]
        for policy in config.policies:
            canonical = check["canonical_stats"][policy]
            replayed = check["replay_stats"][policy]
            rows.append(
                [
                    config.name,
                    policy,
                    format_float(canonical["net_utility"]),
                    format_float(replayed["net_utility"]),
                    format_float(canonical["ask_rate"]),
                    format_float(replayed["ask_rate"]),
                    format_float(canonical["success"]),
                    format_float(replayed["success"]),
                ]
            )
    return markdown_table(
        ["Replay", "Policy", "Canonical utility", "Replay utility", "Canonical ask", "Replay ask", "Canonical success", "Replay success"],
        rows,
    )


def mismatch_table(checks: list[dict[str, Any]]) -> str:
    rows = []
    for check in checks:
        config = check["config"]
        for mismatch in check["mismatches"][:20]:
            rows.append([config.name, mismatch])
    return markdown_table(["Replay", "Mismatch"], rows or [["none", "none"]])


def main() -> None:
    args = parse_args()
    checks = run_checks()
    ok = all(check["canonical_rows"] == check["replay_rows"] and not check["mismatches"] for check in checks)
    text = "\n".join(
        [
            "# API Cache-Only Replay Verification",
            "",
            "This generated report replays each canonical API evidence set through `run_api_experiment.py` with `CachedResponsesClient(cache_only=True)`. It does not read an API key and fails on cache miss. Rows are compared on stable behavioral fields plus stable ECU debug fields; response IDs, timestamps, and usage metadata are intentionally ignored.",
            "",
            "## Summary",
            "",
            summary_table(checks),
            "## Metric Equality Check",
            "",
            metric_table(checks),
            "## Mismatches",
            "",
            mismatch_table(checks),
            "## Interpretation",
            "",
            "- PASS means the shipped API caches reproduce the canonical API result rows without network calls.",
            "- This is a reproducibility check, not a new model evaluation.",
            "",
            f"Overall status: **{'PASS' if ok else 'FAIL'}**",
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote API cache replay verification to {args.out}")
    print(f"overall status: {'PASS' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
