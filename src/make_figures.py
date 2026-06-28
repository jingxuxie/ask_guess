from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate


API_POLICY_LABELS = {
    "api_direct_act": "DirectAct",
    "api_ask_needed": "Ask-Needed",
    "api_ask_needed_cot": "Ask-Needed + private reasoning",
    "api_ecu": "ECU",
}

OFFLINE_POLICY_LABELS = {
    "direct_act": "DirectAct",
    "prompted_heuristic": "Prompted",
    "ecu": "ECU",
}

POLICY_COLORS = {
    "api_direct_act": "#6b7280",
    "api_ask_needed": "#d97706",
    "api_ask_needed_cot": "#7c3aed",
    "api_ecu": "#0f766e",
    "direct_act": "#6b7280",
    "prompted_heuristic": "#d97706",
    "ecu": "#0f766e",
}

CATEGORY_LABELS = {
    "context_resolved": "Context",
    "preference_social": "Preference",
    "equivalent_outcome": "Equivalent",
    "referential": "Referential",
    "risk_sensitive": "Risk",
}

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
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--cost-table", default="paper/tables/cost_sensitivity.md")
    parser.add_argument("--out-dir", default="paper/figures")
    return parser.parse_args()


def svg_header(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#111827}",
        ".title{font-size:22px;font-weight:700}",
        ".subtitle{font-size:13px;fill:#4b5563}",
        ".axis{stroke:#374151;stroke-width:1}",
        ".grid{stroke:#e5e7eb;stroke-width:1}",
        ".tick{font-size:12px;fill:#4b5563}",
        ".label{font-size:13px;fill:#374151}",
        ".legend{font-size:13px;fill:#111827}",
        "</style>",
    ]


def save_svg(path: Path, parts: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts + ["</svg>\n"]), encoding="utf-8")


def y_position(value: float, y: int, height: int, y_min: float, y_max: float) -> float:
    return y + (y_max - value) / (y_max - y_min) * height


def draw_axes(
    parts: list[str],
    x: int,
    y: int,
    width: int,
    height: int,
    y_ticks: list[float],
    y_min: float = 0.0,
    y_max: float = 1.0,
) -> None:
    bottom = y + height
    x_axis_y = y_position(0.0, y, height, y_min, y_max) if y_min <= 0.0 <= y_max else bottom
    parts.append(f'<line class="axis" x1="{x}" y1="{x_axis_y:.1f}" x2="{x + width}" y2="{x_axis_y:.1f}"/>')
    parts.append(f'<line class="axis" x1="{x}" y1="{y}" x2="{x}" y2="{bottom}"/>')
    for tick in y_ticks:
        ty = y_position(tick, y, height, y_min, y_max)
        parts.append(f'<line class="grid" x1="{x}" y1="{ty:.1f}" x2="{x + width}" y2="{ty:.1f}"/>')
        label = f"{tick:.2f}".rstrip("0").rstrip(".")
        if "." not in label:
            label = f"{label}.0"
        parts.append(f'<text class="tick" x="{x - 10}" y="{ty + 4:.1f}" text-anchor="end">{label}</text>')


def bar_chart(
    path: Path,
    title: str,
    subtitle: str,
    labels: list[str],
    series: list[tuple[str, list[float], str]],
    y_label: str = "Net utility",
) -> None:
    width, height = 980, 560
    margin_left, margin_right, margin_top, margin_bottom = 80, 40, 78, 120
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    all_values = [value for _name, values, _color in series for value in values]
    y_min = -0.25 if all_values and min(all_values) < 0.0 else 0.0
    y_max = 1.0
    y_ticks = [-0.25, 0.0, 0.25, 0.5, 0.75, 1.0] if y_min < 0.0 else [0.0, 0.25, 0.5, 0.75, 1.0]
    parts = svg_header(width, height)
    parts.append(f'<text class="title" x="40" y="34">{escape(title)}</text>')
    parts.append(f'<text class="subtitle" x="40" y="56">{escape(subtitle)}</text>')
    draw_axes(parts, margin_left, margin_top, plot_w, plot_h, y_ticks, y_min=y_min, y_max=y_max)
    zero_y = y_position(0.0, margin_top, plot_h, y_min, y_max)

    group_w = plot_w / len(labels)
    bar_gap = 7
    bar_w = min(58, (group_w - 26) / len(series) - bar_gap)
    for i, label in enumerate(labels):
        cx = margin_left + group_w * i + group_w / 2
        parts.append(f'<text class="tick" x="{cx:.1f}" y="{height - 78}" text-anchor="middle">{escape(label)}</text>')
        for j, (name, values, color) in enumerate(series):
            x = cx - ((len(series) * bar_w + (len(series) - 1) * bar_gap) / 2) + j * (bar_w + bar_gap)
            value = values[i]
            value_y = y_position(value, margin_top, plot_h, y_min, y_max)
            y = min(value_y, zero_y)
            bar_h = abs(value_y - zero_y)
            label_y = y - 5 if value >= 0 else y + bar_h + 14
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" rx="2"/>')
            parts.append(f'<text class="tick" x="{x + bar_w / 2:.1f}" y="{label_y:.1f}" text-anchor="middle">{value:.2f}</text>')

    legend_x = margin_left
    legend_y = height - 36
    for idx, (name, _values, color) in enumerate(series):
        lx = legend_x + idx * 155
        parts.append(f'<rect x="{lx}" y="{legend_y - 12}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text class="legend" x="{lx + 20}" y="{legend_y}">{escape(name)}</text>')
    parts.append(f'<text class="label" transform="translate(22 {margin_top + plot_h / 2}) rotate(-90)" text-anchor="middle">{escape(y_label)}</text>')
    save_svg(path, parts)


