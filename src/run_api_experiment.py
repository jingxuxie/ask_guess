from __future__ import annotations

import argparse
import json
from pathlib import Path

from clarify_to_act.api_client import CachedResponsesClient, OpenAIAPIError, parse_json_object, read_api_key
from clarify_to_act.environment import action_success, act_from_intent, compute_reward, simulated_user_answer
from clarify_to_act.generator import eu_advantage
from clarify_to_act.io import read_jsonl, write_jsonl
from clarify_to_act.metrics import aggregate, format_float, markdown_table
from clarify_to_act.policies import diagnostic_question


PROMPT_DIR = Path("prompts")
API_ECU_ASK_MARGIN = 0.075


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--out", default="data/runs/api_smoke_results.jsonl")
    parser.add_argument("--summary-out", default="paper/tables/api_smoke_results.md")
    parser.add_argument("--cache", default="data/runs/api_cache.jsonl")
    parser.add_argument("--api-key-path", default="apikey.txt")
    parser.add_argument("--model", default="gpt-4.1-mini")
    parser.add_argument("--split", default="test")
    parser.add_argument("--limit-per-category", type=int, default=2)
    parser.add_argument("--policies", default="api_direct_act,api_ask_needed,api_ecu")
    parser.add_argument(
        "--scene-format",
        choices=["json", "shuffled_json", "natural_language"],
        default="json",
        help="How to serialize the visible scene into API prompts.",
    )
    parser.add_argument("--cache-only", action="store_true", help="Replay from cache and fail on any cache miss without API calls.")
    return parser.parse_args()


def prompt_text(name: str, **values) -> str:
    template = (PROMPT_DIR / name).read_text(encoding="utf-8")
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", str(value))
    return rendered


def scene_json(episode: dict) -> str:
    return scene_text(episode, "json")


def scene_text(episode: dict, scene_format: str) -> str:
    scene = visible_scene(episode)
    if scene_format == "json":
        return json.dumps(scene, sort_keys=True)
    if scene_format == "shuffled_json":
        shuffled = json.loads(json.dumps(scene))
        shuffled["objects"] = list(reversed(shuffled.get("objects", [])))
        return json.dumps(shuffled, sort_keys=True)
    if scene_format == "natural_language":
        return natural_language_scene(scene)
    raise ValueError(f"Unknown scene format: {scene_format}")


def natural_language_scene(scene: dict) -> str:
    rooms = ", ".join(str(room).replace("_", " ") for room in scene.get("rooms", []))
    current_user = scene.get("current_user")
    parts = []
    if rooms:
        parts.append(f"Rooms: {rooms}.")
    if current_user:
        parts.append(f"Current user: {current_user}.")
    object_sentences = []
    for obj in scene.get("objects", []):
        fields = [
            f"id {obj.get('id')}",
            str(obj.get("color", "")).replace("_", " "),
            str(obj.get("state", "")).replace("_", " "),
            str(obj.get("type", "")).replace("_", " "),
            f"owned by {obj.get('owner')}",
            f"at {str(obj.get('location', '')).replace('_', ' ')}",
            "reachable" if obj.get("reachable") else "not reachable",
            f"salience {obj.get('salience')}",
        ]
        object_sentences.append("; ".join(field for field in fields if field and field != "owned by None") + ".")
    if object_sentences:
        parts.append("Objects: " + " ".join(object_sentences))
    return " ".join(parts)


def visible_scene(episode: dict) -> dict:
    scene = json.loads(json.dumps(episode["scene"]))
    for obj in scene.get("objects", []):
        if obj.get("visible_owner") is False:
            obj["owner"] = "unknown"
    return scene


def select_stratified(episodes: list[dict], split: str, limit_per_category: int) -> list[dict]:
    counts: dict[str, int] = {}
    selected = []
    for episode in episodes:
        if episode["split"] != split:
            continue
        category = episode["ambiguity_type"]
        if counts.get(category, 0) >= limit_per_category:
            continue
        selected.append(episode)
        counts[category] = counts.get(category, 0) + 1
    return selected


def coerce_action(obj: dict) -> dict:
    if obj.get("type") == "ACT":
        return {"type": "ACT", "action": str(obj.get("action", "")), "target_id": str(obj.get("target_id", ""))}
    return {"type": "ACT", "action": "invalid", "target_id": "invalid"}


def candidate_to_action(candidate: dict) -> dict:
    return {"type": "ACT", "action": str(candidate.get("action", "")), "target_id": str(candidate.get("target_id", ""))}


