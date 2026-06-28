from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table


DEFAULT_RUNS = [
    (
        "gpt-4.1-mini",
        [
            "data/runs/api_eval_100_corrected_results.jsonl",
            "data/runs/api_eval_100_cot_results.jsonl",
        ],
    ),
    ("gpt-5.4-mini", ["data/runs/api_gpt_5_4_mini_test100_results.jsonl"]),
    ("gpt-5.5", ["data/runs/api_gpt_5_5_test100_results.jsonl"]),
]

CATEGORY_ORDER = [
    "context_resolved",
    "preference_social",
    "equivalent_outcome",
    "referential",
    "risk_sensitive",
]

CATEGORY_LABELS = {
    "context_resolved": "Context",
    "preference_social": "Preference",
    "equivalent_outcome": "Equivalent",
    "referential": "Referential",
    "risk_sensitive": "Risk",
}

POLICIES = ["api_ask_needed", "api_ask_needed_cot", "api_ecu"]
POLICY_LABELS = {
    "api_ask_needed": "Ask-Needed",
    "api_ask_needed_cot": "CoT Ask-Needed",
    "api_ecu": "ECU",
}
POLICY_COLORS = {
    "api_ask_needed": "#d97706",
    "api_ecu": "#0f766e",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        action="append",
        help="Model label and comma-separated result paths, formatted as model=path[,path2].",
    )
    parser.add_argument("--out", default="paper/tables/current_model_category_failure_modes.md")
    parser.add_argument("--figure-out", default="paper/figures/current_model_category_net_utility.svg")
    return parser.parse_args()


def parse_run_spec(spec: str) -> tuple[str, list[str]]:
    label, sep, paths = spec.partition("=")
    if not sep or not label.strip() or not paths.strip():
        raise ValueError(f"Invalid --run {spec!r}; expected model=path[,path2].")
    return label.strip(), [path.strip() for path in paths.split(",") if path.strip()]


def run_specs(args: argparse.Namespace) -> list[tuple[str, list[str]]]:
    if args.run:
        return [parse_run_spec(spec) for spec in args.run]
    return DEFAULT_RUNS