def line_chart(path: Path, title: str, subtitle: str, x_label: str, x_values: list[float], series: list[tuple[str, list[float], str]]) -> None:
    width, height = 920, 540
    margin_left, margin_right, margin_top, margin_bottom = 80, 42, 78, 86
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    parts = svg_header(width, height)
    parts.append(f'<text class="title" x="40" y="34">{escape(title)}</text>')
    parts.append(f'<text class="subtitle" x="40" y="56">{escape(subtitle)}</text>')
    draw_axes(parts, margin_left, margin_top, plot_w, plot_h, [0.0, 0.25, 0.5, 0.75, 1.0])
    x_min, x_max = min(x_values), max(x_values)

    def sx(value: float) -> float:
        if x_max == x_min:
            return margin_left + plot_w / 2
        return margin_left + (value - x_min) / (x_max - x_min) * plot_w

    def sy(value: float) -> float:
        return margin_top + plot_h - value * plot_h

    for value in x_values:
        x = sx(value)
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{margin_top + plot_h}"/>')
        parts.append(f'<text class="tick" x="{x:.1f}" y="{height - 54}" text-anchor="middle">{value:g}</text>')

    for name, values, color in series:
        points = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in zip(x_values, values))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, y in zip(x_values, values):
            parts.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{color}"/>')
        lx = sx(x_values[-1]) + 8
        ly = sy(values[-1]) + 4
        parts.append(f'<text class="legend" x="{lx:.1f}" y="{ly:.1f}">{escape(name)}</text>')

    parts.append(f'<text class="label" x="{margin_left + plot_w / 2}" y="{height - 18}" text-anchor="middle">{escape(x_label)}</text>')
    parts.append(f'<text class="label" transform="translate(22 {margin_top + plot_h / 2}) rotate(-90)" text-anchor="middle">Net utility</text>')
    save_svg(path, parts)


def aggregate_by_policy(rows: list[dict]) -> dict[str, dict]:
    return {policy: aggregate([r for r in rows if r["policy"] == policy]) for policy in sorted({r["policy"] for r in rows})}


def make_api_main(api_rows: list[dict], out_dir: Path) -> None:
    stats = aggregate_by_policy(api_rows)
    policies = ["api_direct_act", "api_ask_needed", "api_ecu"]
    labels = [API_POLICY_LABELS[p] for p in policies]
    values = [stats[p]["net_utility"] for p in policies]
    bar_chart(
        out_dir / "api_main_net_utility.svg",
        "API Policy Net Utility",
        "100 stratified test episodes, GPT-4.1-mini",
        labels,
        [("Net utility", values, "#0f766e")],
    )


def make_api_category(api_rows: list[dict], out_dir: Path) -> None:
    labels = [CATEGORY_LABELS[c] for c in CATEGORY_ORDER]
    series = []
    for policy in ["api_direct_act", "api_ask_needed", "api_ecu"]:
        values = []
        for category in CATEGORY_ORDER:
            subset = [r for r in api_rows if r["policy"] == policy and r["ambiguity_type"] == category]
            values.append(aggregate(subset)["net_utility"])
        series.append((API_POLICY_LABELS[policy], values, POLICY_COLORS[policy]))
    bar_chart(
        out_dir / "api_category_net_utility.svg",
        "API Net Utility by Category",
        "Clarification is useful only when it changes expected task utility",
        labels,
        series,
    )


def utility_margin_bin(margin: float) -> str:
    if margin <= -0.05:
        return "act_preferred"
    if margin <= 0.05:
        return "near_tie"
    return "ask_preferred"


