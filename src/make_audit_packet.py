from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from clarify_to_act.io import read_jsonl, write_text


CATEGORY_ORDER = [
    "context_resolved",
    "preference_social",
    "equivalent_outcome",
    "referential",
    "risk_sensitive",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument(
        "--api-results",
        default="data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl,data/runs/api_style_stress_50_results.jsonl",
        help="Comma-separated JSONL result files used for the question audit.",
    )
    parser.add_argument("--out-dir", default="paper/audits")
    parser.add_argument("--scenarios-per-category", type=int, default=20)
    parser.add_argument("--questions", type=int, default=100)
    return parser.parse_args()


def read_result_paths(paths: str) -> list[dict]:
    rows: list[dict] = []
    for path in [part.strip() for part in paths.split(",") if part.strip()]:
        rows.extend(read_jsonl(path))
    return rows


def compact_scene(episode: dict) -> str:
    objects = []
    for obj in episode["scene"]["objects"]:
        owner = obj["owner"] if obj.get("visible_owner", True) else "unknown"
        objects.append(
            f"{obj['id']}={obj['color']} {obj['type']}, state={obj['state']}, "
            f"loc={obj['location']}, owner={owner}, sal={obj['salience']}"
        )
    current_user = episode["scene"].get("current_user")
    prefix = f"current_user={current_user}; " if current_user else ""
    return prefix + "; ".join(objects)


def hidden_target(episode: dict) -> str:
    intents = {intent["intent_id"]: intent for intent in episode["candidate_intents"]}
    return intents[episode["hidden_intent_id"]]["target_id"]


def scenario_audit(episodes: list[dict], per_category: int) -> tuple[str, int]:
    selected = []
    counts = defaultdict(int)
    for episode in episodes:
        if episode["split"] != "test":
            continue
        category = episode["ambiguity_type"]
        if category not in CATEGORY_ORDER:
            continue
        if counts[category] >= per_category:
            continue
        selected.append(episode)
        counts[category] += 1
    selected.sort(key=lambda ep: (CATEGORY_ORDER.index(ep["ambiguity_type"]), ep["episode_id"]))

    rows = [
        "# Scenario Audit Packet",
        "",
        "Reviewer task: mark whether the instruction, visible scene, hidden intent, and oracle ask label look sane.",
        "",
        "| ID | Category | Variant | Instruction | Visible scene | Hidden target | Oracle ask | Ask cost | Wrong cost | Verdict | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for ep in selected:
        rows.append(
            "| "
            + " | ".join(
                [
                    ep["episode_id"],
                    ep["ambiguity_type"],
                    ep["variant"],
                    ep["user_instruction"],
                    compact_scene(ep),
                    hidden_target(ep),
                    str(ep["oracle_should_ask"]),
                    f"{ep['ask_cost']:.2f}",
                    f"{ep['wrong_action_cost']:.2f}",
                    "",
                    "",
                ]
            )
            + " |"
        )
    rows.append("")
    return "\n".join(rows), len(selected)


def question_audit(api_rows: list[dict], limit: int) -> tuple[str, int]:
    asked = [row for row in api_rows if row.get("asked") and row.get("question")]
    asked.sort(key=lambda row: (row["policy"], row["split"], row["ambiguity_type"], row["episode_id"]))
    # Round-robin across method/category groups so the larger prompted-baseline
    # groups do not crowd out ECU or CoT questions.
    selected: list[dict] = []
    groups: dict[tuple[str, str], list[dict]] = {}
    for policy in ["api_ask_needed", "api_ask_needed_cot", "api_ecu"]:
        for category in CATEGORY_ORDER:
            group = [row for row in asked if row["policy"] == policy and row["ambiguity_type"] == category]
            if group:
                groups[(policy, category)] = group
    group_order = list(groups)
    index_by_group = {key: 0 for key in group_order}
    while len(selected) < limit:
        added = False
        for key in group_order:
            idx = index_by_group[key]
            group = groups[key]
            if idx >= len(group):
                continue
            selected.append(group[idx])
            index_by_group[key] += 1
            added = True
            if len(selected) >= limit:
                break
        if not added:
            break

    rows = [
        "# Clarifying Question Audit Packet",
        "",
        "Reviewer task: mark whether the question is natural, concise, and diagnostic for the candidate ambiguity.",
        "",
        "| ID | Policy | Category | Oracle ask | Success | Reward | Question | Simulated answer | Final action | Verdict | Notes |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in selected[:limit]:
        rows.append(
            "| "
            + " | ".join(
                [
                    row["episode_id"],
                    row["policy"],
                    row["ambiguity_type"],
                    str(row["oracle_should_ask"]),
                    str(row["success"]),
                    f"{row['reward']:.2f}",
                    row.get("question") or "",
                    row.get("answer") or "",
                    json.dumps(row.get("final_action", {}), sort_keys=True),
                    "",
                    "",
                ]
            )
            + " |"
        )
    rows.append("")
    return "\n".join(rows), min(len(selected), limit)


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    api_rows = read_result_paths(args.api_results)
    out_dir = Path(args.out_dir)
    scenario_text, scenario_count = scenario_audit(episodes, args.scenarios_per_category)
    question_text, question_count = question_audit(api_rows, args.questions)
    write_text(out_dir / "scenario_audit_packet.md", scenario_text)
    write_text(out_dir / "question_audit_packet.md", question_text)
    index = f"""# Audit Packet Index

Generated from:

- episodes: `{args.episodes}`
- API results: `{args.api_results}`

Files:

- `scenario_audit_packet.md`: {scenario_count} stratified test scenarios.
- `question_audit_packet.md`: {question_count} clarification questions sampled from API policies.

Fill the `Verdict` and `Notes` columns during author review. Suggested verdicts: `ok`, `minor_issue`, `bad_label`, `bad_question`, `unclear`.
"""
    write_text(out_dir / "AUDIT_INDEX.md", index)
    print(f"wrote audit packet to {out_dir}")


if __name__ == "__main__":
    main()
