from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clarify_to_act.environment import hidden_intent, simulated_user_answer
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table
from clarify_to_act.policies import diagnostic_question
from run_api_experiment import visible_scene


DEFAULT_EPISODES = ",".join(
    [
        "data/generated/episodes.jsonl",
        "data/generated/style_stress_episodes.jsonl",
        "data/generated/ambiguity_mix_shift_episodes.jsonl",
    ]
)
DEFAULT_API_RESULTS = ",".join(
    [
        "data/runs/api_eval_100_corrected_results.jsonl",
        "data/runs/api_eval_100_cot_results.jsonl",
        "data/runs/api_style_stress_50_results.jsonl",
        "data/runs/api_second_model_25_results.jsonl",
    ]
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default=DEFAULT_EPISODES)
    parser.add_argument("--api-results", default=DEFAULT_API_RESULTS)
    parser.add_argument("--out", default="paper/tables/simulated_user_audit.md")
    return parser.parse_args()


def read_jsonl_paths(paths: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in [part.strip() for part in paths.split(",") if part.strip()]:
        for row in read_jsonl(path):
            item = dict(row)
            item["_source_path"] = path
            rows.append(item)
    return rows


def normalize_text(value: object) -> str:
    return str(value or "").replace("_", " ").lower()


def visible_objects_by_id(episode: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scene = visible_scene(episode)
    return {obj["id"]: obj for obj in scene["objects"]}


def score_visible_object(obj: dict[str, Any], answer: str) -> int:
    answer_text = normalize_text(answer)
    score = 0
    for key in ("state", "location", "owner", "color", "type"):
        value = normalize_text(obj.get(key, ""))
        if not value or value == "unknown":
            continue
        if value in answer_text:
            score += 1
    return score


def answer_resolution(episode: dict[str, Any], answer: str) -> dict[str, Any]:
    hidden_class = hidden_intent(episode)["success_equivalence_class"]
    objects = visible_objects_by_id(episode)
    scored = []
    for intent in episode["candidate_intents"]:
        obj = objects[intent["target_id"]]
        scored.append((score_visible_object(obj, answer), intent["success_equivalence_class"], intent["target_id"]))
    scored.sort(key=lambda item: item[0], reverse=True)
    top_score = scored[0][0] if scored else 0
    top_classes = {success_class for score, success_class, _ in scored if score == top_score}
    top_targets = [target_id for score, _, target_id in scored if score == top_score]
    resolves = top_score > 0 and top_classes == {hidden_class}
    return {
        "resolves": resolves,
        "top_score": top_score,
        "top_classes": sorted(top_classes),
        "top_targets": top_targets,
        "hidden_class": hidden_class,
    }


def generated_audit_rows(episodes: list[dict[str, Any]]) -> tuple[list[list[str]], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    failures = []
    for episode in episodes:
        if not episode["oracle_should_ask"]:
            continue
        question = diagnostic_question(episode)
        answer = simulated_user_answer(episode, question)
        resolution = answer_resolution(episode, answer)
        row = {
            "source": episode["_source_path"],
            "category": episode["ambiguity_type"],
            "episode_id": episode["episode_id"],
            "question": question,
            "answer": answer,
            "resolves": resolution["resolves"],
            "top_score": resolution["top_score"],
            "top_targets": resolution["top_targets"],
            "hidden_class": resolution["hidden_class"],
        }
        groups[(episode["_source_path"], episode["ambiguity_type"])].append(row)
        if not resolution["resolves"]:
            failures.append(row)

    table_rows = []
    for (source, category), rows in sorted(groups.items()):
        resolves = sum(1 for row in rows if row["resolves"])
        table_rows.append([source, category, str(len(rows)), str(resolves), format_float(resolves / len(rows))])
    return table_rows, failures


def api_audit_rows(api_rows: list[dict[str, Any]], episodes_by_id: dict[str, dict[str, Any]]) -> tuple[list[list[str]], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    failures = []
    for row in api_rows:
        if not row.get("asked"):
            continue
        episode = episodes_by_id[row["episode_id"]]
        answer = str(row.get("answer") or "")
        resolution = answer_resolution(episode, answer)
        item = {
            "source": row["_source_path"],
            "policy": row["policy"],
            "episode_id": row["episode_id"],
            "category": row["ambiguity_type"],
            "question": row.get("question"),
            "answer": answer,
            "resolves": resolution["resolves"],
            "top_score": resolution["top_score"],
            "top_targets": resolution["top_targets"],
            "hidden_class": resolution["hidden_class"],
        }
        groups[(row["_source_path"], row["policy"])].append(item)
        if not resolution["resolves"]:
            failures.append(item)

    table_rows = []
    for (source, policy), rows in sorted(groups.items()):
        resolves = sum(1 for row in rows if row["resolves"])
        table_rows.append([source, policy, str(len(rows)), str(resolves), format_float(resolves / len(rows))])
    return table_rows, failures


def summary_rows(generated_rows: list[list[str]], api_rows: list[list[str]]) -> list[list[str]]:
    generated_total = sum(int(row[2]) for row in generated_rows)
    generated_resolved = sum(int(row[3]) for row in generated_rows)
    api_total = sum(int(row[2]) for row in api_rows)
    api_resolved = sum(int(row[3]) for row in api_rows)
    return [
        [
            "Generated oracle-ask diagnostic answers",
            str(generated_total),
            str(generated_resolved),
            format_float(generated_resolved / generated_total if generated_total else 0.0),
        ],
        [
            "Actual API asked-row answers",
            str(api_total),
            str(api_resolved),
            format_float(api_resolved / api_total if api_total else 0.0),
        ],
    ]


def failure_table(failures: list[dict[str, Any]]) -> str:
    rows = []
    for failure in failures[:20]:
        rows.append(
            [
                failure["source"],
                failure.get("policy", "generated"),
                failure["episode_id"],
                failure.get("category", ""),
                str(failure.get("question", ""))[:80],
                str(failure.get("answer", ""))[:80],
                str(failure.get("top_targets", []))[:80],
            ]
        )
    return markdown_table(["Source", "Policy", "Episode", "Category", "Question", "Answer", "Top visible targets"], rows or [["none", "none", "none", "none", "none", "none", "none"]])


def main() -> None:
    args = parse_args()
    episodes = read_jsonl_paths(args.episodes)
    episodes_by_id = {episode["episode_id"]: episode for episode in episodes}
    api_rows = read_jsonl_paths(args.api_results)

    generated_rows, generated_failures = generated_audit_rows(episodes)
    api_rows_table, api_failures = api_audit_rows(api_rows, episodes_by_id)
    all_failures = generated_failures + api_failures
    status_ok = not all_failures

    text = "\n".join(
        [
            "# Simulated User Answer Audit",
            "",
            "This generated audit checks whether deterministic simulated-user answers are visibly diagnostic. For each oracle-ask generated episode, it asks the policy diagnostic question and verifies that the returned answer identifies the hidden success class using only fields visible to the model. For each actual API row where a policy asked a question, it verifies the stored answer the model received in the same way.",
            "",
            "## Summary",
            "",
            markdown_table(["Check", "N", "Resolved", "Resolution rate"], summary_rows(generated_rows, api_rows_table)),
            "## Generated Oracle-Ask Diagnostic Answers",
            "",
            markdown_table(["Source", "Category", "Oracle-ask N", "Resolved", "Resolution rate"], generated_rows),
            "## Actual API Asked-Row Answers",
            "",
            markdown_table(["Source", "Policy", "Asked N", "Resolved", "Resolution rate"], api_rows_table),
            "## Failures",
            "",
            failure_table(all_failures),
            "## Interpretation",
            "",
            "- PASS means the deterministic answer strings identify the hidden success class from visible scene fields in this audit.",
            "- This supports the reproducibility and diagnostic clarity of the simulated user, but it is not a human-response study.",
            "",
            f"Overall status: **{'PASS' if status_ok else 'FAIL'}**",
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote simulated user answer audit to {args.out}")
    print(f"overall status: {'PASS' if status_ok else 'FAIL'}")
    if not status_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
