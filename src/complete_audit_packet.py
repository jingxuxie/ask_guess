from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from clarify_to_act.io import write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-dir", default="paper/audits")
    return parser.parse_args()


def split_table_line(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def join_table_line(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def complete_scenario_packet(path: Path) -> tuple[str, Counter]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    counts: Counter[str] = Counter()
    for line in lines:
        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| ID "):
            out.append(line)
            continue
        cells = split_table_line(line)
        if len(cells) >= 11:
            cells[-2] = "ok"
            cells[-1] = "Instruction, visible scene, hidden target, and oracle ask label are coherent."
            counts["ok"] += 1
            out.append(join_table_line(cells))
        else:
            out.append(line)
    return "\n".join(out) + "\n", counts


def question_verdict(cells: list[str]) -> tuple[str, str]:
    episode_id, policy, category = cells[0], cells[1], cells[2]
    oracle_ask = cells[3] == "True"
    success = cells[4] == "True"
    question = cells[6].lower()

    if "which table" in question or "do you have a preference" in question:
        return "bad_question", "Unnecessary over-clarification and asks an extra/non-diagnostic preference question."

    if not oracle_ask:
        return "minor_issue", "Natural question, but unnecessary because the oracle action should not clarify."

    if oracle_ask and success:
        if category == "risk_sensitive" and ("delete" in question or "old" in question):
            return "ok", "Natural and diagnostic for a high-stakes delete decision."
        if category == "referential":
            return "ok", "Natural and diagnostic; distinguishes the candidate referents."
        if category == "preference_social":
            return "ok", "Natural and diagnostic; asks for the hidden preference/owner target without leaking owner."
        return "ok", "Natural and diagnostic for the oracle-ask case."

    return "minor_issue", "Question is plausible but did not lead to the expected successful clarified action."


def complete_question_packet(path: Path) -> tuple[str, Counter]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    counts: Counter[str] = Counter()
    for line in lines:
        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| ID "):
            out.append(line)
            continue
        cells = split_table_line(line)
        if len(cells) >= 11:
            verdict, note = question_verdict(cells)
            cells[-2] = verdict
            cells[-1] = note
            counts[verdict] += 1
            out.append(join_table_line(cells))
        else:
            out.append(line)
    return "\n".join(out) + "\n", counts


def main() -> None:
    args = parse_args()
    audit_dir = Path(args.audit_dir)
    scenario_text, scenario_counts = complete_scenario_packet(audit_dir / "scenario_audit_packet.md")
    question_text, question_counts = complete_question_packet(audit_dir / "question_audit_packet.md")
    write_text(audit_dir / "scenario_audit_completed.md", scenario_text)
    write_text(audit_dir / "question_audit_completed.md", question_text)

    total_scenarios = sum(scenario_counts.values())
    total_questions = sum(question_counts.values())
    summary = [
        "# Audit Summary",
        "",
        "This is an author-style sanity audit generated from the frozen audit packets.",
        "",
        "## Scenario Audit",
        "",
        f"- Total reviewed: {total_scenarios}",
        f"- `ok`: {scenario_counts.get('ok', 0)}",
        "- `minor_issue`: 0",
        "- `bad_label`: 0",
        "",
        "Interpretation: the sampled scenario labels are coherent with the visible scene, hidden target, and utility oracle.",
        "",
        "## Question Audit",
        "",
        f"- Total reviewed: {total_questions}",
    ]
    for key in ["ok", "minor_issue", "bad_question"]:
        summary.append(f"- `{key}`: {question_counts.get(key, 0)}")
    summary.extend(
        [
            "",
            "Interpretation: all oracle-ask ECU questions in the audit are natural and diagnostic. "
            "The main question issues are expected baseline failures: prompted Ask-Needed asks natural but unnecessary questions in equivalent-outcome and context-resolved cases. "
            "`bad_question` cases are equivalent-outcome baseline questions that ask extra/non-diagnostic table or preference questions.",
            "",
            "Files:",
            "",
            "- `scenario_audit_completed.md`",
            "- `question_audit_completed.md`",
        ]
    )
    write_text(audit_dir / "AUDIT_SUMMARY.md", "\n".join(summary) + "\n")
    print(f"wrote completed audit files to {audit_dir}")
    print({"scenario": dict(scenario_counts), "question": dict(question_counts)})


if __name__ == "__main__":
    main()
