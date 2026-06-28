from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


POLICY_ORDER = ["api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"]

FAILURE_LABELS = {
    "guessing_under_referential_ambiguity": "Guessing under referential ambiguity",
    "risk_blindness": "Risk blindness",
    "preference_social_blindness": "Preference/social blindness",
    "equivalence_blindness": "Equivalence blindness",
    "context_overclarification": "Context over-clarification",
    "overclarification": "Over-clarification",
    "bad_post_answer_grounding": "Bad post-answer grounding",
    "bad_direct_grounding": "Bad direct grounding",
    "other_failure": "Other failure",
}

FAILURE_ORDER = [
    "guessing_under_referential_ambiguity",
    "risk_blindness",
    "preference_social_blindness",
    "equivalence_blindness",
    "context_overclarification",
    "overclarification",
    "bad_post_answer_grounding",
    "bad_direct_grounding",
    "other_failure",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/api_eval_100_corrected/failure_taxonomy.md")
    return parser.parse_args()


def read_jsonl_paths(paths: str) -> list[dict]:
    rows: list[dict] = []
    for path in [part.strip() for part in paths.split(",") if part.strip()]:
        rows.extend(read_jsonl(path))
    return rows


def policy_sort_key(policy: str) -> tuple[int, str]:
    try:
        return (POLICY_ORDER.index(policy), policy)
    except ValueError:
        return (999, policy)


def classify_failure(row: dict) -> str | None:
    asked = bool(row["asked"])
    oracle_should_ask = bool(row["oracle_should_ask"])
    success = bool(row["success"])
    category = row["ambiguity_type"]

    if success and asked == oracle_should_ask:
        return None
    if asked and not oracle_should_ask:
        if category == "equivalent_outcome":
            return "equivalence_blindness"
        if category == "context_resolved":
            return "context_overclarification"
        return "overclarification"
    if not asked and oracle_should_ask:
        if category == "risk_sensitive":
            return "risk_blindness"
        if category == "preference_social":
            return "preference_social_blindness"
        if category == "referential":
            return "guessing_under_referential_ambiguity"
        return "other_failure"
    if asked and oracle_should_ask and not success:
        return "bad_post_answer_grounding"
    if not asked and not oracle_should_ask and not success:
        return "bad_direct_grounding"
    return "other_failure"


def event_rows(rows: list[dict]) -> list[dict]:
    events = []
    for row in rows:
        failure_type = classify_failure(row)
        if failure_type is None:
            continue
        new_row = dict(row)
        new_row["failure_type"] = failure_type
        events.append(new_row)
    return events


def summary_table(rows: list[dict], events: list[dict]) -> str:
    total_by_policy = Counter(row["policy"] for row in rows)
    failure_by_policy = Counter(row["policy"] for row in events)
    table_rows = []
    for policy in sorted(total_by_policy, key=policy_sort_key):
        total = total_by_policy[policy]
        failures = failure_by_policy[policy]
        table_rows.append([policy, str(total), str(failures), format_float(failures / total if total else 0.0)])
    return markdown_table(["Method", "Rows", "Failure events", "Event rate"], table_rows)


def type_table(events: list[dict]) -> str:
    counts = Counter(row["failure_type"] for row in events)
    table_rows = []
    for failure_type in FAILURE_ORDER:
        count = counts.get(failure_type, 0)
        if not count:
            continue
        table_rows.append([FAILURE_LABELS[failure_type], str(count)])
    return markdown_table(["Failure type", "Count"], table_rows)


def policy_type_table(events: list[dict]) -> str:
    policies = sorted({row["policy"] for row in events}, key=policy_sort_key)
    table_rows = []
    grouped = Counter((row["policy"], row["failure_type"]) for row in events)
    for failure_type in FAILURE_ORDER:
        if not any(grouped.get((policy, failure_type), 0) for policy in policies):
            continue
        table_rows.append(
            [FAILURE_LABELS[failure_type]]
            + [str(grouped.get((policy, failure_type), 0)) for policy in policies]
        )
    return markdown_table(["Failure type"] + policies, table_rows)


def category_type_table(events: list[dict]) -> str:
    grouped = Counter((row["ambiguity_type"], row["failure_type"]) for row in events)
    table_rows = []
    for category, failure_type in sorted(grouped, key=lambda item: (item[0], FAILURE_ORDER.index(item[1]) if item[1] in FAILURE_ORDER else 999)):
        table_rows.append([category, FAILURE_LABELS[failure_type], str(grouped[(category, failure_type)])])
    return markdown_table(["Category", "Failure type", "Count"], table_rows)


def compact_action(action: dict) -> str:
    return f"{action.get('action', '')} -> {action.get('target_id', '')}"


def exemplar_sections(events: list[dict], episodes: dict[str, dict]) -> str:
    first_by_type: dict[str, dict] = {}
    for row in events:
        first_by_type.setdefault(row["failure_type"], row)
    parts = []
    for failure_type in FAILURE_ORDER:
        row = first_by_type.get(failure_type)
        if row is None:
            continue
        episode = episodes.get(row["episode_id"], {})
        parts.append(f"### {FAILURE_LABELS[failure_type]}\n\n")
        parts.append(f"- Method / episode: `{row['policy']}` / `{row['episode_id']}`\n")
        parts.append(f"- Category: `{row['ambiguity_type']}` / `{row['variant']}`\n")
        if episode.get("user_instruction"):
            parts.append(f"- Instruction: {episode['user_instruction']}\n")
        parts.append(f"- Asked: {row['asked']} | Oracle should ask: {row['oracle_should_ask']} | Success: {row['success']} | Reward: {row['reward']}\n")
        if row.get("question"):
            parts.append(f"- Question: {row['question']}\n")
        if row.get("answer"):
            parts.append(f"- Answer: {row['answer']}\n")
        parts.append(f"- Final action: `{compact_action(row['final_action'])}`\n\n")
    return "".join(parts)


def takeaway(events: list[dict]) -> str:
    counts = Counter(row["failure_type"] for row in events)
    if not counts:
        return "No failure events under this definition.\n"
    top = counts.most_common(3)
    labels = ", ".join(f"{FAILURE_LABELS[name]} ({count})" for name, count in top)
    return f"Top failure modes: {labels}.\n"


def main() -> None:
    args = parse_args()
    episodes = {episode["episode_id"]: episode for episode in read_jsonl_paths(args.episodes)}
    rows = read_jsonl_paths(args.results)
    events = event_rows(rows)
    text = "\n".join(
        [
            "# Failure Taxonomy",
            "",
            "A failure event is any row where the final action fails or the policy asks when the utility oracle says to act / acts when the utility oracle says to ask. Successful but unnecessary questions and lucky unsafe guesses are therefore counted as failures of ask/act calibration.",
            "",
            "## Takeaway",
            "",
            takeaway(events),
            "## Event Rate by Method",
            "",
            summary_table(rows, events),
            "## Failure Type Counts",
            "",
            type_table(events),
            "## Failure Type by Method",
            "",
            policy_type_table(events),
            "## Failure Type by Category",
            "",
            category_type_table(events),
            "## Exemplars",
            "",
            exemplar_sections(events, episodes),
        ]
    )
    write_text(args.out, text)
    print(f"wrote failure taxonomy to {args.out}")


if __name__ == "__main__":
    main()
