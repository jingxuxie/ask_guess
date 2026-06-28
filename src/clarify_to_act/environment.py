from __future__ import annotations


def intent_by_id(episode: dict) -> dict[str, dict]:
    return {intent["intent_id"]: intent for intent in episode["candidate_intents"]}


def object_by_id(episode: dict) -> dict[str, dict]:
    return {obj["id"]: obj for obj in episode["scene"]["objects"]}


def hidden_intent(episode: dict) -> dict:
    return intent_by_id(episode)[episode["hidden_intent_id"]]


def best_intent_by_prior(episode: dict) -> dict:
    return max(episode["candidate_intents"], key=lambda intent: intent["prior"])


def best_intent_by_success_class(episode: dict) -> dict:
    class_scores: dict[str, float] = {}
    class_representatives: dict[str, dict] = {}
    for intent in episode["candidate_intents"]:
        success_class = intent["success_equivalence_class"]
        class_scores[success_class] = class_scores.get(success_class, 0.0) + intent["prior"]
        class_representatives.setdefault(success_class, intent)
    best_class = max(class_scores, key=class_scores.get)
    return class_representatives[best_class]


def action_success(episode: dict, final_action: dict) -> bool:
    if final_action.get("type") != "ACT":
        return False
    target_id = final_action.get("target_id")
    action = normalize_action(final_action.get("action"))
    candidate_by_target = {intent["target_id"]: intent for intent in episode["candidate_intents"]}
    chosen = candidate_by_target.get(target_id)
    if chosen is None:
        return False
    hidden = hidden_intent(episode)
    if action != normalize_action(hidden["action"]):
        return False
    return chosen["success_equivalence_class"] == hidden["success_equivalence_class"]


def normalize_action(action: object) -> str:
    text = str(action or "").strip().lower().replace(" ", "_")
    aliases = {
        "bring": "bring",
        "pass": "bring",
        "grab": "bring",
        "get": "bring",
        "fetch": "bring",
        "hand": "bring",
        "hand_over": "bring",
        "pick_up": "bring",
        "bring_to_current_user": "bring",
        "move": "move",
        "move_to_table": "move",
        "move_to_the_table": "move",
        "relocate": "move",
        "place": "move",
        "place_to_table": "move",
        "place_on_table": "move",
        "put": "move",
        "delete": "delete",
        "remove": "delete",
        "discard": "delete",
        "put_away": "put_away",
        "store": "put_away",
        "move_to_storage": "put_away",
        "move_to_storage_or_designated_place": "put_away",
        "move_to_storage_or_designated_area": "put_away",
        "move_to_designated_place": "put_away",
        "move_to_designated_area": "put_away",
        "put_in_storage": "put_away",
        "tidy": "put_away",
        "tidy_away": "put_away",
        "tidy_up": "put_away",
    }
    return aliases.get(text, text)


def compute_reward(episode: dict, success: bool, asked: bool) -> float:
    reward = 1.0 if success else -float(episode["wrong_action_cost"])
    if asked:
        reward -= float(episode["ask_cost"])
    return round(reward, 6)


def simulated_user_answer(episode: dict, question: str) -> str:
    answers = episode["oracle_clarifying_answers"]
    q = question.lower()
    hidden = hidden_intent(episode)
    target = object_by_id(episode)[hidden["target_id"]]
    owner_is_visible = target.get("visible_owner", True)
    if "where" in q or "location" in q or "room" in q:
        return answers.get("location", answers["default"])
    if not owner_is_visible and not any(cue in q for cue in ["owner", "whose", "belongs", "belonging"]):
        return answers.get("location", answers["default"])
    if "owner" in q or "whose" in q or "belongs" in q or "belonging" in q:
        return answers.get("owner", answers["default"])
    if "clean" in q or "dirty" in q or "old" in q or "new" in q or "state" in q:
        return answers.get("state", answers["default"])
    return answers["default"]


def score_candidate_against_answer(obj: dict, answer: str) -> int:
    answer = answer.lower()
    score = 0
    for key in ("state", "location", "owner", "color", "type"):
        value = str(obj.get(key, "")).replace("_", " ").lower()
        if value and value in answer:
            score += 1
    return score


def choose_intent_after_answer(episode: dict, answer: str) -> dict:
    objects = object_by_id(episode)
    scored = []
    for intent in episode["candidate_intents"]:
        obj = objects[intent["target_id"]]
        scored.append((score_candidate_against_answer(obj, answer), intent["prior"], intent))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    if scored[0][0] <= 0:
        return best_intent_by_success_class(episode)
    return scored[0][2]


def act_from_intent(intent: dict) -> dict:
    return {"type": "ACT", "action": intent["action"], "target_id": intent["target_id"]}