def api_equivalence_allowed(episode: dict) -> bool:
    instruction = episode["user_instruction"].lower()
    if any(cue in instruction for cue in [" spare ", " any ", " a spare ", " one of "]):
        return True
    objects = {obj["id"]: obj for obj in episode["scene"]["objects"]}
    candidate_objects = [objects.get(intent["target_id"], {}) for intent in episode["candidate_intents"]]
    return bool(candidate_objects) and all(obj.get("state") == "spare" for obj in candidate_objects)


def api_direct_act(client: CachedResponsesClient, episode: dict, scene_format: str) -> tuple[dict, dict]:
    prompt = prompt_text("direct_act.txt", scene_json=scene_text(episode, scene_format), instruction=episode["user_instruction"])
    parsed, meta = client.complete_json(prompt, max_output_tokens=160)
    return coerce_action(parsed), {"raw_first": parsed, "api": meta}


def api_ask_needed_first(client: CachedResponsesClient, episode: dict, scene_format: str = "json") -> tuple[dict, dict]:
    prompt = prompt_text("ask_when_needed.txt", scene_json=scene_text(episode, scene_format), instruction=episode["user_instruction"])
    parsed, meta = client.complete_json(prompt, max_output_tokens=200)
    if parsed.get("type") == "ASK":
        return {"type": "ASK", "question": str(parsed.get("question", ""))}, {"raw_first": parsed, "api": meta}
    return coerce_action(parsed), {"raw_first": parsed, "api": meta}


def api_ask_needed_cot_first(client: CachedResponsesClient, episode: dict, scene_format: str) -> tuple[dict, dict]:
    prompt = prompt_text("ask_when_needed_cot.txt", scene_json=scene_text(episode, scene_format), instruction=episode["user_instruction"])
    parsed, meta = client.complete_json(prompt, max_output_tokens=240)
    if parsed.get("type") == "ASK":
        return {"type": "ASK", "question": str(parsed.get("question", ""))}, {"raw_first": parsed, "api": meta}
    return coerce_action(parsed), {"raw_first": parsed, "api": meta}


def api_act_after_answer(
    client: CachedResponsesClient,
    episode: dict,
    question: str,
    answer: str,
    scene_format: str,
) -> tuple[dict, dict]:
    prompt = prompt_text(
        "act_after_answer.txt",
        scene_json=scene_text(episode, scene_format),
        instruction=episode["user_instruction"],
        question=question,
        answer=answer,
    )
    parsed, meta = client.complete_json(prompt, max_output_tokens=160)
    return coerce_action(parsed), {"raw_second": parsed, "api_second": meta}


def api_ecu_first(client: CachedResponsesClient, episode: dict, scene_format: str) -> tuple[dict, dict]:
    prompt = prompt_text(
        "candidate_interpretations.txt",
        scene_json=scene_text(episode, scene_format),
        instruction=episode["user_instruction"],
    )
    parsed, meta = client.complete_json(prompt, max_output_tokens=420)
    candidates = parsed.get("candidates", [])
    if not isinstance(candidates, list) or not candidates:
        return api_ask_needed_first(client, episode, scene_format)

    cleaned = []
    total_probability = 0.0
    for idx, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            continue
        probability = float(candidate.get("probability", 0.0) or 0.0)
        probability = max(probability, 0.0)
        total_probability += probability
        cleaned.append(
            {
                "intent_id": f"api_{idx}",
                "target_id": str(candidate.get("target_id", "")),
                "action": str(candidate.get("action", "")),
                "prior": probability,
                "success_equivalence_class": str(candidate.get("target_id", "")),
            }
        )
    if not cleaned:
        return api_ask_needed_first(client, episode, scene_format)
    if total_probability <= 0:
        for c in cleaned:
            c["prior"] = 1.0 / len(cleaned)
    else:
        for c in cleaned:
            c["prior"] = c["prior"] / total_probability

    if parsed.get("candidates_equivalent_for_success") is True and api_equivalence_allowed(episode):
        for c in cleaned:
            c["success_equivalence_class"] = "api_equivalent_success"

    advantage = eu_advantage(cleaned, episode["ask_cost"], episode["wrong_action_cost"])
    best = max(cleaned, key=lambda c: c["prior"])
    context_resolved = parsed.get("context_resolves_instruction") is True
    context_resolved_enough = context_resolved and best["prior"] >= 0.85 and advantage <= 0.20
    if advantage > API_ECU_ASK_MARGIN and not context_resolved_enough:
        question_prompt = prompt_text(
            "generate_question.txt",
            scene_json=scene_text(episode, scene_format),
            instruction=episode["user_instruction"],
            candidate_json=json.dumps(cleaned, sort_keys=True),
        )
        question_obj, question_meta = client.complete_json(question_prompt, max_output_tokens=120)
        question = str(question_obj.get("question", diagnostic_question(episode)))
        return {"type": "ASK", "question": question}, {
            "raw_first": parsed,
            "api": meta,
            "api_candidates": cleaned,
            "api_advantage": advantage,
            "api_ecu_margin": API_ECU_ASK_MARGIN,
            "raw_question": question_obj,
            "api_question": question_meta,
        }

    return candidate_to_action(best), {
        "raw_first": parsed,
        "api": meta,
        "api_candidates": cleaned,
        "api_advantage": advantage,
        "api_ecu_margin": API_ECU_ASK_MARGIN,
        "api_context_resolved_enough": context_resolved_enough,
    }