def load_rows(paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        rows.extend(read_jsonl(path))
    return rows


def stats_for(rows: list[dict], policy: str, category: str) -> dict | None:
    selected = [row for row in rows if row["policy"] == policy and row["ambiguity_type"] == category]
    if not selected:
        return None
    return aggregate(selected)


def fmt_stat(stats: dict | None, key: str) -> str:
    return "-" if stats is None else format_float(float(stats[key]))


def row_records(runs: list[tuple[str, list[dict]]]) -> list[dict]:
    records: list[dict] = []
    for model, rows in runs:
        for category in CATEGORY_ORDER:
            ask = stats_for(rows, "api_ask_needed", category)
            cot = stats_for(rows, "api_ask_needed_cot", category)
            ecu = stats_for(rows, "api_ecu", category)
            if ask is None or ecu is None:
                continue
            records.append(
                {
                    "model": model,
                    "category": category,
                    "n": int(ask["n"]),
                    "ask": ask,
                    "cot": cot,
                    "ecu": ecu,
                    "delta": float(ecu["net_utility"]) - float(ask["net_utility"]),
                }
            )
    return records


def failure_label(ask: dict) -> str:
    missed = float(ask["missed_clarification_rate"])
    unnecessary = float(ask["unnecessary_clarification_rate"])
    if missed > 0.0 and unnecessary > 0.0:
        return "mixed ask timing"
    if missed > 0.0:
        return "under-asks"
    if unnecessary > 0.0:
        return "over-asks"
    return "matched ask timing"


def summary(records: list[dict]) -> str:
    lines = [
        "# Current-Model Category Failure Modes",
        "",
        "This no-API analysis uses cached 100-episode stratified result files. The figure intentionally compares plain prompted Ask-Needed against ECU; the CoT column is included as context because GPT-5.5 private reasoning closes some category gaps on this subset.",
        "",
        "## Summary",
        "",
    ]
    for model in sorted({record["model"] for record in records}):
        model_records = [record for record in records if record["model"] == model]
        largest = max(model_records, key=lambda record: record["delta"])
        ask = largest["ask"]
        lines.append(
            "- "
            + model
            + ": largest plain Ask-Needed gap is "
            + CATEGORY_LABELS[largest["category"]]
            + " (ECU - Ask-Needed "
            + format_float(largest["delta"])
            + "), with "
            + failure_label(ask)
            + " behavior; missed="
            + format_float(float(ask["missed_clarification_rate"]))
            + ", unnecessary="
            + format_float(float(ask["unnecessary_clarification_rate"]))
            + "."
        )

    max_ecu_missed = max(float(record["ecu"]["missed_clarification_rate"]) for record in records)
    max_ecu_unnecessary = max(float(record["ecu"]["unnecessary_clarification_rate"]) for record in records)
    lines.extend(
        [
            "- Across these model/category cells, ECU's maximum missed and unnecessary clarification rates are "
            + format_float(max_ecu_missed)
            + " and "
            + format_float(max_ecu_unnecessary)
            + ".",
            "",
            "## Category Table",
            "",
        ]
    )
    return "\n".join(lines)


def table(records: list[dict]) -> str:
    rows = []
    for record in records:
        ask = record["ask"]
        cot = record["cot"]
        ecu = record["ecu"]
        rows.append(
            [
                record["model"],
                CATEGORY_LABELS[record["category"]],
                str(record["n"]),
                format_float(float(ask["net_utility"])),
                fmt_stat(cot, "net_utility"),
                format_float(float(ecu["net_utility"])),
                format_float(record["delta"]),
                format_float(float(ask["ask_rate"])),
                format_float(float(ask["oracle_ask_rate"])),
                format_float(float(ask["missed_clarification_rate"])),
                format_float(float(ask["unnecessary_clarification_rate"])),
                format_float(float(ecu["missed_clarification_rate"])),
                format_float(float(ecu["unnecessary_clarification_rate"])),
            ]
        )
    return markdown_table(
        [
            "Model",
            "Category",
            "N",
            "Ask utility",
            "CoT utility",
            "ECU utility",
            "ECU - Ask",
            "Ask rate",
            "Oracle ask",
            "Ask missed",
            "Ask unnecessary",
            "ECU missed",
            "ECU unnecessary",
        ],
        rows,
    )


def y_pos(value: float, top: int, height: int, y_min: float, y_max: float) -> float:
    return top + (y_max - value) / (y_max - y_min) * height


def write_svg(records: list[dict], path: Path) -> None:
    models = [model for model, _paths in DEFAULT_RUNS if any(record["model"] == model for record in records)]
    for record in records:
        if record["model"] not in models:
            models.append(record["model"])

    width, height = 1260, 560
    margin_left, margin_right, margin_top, margin_bottom = 72, 36, 82, 112
    panel_gap = 34
    panel_width = (width - margin_left - margin_right - panel_gap * (len(models) - 1)) / len(models)
    plot_height = height - margin_top - margin_bottom
    y_min, y_max = -0.25, 1.0
    y_ticks = [-0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
    zero_y = y_pos(0.0, margin_top, plot_height, y_min, y_max)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#111827}",
        ".title{font-size:22px;font-weight:700}",
        ".subtitle{font-size:13px;fill:#4b5563}",
        ".facet{font-size:15px;font-weight:700}",
        ".axis{stroke:#374151;stroke-width:1}",
        ".grid{stroke:#e5e7eb;stroke-width:1}",
        ".tick{font-size:11px;fill:#4b5563}",
        ".legend{font-size:13px;fill:#111827}",
        ".label{font-size:13px;fill:#374151}",
        "</style>",
        '<text class="title" x="40" y="34">Current-Model Category Net Utility</text>',
        '<text class="subtitle" x="40" y="56">Plain prompted Ask-Needed versus expected communicative utility, 100 stratified episodes per model</text>',
    ]

    for model_index, model in enumerate(models):
        left = margin_left + model_index * (panel_width + panel_gap)
        right = left + panel_width
        records_by_category = {
            record["category"]: record for record in records if record["model"] == model
        }
        parts.append(f'<text class="facet" x="{left:.1f}" y="{margin_top - 18}">{escape(model)}</text>')
        parts.append(f'<line class="axis" x1="{left:.1f}" y1="{zero_y:.1f}" x2="{right:.1f}" y2="{zero_y:.1f}"/>')
        parts.append(f'<line class="axis" x1="{left:.1f}" y1="{margin_top}" x2="{left:.1f}" y2="{margin_top + plot_height}"/>')

        for tick in y_ticks:
            ty = y_pos(tick, margin_top, plot_height, y_min, y_max)
            parts.append(f'<line class="grid" x1="{left:.1f}" y1="{ty:.1f}" x2="{right:.1f}" y2="{ty:.1f}"/>')
            if model_index == 0:
                label = f"{tick:.2f}".rstrip("0").rstrip(".")
                if "." not in label:
                    label = f"{label}.0"
                parts.append(f'<text class="tick" x="{left - 10:.1f}" y="{ty + 4:.1f}" text-anchor="end">{label}</text>')

        group_width = panel_width / len(CATEGORY_ORDER)
        bar_width = min(24.0, group_width / 3.2)
        for category_index, category in enumerate(CATEGORY_ORDER):
            record = records_by_category[category]
            center = left + category_index * group_width + group_width / 2
            values = [
                ("api_ask_needed", float(record["ask"]["net_utility"])),
                ("api_ecu", float(record["ecu"]["net_utility"])),
            ]
            for bar_index, (policy, value) in enumerate(values):
                x = center - bar_width - 3 + bar_index * (bar_width + 6)
                value_y = y_pos(value, margin_top, plot_height, y_min, y_max)
                y = min(value_y, zero_y)
                bar_height = abs(value_y - zero_y)
                label_y = y - 5 if value >= 0 else y + bar_height + 13
                parts.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{POLICY_COLORS[policy]}" rx="2"/>'
                )
                parts.append(f'<text class="tick" x="{x + bar_width / 2:.1f}" y="{label_y:.1f}" text-anchor="middle">{value:.2f}</text>')
            parts.append(
                f'<text class="tick" x="{center:.1f}" y="{height - 70}" text-anchor="middle">{escape(CATEGORY_LABELS[category])}</text>'
            )

    legend_y = height - 28
    legend_x = margin_left
    for index, policy in enumerate(["api_ask_needed", "api_ecu"]):
        lx = legend_x + index * 150
        parts.append(f'<rect x="{lx}" y="{legend_y - 13}" width="14" height="14" fill="{POLICY_COLORS[policy]}" rx="2"/>')
        parts.append(f'<text class="legend" x="{lx + 20}" y="{legend_y}">{escape(POLICY_LABELS[policy])}</text>')
    parts.append(f'<text class="label" transform="translate(22 {margin_top + plot_height / 2}) rotate(-90)" text-anchor="middle">Net utility</text>')
    parts.append("</svg>\n")
    write_text(path, "\n".join(parts))


def main() -> None:
    args = parse_args()
    runs = [(label, load_rows(paths)) for label, paths in run_specs(args)]
    records = row_records(runs)
    write_text(args.out, summary(records) + table(records))
    write_svg(records, Path(args.figure_out))
    print(f"wrote category failure-mode table to {args.out}")
    print(f"wrote category failure-mode figure to {args.figure_out}")


if __name__ == "__main__":
    main()
