from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from clarify_to_act.io import write_text
from clarify_to_act.metrics import format_float, markdown_table


SOURCE_URL = "https://raw.githubusercontent.com/zt991211/CLAMBER/main/clamber_benchmark.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/external/clamber_benchmark.jsonl")
    parser.add_argument("--out", default="paper/tables/clamber_external_sanity.md")
    parser.add_argument("--ask-cost", type=float, default=0.05)
    parser.add_argument("--miss-cost", type=float, default=1.0)
    return parser.parse_args()


def read_clamber(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if isinstance(row, str):
                row = json.loads(row)
            rows.append(row)
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def confusion(rows: list[dict]) -> dict[str, float]:
    tp = sum(int(row["require_clarification"]) == 1 and int(row["predict_ambiguous"]) == 1 for row in rows)
    fn = sum(int(row["require_clarification"]) == 1 and int(row["predict_ambiguous"]) == 0 for row in rows)
    fp = sum(int(row["require_clarification"]) == 0 and int(row["predict_ambiguous"]) == 1 for row in rows)
    tn = sum(int(row["require_clarification"]) == 0 and int(row["predict_ambiguous"]) == 0 for row in rows)
    n = len(rows)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {
        "n": n,
        "oracle_ask_rate": (tp + fn) / max(n, 1),
        "predicted_ask_rate": (tp + fp) / max(n, 1),
        "accuracy": (tp + tn) / max(n, 1),
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-12),
        "missed_clarification_rate": fn / max(tp + fn, 1),
        "unnecessary_clarification_rate": fp / max(fp + tn, 1),
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
    }


def illustrative_utility(rows: list[dict], ask_cost: float, miss_cost: float) -> float:
    total = 0.0
    for row in rows:
        should_ask = int(row["require_clarification"]) == 1
        asked = int(row["predict_ambiguous"]) == 1
        if should_ask and asked:
            total += 1.0 - ask_cost
        elif should_ask and not asked:
            total -= miss_cost
        elif not should_ask and asked:
            total += 1.0 - ask_cost
        else:
            total += 1.0
    return total / max(len(rows), 1)


def metric_row(label: str, rows: list[dict], ask_cost: float, miss_cost: float) -> list[str]:
    stats = confusion(rows)
    return [
        label,
        str(int(stats["n"])),
        format_float(stats["oracle_ask_rate"]),
        format_float(stats["predicted_ask_rate"]),
        format_float(stats["accuracy"]),
        format_float(stats["precision"]),
        format_float(stats["recall"]),
        format_float(stats["missed_clarification_rate"]),
        format_float(stats["unnecessary_clarification_rate"]),
        format_float(illustrative_utility(rows, ask_cost, miss_cost)),
        f"{int(stats['tp'])}/{int(stats['fn'])}/{int(stats['fp'])}/{int(stats['tn'])}",
    ]


def grouped_table(rows: list[dict], key: str, ask_cost: float, miss_cost: float) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key, ""))].append(row)
    table_rows = [metric_row(name, group, ask_cost, miss_cost) for name, group in sorted(groups.items())]
    return markdown_table(
        [
            key.title(),
            "N",
            "Oracle ask",
            "Pred. ask",
            "Accuracy",
            "Precision",
            "Recall",
            "Missed",
            "Unnec.",
            "Illust. utility",
            "TP/FN/FP/TN",
        ],
        table_rows,
    )


def compact_examples(rows: list[dict], limit: int = 5) -> str:
    missed = [
        row
        for row in rows
        if int(row["require_clarification"]) == 1 and int(row["predict_ambiguous"]) == 0
    ][:limit]
    table_rows = []
    for row in missed:
        question = str(row["question"]).replace("\n", " ")
        clarifying = str(row["clarifying_question"]).replace("\n", " ")
        table_rows.append([row["category"], row["subclass"], question[:100], clarifying[:120]])
    return markdown_table(["Category", "Subclass", "User query excerpt", "Reference clarification excerpt"], table_rows)


def main() -> None:
    args = parse_args()
    path = Path(args.input)
    rows = read_clamber(path)
    overall = metric_row("all", rows, args.ask_cost, args.miss_cost)
    text = "\n".join(
        [
            "# CLAMBER External Sanity Check",
            "",
            "This is a small external-validity diagnostic, not a main Clarify-to-Act result. It maps CLAMBER's `require_clarification` field to an ASK label and the provided `predict_ambiguous` field to a query-only ambiguity-detector ASK prediction.",
            "",
            "The illustrative utility column uses a Clarify-to-Act-style projection with reward `1 - ask_cost` for asking, reward `1` for correctly not asking, and `-miss_cost` for missing a required clarification. It is not CLAMBER's task metric.",
            "",
            "## Source",
            "",
            markdown_table(
                ["Item", "Value"],
                [
                    ["Source URL", SOURCE_URL],
                    ["Local input", args.input],
                    ["Rows", str(len(rows))],
                    ["SHA256", sha256(path)],
                    ["Ask cost", format_float(args.ask_cost, 2)],
                    ["Miss cost", format_float(args.miss_cost, 2)],
                ],
            ),
            "## Overall",
            "",
            markdown_table(
                [
                    "Group",
                    "N",
                    "Oracle ask",
                    "Pred. ask",
                    "Accuracy",
                    "Precision",
                    "Recall",
                    "Missed",
                    "Unnec.",
                    "Illust. utility",
                    "TP/FN/FP/TN",
                ],
                [overall],
            ),
            "## By Category",
            "",
            grouped_table(rows, "category", args.ask_cost, args.miss_cost),
            "## By Subclass",
            "",
            grouped_table(rows, "subclass", args.ask_cost, args.miss_cost),
            "## Missed-Clarification Examples",
            "",
            compact_examples(rows),
            "## Interpretation",
            "",
            "- CLAMBER is query-level and not grounded in deterministic action reward, so this should only be used as external motivation.",
            "- The provided ambiguity prediction substantially under-asks relative to CLAMBER's clarification labels, especially in multi-constraint (`MC`) cases.",
            "- This supports the paper's framing that query-level ambiguity detection is complementary to, but weaker than, situated utility-calibrated ask/act evaluation.",
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote CLAMBER external sanity report to {args.out}")


if __name__ == "__main__":
    main()
