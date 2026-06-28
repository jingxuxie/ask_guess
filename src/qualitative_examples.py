from __future__ import annotations

import argparse
from collections.abc import Callable

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


CASE_SPECS: list[tuple[str, str, Callable[[dict], bool]]] = [
    ("Context resolves", "Act", lambda ep: ep["ambiguity_type"] == "context_resolved"),
    ("Equivalent outcomes", "Act", lambda ep: ep["ambiguity_type"] == "equivalent_outcome"),
    ("Referential ambiguity", "Ask", lambda ep: ep["ambiguity_type"] == "referential"),
    ("High-risk ambiguity", "Ask", lambda ep: ep["ambiguity_type"] == "risk_sensitive"),
    (
        "Preference visible",
        "Act",
        lambda ep: ep["ambiguity_type"] == "preference_social" and ep["variant"] == "owner_visible",
    ),
    (
        "Preference hidden",
        "Ask",
        lambda ep: ep["ambiguity_type"] == "preference_social" and ep["variant"] == "owner_hidden",
    ),
]


PREFERRED_EPISODES = {
    "Context resolves": "test_context_000251",
    "Equivalent outcomes": "test_equivalent_000122",
    "Referential ambiguity": "test_referential_000395",
    "High-risk ambiguity": "test_risk_000033",
    "Preference visible": "test_preference_000294",
    "Preference hidden": "test_preference_000339",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/qualitative_examples.md")
    return parser.parse_args()


def escape_cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def find_episode(episodes: list[dict], label: str, predicate: Callable[[dict], bool]) -> dict:
    preferred = PREFERRED_EPISODES[label]
    for ep in episodes:
        if ep["episode_id"] == preferred:
            return ep
    for ep in episodes:
        if ep["split"] == "test" and predicate(ep):
            return ep
    raise ValueError(f"no test episode found for {label}")


def object_by_id(ep: dict) -> dict[str, dict]:
    return {obj["id"]: obj for obj in ep["scene"]["objects"]}


def visible_object_desc(obj: dict) -> str:
    owner = obj["owner"] if obj.get("visible_owner", True) else "owner hidden"
    reach = "reachable" if obj.get("reachable", True) else "unreachable"
    return (
        f"{obj['state']} {obj['color']} {obj['type']} at {obj['location']} "
        f"({owner}, salience {format_float(float(obj['salience']), 2)}, {reach})"
    )


def compact_situation(ep: dict) -> str:
    objects = object_by_id(ep)
    candidate_objects = [objects[intent["target_id"]] for intent in ep["candidate_intents"]]
    if ep["ambiguity_type"] == "context_resolved":
        ranked = sorted(candidate_objects, key=lambda obj: float(obj["salience"]), reverse=True)
        return f"{visible_object_desc(ranked[0])}; distractor {visible_object_desc(ranked[-1])}"
    if ep["ambiguity_type"] == "equivalent_outcome":
        target_type = candidate_objects[0]["type"]
        success_classes = {intent["success_equivalence_class"] for intent in ep["candidate_intents"]}
        return f"{len(candidate_objects)} spare {target_type}s; {len(success_classes)} success class for all targets"
    if ep["ambiguity_type"] == "risk_sensitive":
        top = max(ep["candidate_intents"], key=lambda intent: float(intent["prior"]))
        top_obj = objects[top["target_id"]]
        return (
            f"top candidate {visible_object_desc(top_obj)} with prior {format_float(float(top['prior']), 3)}; "
            f"wrong-action cost {format_float(float(ep['wrong_action_cost']))}"
        )
    if ep["ambiguity_type"] == "preference_social":
        user = ep["scene"].get("current_user", "user")
        return f"current_user={user}; " + "; ".join(visible_object_desc(obj) for obj in candidate_objects)
    return "; ".join(visible_object_desc(obj) for obj in candidate_objects)


def utility_reason(ep: dict) -> str:
    margin = format_float(float(ep["features"]["eu_ask_minus_act"]))
    ask_cost = format_float(float(ep["ask_cost"]))
    if ep["oracle_should_ask"]:
        return f"EU(ask)-EU(act)={margin} despite ask cost {ask_cost}"
    return f"EU(ask)-EU(act)={margin}; asking would waste cost {ask_cost}"


def result_index(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(row["episode_id"], row["policy"]): row for row in rows}


def action_target(row: dict | None) -> str:
    if not row:
        return "not evaluated"
    action = row.get("final_action") or {}
    target = action.get("target_id", "?")
    verb = action.get("action", "act")
    prefix = "ASK then" if row.get("asked") else "ACT"
    return f"{prefix} {verb} {target}; reward {format_float(float(row['reward']))}"


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    api_rows = read_jsonl(args.api_results)
    api_by_episode = result_index(api_rows)

    rows = []
    for label, oracle_action, predicate in CASE_SPECS:
        ep = find_episode(episodes, label, predicate)
        ask_needed = api_by_episode.get((ep["episode_id"], "api_ask_needed"))
        ecu = api_by_episode.get((ep["episode_id"], "api_ecu"))
        rows.append(
            [
                label,
                ep["episode_id"],
                ep["user_instruction"],
                compact_situation(ep),
                utility_reason(ep),
                oracle_action,
                action_target(ask_needed),
                action_target(ecu),
            ]
        )

    text = "\n".join(
        [
            "# Qualitative Benchmark Examples",
            "",
            "Representative examples are selected deterministically from the canonical 100-episode API subset when available.",
            "They illustrate why the paper evaluates expected communicative utility rather than ambiguity detection alone.",
            "",
            markdown_table(
                [
                    "Case",
                    "Episode",
                    "Instruction",
                    "Visible situation",
                    "Utility reason",
                    "Oracle",
                    "Prompted Ask-Needed",
                    "API ECU",
                ],
                [[escape_cell(cell) for cell in row] for row in rows],
            ),
        ]
    )
    write_text(args.out, text)
    print(f"wrote qualitative examples to {args.out}")


if __name__ == "__main__":
    main()
