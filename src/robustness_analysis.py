from __future__ import annotations

import argparse
from collections import defaultdict
from statistics import mean

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table


HELDOUT_TYPES = {"charger", "keys", "remote", "notebook", "water_bottle"}
POLICY_ORDER = [
    "direct_act",
    "ask_always",
    "raw_ambiguity",
    "prompted_heuristic",
    "ecu",
    "ecu_threshold",
    "learned_controller",
]
KEY_POLICIES = {"direct_act", "prompted_heuristic", "ecu", "learned_controller"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--out", default="paper/tables/robustness_breakdown.md")
    return parser.parse_args()


def policy_sort_key(policy: str) -> tuple[int, str]:
    try:
        return (POLICY_ORDER.index(policy), policy)
    except ValueError:
        return (999, policy)


def episode_has_heldout_object(episode: dict) -> bool:
    return any(obj.get("type") in HELDOUT_TYPES for obj in episode.get("scene", {}).get("objects", []))


def episode_object_types(episode: dict) -> str:
    return ", ".join(sorted({str(obj.get("type", "")) for obj in episode.get("scene", {}).get("objects", [])}))


def split_delta_table(rows: list[dict]) -> str:
    grouped = group_rows(rows, ("split", "policy"))
    table_rows = []
    for policy in sorted({row["policy"] for row in rows}, key=policy_sort_key):
        if ("test", policy) not in grouped or ("ood_test", policy) not in grouped:
            continue
        test_stats = aggregate(grouped[("test", policy)])
        ood_stats = aggregate(grouped[("ood_test", policy)])
        table_rows.append(
            [
                policy,
                format_float(test_stats["net_utility"]),
                format_float(ood_stats["net_utility"]),
                format_float(ood_stats["net_utility"] - test_stats["net_utility"]),
                format_float(test_stats["success"]),
                format_float(ood_stats["success"]),
                format_float(test_stats["ask_rate"]),
                format_float(ood_stats["ask_rate"]),
            ]
        )
    return markdown_table(
        ["Method", "Test utility", "OOD utility", "OOD - test", "Test success", "OOD success", "Test ask", "OOD ask"],
        table_rows,
    )


def category_delta_table(rows: list[dict]) -> str:
    grouped = group_rows([row for row in rows if row["policy"] in KEY_POLICIES], ("split", "ambiguity_type", "policy"))
    table_rows = []
    keys = sorted(
        {
            (category, policy)
            for split, category, policy in grouped
            if split in {"test", "ood_test"}
        },
        key=lambda item: (item[0], policy_sort_key(item[1])),
    )
    for category, policy in keys:
        test_rows = grouped.get(("test", category, policy), [])
        ood_rows = grouped.get(("ood_test", category, policy), [])
        if not test_rows or not ood_rows:
            continue
        test_stats = aggregate(test_rows)
        ood_stats = aggregate(ood_rows)
        table_rows.append(
            [
                category,
                policy,
                str(test_stats["n"]),
                str(ood_stats["n"]),
                format_float(test_stats["net_utility"]),
                format_float(ood_stats["net_utility"]),
                format_float(ood_stats["net_utility"] - test_stats["net_utility"]),
            ]
        )
    return markdown_table(["Category", "Method", "Test N", "OOD N", "Test utility", "OOD utility", "OOD - test"], table_rows)


def heldout_slice_table(episodes: list[dict], rows: list[dict]) -> str:
    episode_meta = {
        ep["episode_id"]: {
            "heldout": episode_has_heldout_object(ep),
            "object_types": episode_object_types(ep),
        }
        for ep in episodes
    }
    enriched = []
    for row in rows:
        if row["split"] != "ood_test":
            continue
        meta = episode_meta[row["episode_id"]]
        new_row = dict(row)
        new_row["heldout_object"] = meta["heldout"]
        enriched.append(new_row)

    grouped = group_rows(enriched, ("heldout_object", "policy"))
    table_rows = []
    for heldout in [True, False]:
        for policy in sorted({row["policy"] for row in enriched}, key=policy_sort_key):
            group = grouped.get((heldout, policy), [])
            if not group:
                continue
            stats = aggregate(group)
            table_rows.append(
                [
                    "held-out object" if heldout else "no held-out object",
                    policy,
                    str(stats["n"]),
                    format_float(stats["net_utility"]),
                    format_float(stats["success"]),
                    format_float(stats["ask_rate"]),
                ]
            )
    return markdown_table(["OOD slice", "Method", "N", "Net utility", "Success", "Ask rate"], table_rows)


def object_type_table(episodes: list[dict]) -> str:
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for ep in episodes:
        if ep["split"] not in {"test", "ood_test"}:
            continue
        for obj_type in {obj["type"] for obj in ep["scene"]["objects"]}:
            counts[(ep["split"], obj_type)] += 1
    table_rows = []
    for obj_type in sorted({key[1] for key in counts}):
        table_rows.append(
            [
                obj_type,
                str(counts.get(("test", obj_type), 0)),
                str(counts.get(("ood_test", obj_type), 0)),
                "yes" if obj_type in HELDOUT_TYPES else "no",
            ]
        )
    return markdown_table(["Object type", "Test episodes", "OOD episodes", "Held out from train/dev/test pools"], table_rows)


def headline(rows: list[dict]) -> str:
    grouped = group_rows(rows, ("split", "policy"))
    bits = []
    for policy in ["prompted_heuristic", "ecu", "learned_controller"]:
        test_stats = aggregate(grouped[("test", policy)])
        ood_stats = aggregate(grouped[("ood_test", policy)])
        bits.append(
            f"- `{policy}`: test {format_float(test_stats['net_utility'])}, "
            f"OOD {format_float(ood_stats['net_utility'])}, "
            f"delta {format_float(ood_stats['net_utility'] - test_stats['net_utility'])}"
        )
    return "\n".join(bits) + "\n"


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    rows = read_jsonl(args.results)
    sections = [
        "# Robustness Breakdown\n\n",
        "The OOD split uses the same diagnostic categories with shifted object types where the generator supports them. This table is offline-only and uses the frozen deterministic results.\n\n",
        "## Headline OOD Deltas\n\n",
        headline(rows),
        "\n## Split-Level Deltas\n\n",
        split_delta_table(rows),
        "\n## Category-Level Deltas\n\n",
        category_delta_table(rows),
        "\n## OOD Held-Out Object Slice\n\n",
        heldout_slice_table(episodes, rows),
        "\n## Object Type Coverage\n\n",
        object_type_table(episodes),
    ]
    write_text(args.out, "".join(sections))
    print(f"wrote robustness breakdown to {args.out}")


if __name__ == "__main__":
    main()