def run_policy(client: CachedResponsesClient, policy: str, episode: dict, scene_format: str = "json") -> dict:
    debug = {}
    if policy == "api_direct_act":
        first, debug = api_direct_act(client, episode, scene_format)
    elif policy == "api_ask_needed":
        first, debug = api_ask_needed_first(client, episode, scene_format)
    elif policy == "api_ask_needed_cot":
        first, debug = api_ask_needed_cot_first(client, episode, scene_format)
    elif policy == "api_ecu":
        first, debug = api_ecu_first(client, episode, scene_format)
    else:
        raise ValueError(f"Unknown API policy: {policy}")

    asked = first.get("type") == "ASK"
    question = first.get("question") if asked else None
    answer = None
    if asked:
        answer = simulated_user_answer(episode, question or "")
        final, second_debug = api_act_after_answer(client, episode, question or "", answer, scene_format)
        debug.update(second_debug)
    else:
        final = first

    success = action_success(episode, final)
    reward = compute_reward(episode, success=success, asked=asked)
    return {
        "episode_id": episode["episode_id"],
        "split": episode["split"],
        "ambiguity_type": episode["ambiguity_type"],
        "variant": episode["variant"],
        "policy": policy,
        "model": client.model,
        "scene_format": scene_format,
        "asked": asked,
        "question": question,
        "answer": answer,
        "final_action": final,
        "success": success,
        "reward": reward,
        "oracle_should_ask": episode["oracle_should_ask"],
        "ask_cost": episode["ask_cost"],
        "wrong_action_cost": episode["wrong_action_cost"],
        "debug": debug,
    }


def write_summary(rows: list[dict], path: str) -> None:
    table_rows = []
    for policy in sorted({row["policy"] for row in rows}):
        stats = aggregate([row for row in rows if row["policy"] == policy])
        table_rows.append(
            [
                policy,
                str(stats["n"]),
                format_float(stats["net_utility"]),
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["missed_clarification_rate"]),
                format_float(stats["unnecessary_clarification_rate"]),
            ]
        )
    text = "# API Smoke Results\n\n" + markdown_table(
        ["Method", "N", "Net utility", "Success", "Ask rate", "Missed clarif.", "Unnecessary clarif."],
        table_rows,
    )
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    selected = select_stratified(episodes, args.split, args.limit_per_category)
    api_key = "" if args.cache_only else read_api_key(args.api_key_path)
    client = CachedResponsesClient(api_key=api_key, model=args.model, cache_path=args.cache, cache_only=args.cache_only)
    policies = [p.strip() for p in args.policies.split(",") if p.strip()]
    rows = []
    for episode in selected:
        for policy in policies:
            try:
                rows.append(run_policy(client, policy, episode, args.scene_format))
            except (OpenAIAPIError, ValueError, json.JSONDecodeError) as exc:
                rows.append(
                    {
                        "episode_id": episode["episode_id"],
                        "split": episode["split"],
                        "ambiguity_type": episode["ambiguity_type"],
                        "variant": episode["variant"],
                        "policy": policy,
                        "model": client.model,
                        "scene_format": args.scene_format,
                        "asked": False,
                        "question": None,
                        "answer": None,
                        "final_action": {"type": "ACT", "action": "api_error", "target_id": "api_error"},
                        "success": False,
                        "reward": -float(episode["wrong_action_cost"]),
                        "oracle_should_ask": episode["oracle_should_ask"],
                        "ask_cost": episode["ask_cost"],
                        "wrong_action_cost": episode["wrong_action_cost"],
                        "debug": {"error": str(exc)},
                    }
                )
                print(f"API error on {policy}/{episode['episode_id']}: {exc}")
                raise
    write_jsonl(args.out, rows)
    write_summary(rows, args.summary_out)
    print(f"wrote {len(rows)} API smoke rows to {args.out}")
    print(f"wrote summary to {args.summary_out}")


if __name__ == "__main__":
    main()