def make_api_calibration(episodes: list[dict], api_rows: list[dict], out_dir: Path) -> None:
    episode_map = {episode["episode_id"]: episode for episode in episodes}
    selected_ids = sorted({row["episode_id"] for row in api_rows})
    bin_order = ["act_preferred", "near_tie", "ask_preferred"]
    labels = ["Act preferred", "Near tie", "Ask preferred"]

    episode_bins: dict[str, list[dict]] = defaultdict(list)
    for episode_id in selected_ids:
        episode = episode_map[episode_id]
        margin = float(episode["features"]["eu_ask_minus_act"])
        episode_bins[utility_margin_bin(margin)].append(episode)

    row_bins: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in api_rows:
        episode = episode_map[row["episode_id"]]
        margin = float(episode["features"]["eu_ask_minus_act"])
        row_bins[(row["policy"], utility_margin_bin(margin))].append(row)

    oracle_values = []
    for bin_name in bin_order:
        bin_episodes = episode_bins[bin_name]
        oracle_values.append(sum(1 for episode in bin_episodes if episode["oracle_should_ask"]) / max(len(bin_episodes), 1))

    series = [("Oracle", oracle_values, "#111827")]
    for policy in ["api_ask_needed", "api_ecu"]:
        values = []
        for bin_name in bin_order:
            rows = row_bins[(policy, bin_name)]
            values.append(aggregate(rows)["ask_rate"])
        series.append((API_POLICY_LABELS[policy], values, POLICY_COLORS[policy]))

    bar_chart(
        out_dir / "api_calibration_ask_rate.svg",
        "Ask Rate by Utility Margin",
        "Main API set: prompted asking is not calibrated to the value of information",
        labels,
        series,
        y_label="Ask rate",
    )


def parse_cost_table(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0] in {"Ask cost", "---"}:
            continue
        try:
            rows.append(
                {
                    "ask_cost": float(cells[0]),
                    "wrong_cost": float(cells[1]),
                    "method": cells[2],
                    "net_utility": float(cells[3]),
                    "success": float(cells[4]),
                    "ask_rate": float(cells[5]),
                    "oracle_ask_rate": float(cells[6]),
                }
            )
        except (ValueError, IndexError):
            continue
    return rows


def make_cost_figures(cost_rows: list[dict], out_dir: Path) -> None:
    methods = ["direct_act", "prompted_heuristic", "ecu"]
    ask_rows = [r for r in cost_rows if abs(r["wrong_cost"] - 1.0) < 1e-9]
    ask_values = sorted({r["ask_cost"] for r in ask_rows})
    ask_series = []
    for method in methods:
        by_x = {r["ask_cost"]: r["net_utility"] for r in ask_rows if r["method"] == method}
        ask_series.append((OFFLINE_POLICY_LABELS[method], [by_x[x] for x in ask_values], POLICY_COLORS[method]))
    line_chart(
        out_dir / "cost_sensitivity_ask_cost.svg",
        "Ask Cost Sensitivity",
        "Wrong-action cost fixed at 1.0",
        "Ask cost",
        ask_values,
        ask_series,
    )

    wrong_rows = [r for r in cost_rows if abs(r["ask_cost"] - 0.05) < 1e-9]
    wrong_values = sorted({r["wrong_cost"] for r in wrong_rows})
    wrong_series = []
    for method in methods:
        by_x = {r["wrong_cost"]: r["net_utility"] for r in wrong_rows if r["method"] == method}
        wrong_series.append((OFFLINE_POLICY_LABELS[method], [by_x[x] for x in wrong_values], POLICY_COLORS[method]))
    line_chart(
        out_dir / "cost_sensitivity_wrong_cost.svg",
        "Wrong-Action Cost Sensitivity",
        "Ask cost fixed at 0.05",
        "Wrong-action cost",
        wrong_values,
        wrong_series,
    )


def write_index(out_dir: Path) -> None:
    text = """# Figure Index

## `api_main_net_utility.svg`

Main API result. Shows net utility for DirectAct, prompted Ask-Needed, and API ECU on the 100-episode stratified GPT-4.1-mini evaluation.

## `api_category_net_utility.svg`

Category breakdown for the same API evaluation. This is the strongest single figure for the paper because it shows the difference between genuine ambiguity, context-resolved underspecification, equivalent outcomes, risk, and preference/social cases.

## `current_model_category_net_utility.svg`

Current-model category breakdown generated by `src/current_model_category_modes.py`. It compares plain prompted Ask-Needed against ECU for GPT-4.1-mini, GPT-5.4-mini, and GPT-5.5 on the same 100-episode stratified subset.

## `api_calibration_ask_rate.svg`

Ask-rate calibration by oracle expected-utility margin on the main API set. ECU tracks the oracle, while prompted Ask-Needed asks at similar rates when acting is preferred and when asking is preferred.

## `cost_sensitivity_ask_cost.svg`

Offline cost-sensitivity curve with wrong-action cost fixed at 1.0. ECU adapts to increasing clarification cost, while the prompted heuristic remains fixed.

## `cost_sensitivity_wrong_cost.svg`

Offline cost-sensitivity curve with ask cost fixed at 0.05. DirectAct degrades as wrong-action cost rises, while ECU remains robust by asking in high-stakes cases.
"""
    write_text(out_dir / "FIGURE_INDEX.md", text)


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    episodes = read_jsonl(args.episodes)
    api_rows = read_jsonl(args.api_results)
    cost_rows = parse_cost_table(args.cost_table)
    make_api_main(api_rows, out_dir)
    make_api_category(api_rows, out_dir)
    make_api_calibration(episodes, api_rows, out_dir)
    make_cost_figures(cost_rows, out_dir)
    write_index(out_dir)
    print(f"wrote figures to {out_dir}")


if __name__ == "__main__":
    main()
