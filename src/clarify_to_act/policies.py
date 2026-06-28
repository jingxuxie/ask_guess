from __future__ import annotations

from collections import defaultdict

from .controller import LogisticAskController
from .environment import act_from_intent, best_intent_by_success_class, choose_intent_after_answer
from .generator import eu_advantage


def diagnostic_question(episode: dict) -> str:
    objects = {obj["id"]: obj for obj in episode["scene"]["objects"]}
    candidates = episode["candidate_intents"]
    candidate_objects = [objects[intent["target_id"]] for intent in candidates]
    object_type = candidate_objects[0].get("type", "item") if candidate_objects else "item"
    for key, label in [("state", "which one"), ("location", "where it is"), ("owner", "whose it is")]:
        values = []
        for obj in candidate_objects:
            value = str(obj.get(key, "")).replace("_", " ")
            if value and value not in values:
                values.append(value)
        if len(values) > 1:
            if key == "location":
                return f"Which {object_type} do you mean, and where is it?"
            if key == "owner":
                return f"Which {object_type} do you mean, whose is it?"
            return f"Which {object_type} do you mean, the {' or the '.join(values[:3])} one?"
    return f"Which {object_type} do you mean?"


class Policy:
    name = "policy"

    def fit(self, train: list[dict], dev: list[dict]) -> None:
        return None

    def first_turn(self, episode: dict) -> dict:
        raise NotImplementedError

    def second_turn(self, episode: dict, question: str, answer: str) -> dict:
        return act_from_intent(choose_intent_after_answer(episode, answer))


class DirectActPolicy(Policy):
    name = "direct_act"

    def first_turn(self, episode: dict) -> dict:
        return act_from_intent(best_intent_by_success_class(episode))


class AskAlwaysPolicy(Policy):
    name = "ask_always"

    def first_turn(self, episode: dict) -> dict:
        return {"type": "ASK", "question": diagnostic_question(episode)}


class RawAmbiguityPolicy(Policy):
    name = "raw_ambiguity"

    def first_turn(self, episode: dict) -> dict:
        if len(episode["candidate_intents"]) > 1:
            return {"type": "ASK", "question": diagnostic_question(episode)}
        return act_from_intent(best_intent_by_success_class(episode))


class PromptedHeuristicPolicy(Policy):
    name = "prompted_heuristic"

    def first_turn(self, episode: dict) -> dict:
        features = episode["features"]
        top_prior = float(features["top_prior"])
        # Proxy for a prompted LLM that notices uncertainty but does not get
        # oracle access to utility, equivalence classes, or benchmark labels.
        if top_prior < 0.90:
            return {"type": "ASK", "question": diagnostic_question(episode)}
        return act_from_intent(best_intent_by_success_class(episode))


class ECUPolicy(Policy):
    name = "ecu"

    def first_turn(self, episode: dict) -> dict:
        advantage = eu_advantage(
            episode["candidate_intents"],
            ask_cost=float(episode["ask_cost"]),
            wrong_action_cost=float(episode["wrong_action_cost"]),
        )
        if advantage > 0.0:
            return {"type": "ASK", "question": diagnostic_question(episode)}
        return act_from_intent(best_intent_by_success_class(episode))


class ECUThresholdPolicy(Policy):
    name = "ecu_threshold"

    def __init__(self) -> None:
        self.threshold = 0.0

    def fit(self, train: list[dict], dev: list[dict]) -> None:
        best_threshold = 0.0
        best_reward = float("-inf")
        thresholds = [round(-0.5 + i * 0.025, 3) for i in range(61)]
        tune = dev if dev else train
        for threshold in thresholds:
            total = 0.0
            for episode in tune:
                advantage = eu_advantage(episode["candidate_intents"], episode["ask_cost"], episode["wrong_action_cost"])
                # Tune against expected interaction utility from priors. Using
                # realized hidden intents on a tiny dev set overfits badly.
                total += expected_ask_utility(episode) if advantage > threshold else expected_act_utility(episode)
            reward = total / max(len(tune), 1)
            if reward > best_reward:
                best_reward = reward
                best_threshold = threshold
        self.threshold = best_threshold

    def first_turn(self, episode: dict) -> dict:
        advantage = eu_advantage(episode["candidate_intents"], episode["ask_cost"], episode["wrong_action_cost"])
        if advantage > self.threshold:
            return {"type": "ASK", "question": diagnostic_question(episode)}
        return act_from_intent(best_intent_by_success_class(episode))


class LearnedControllerPolicy(Policy):
    name = "learned_controller"

    def __init__(self) -> None:
        self.controller = LogisticAskController()

    def fit(self, train: list[dict], dev: list[dict]) -> None:
        self.controller.fit(train, dev)

    def first_turn(self, episode: dict) -> dict:
        if self.controller.should_ask(episode):
            return {"type": "ASK", "question": diagnostic_question(episode)}
        return act_from_intent(best_intent_by_success_class(episode))


def make_policies(names: list[str] | None = None) -> list[Policy]:
    all_policies: dict[str, Policy] = {
        "direct_act": DirectActPolicy(),
        "ask_always": AskAlwaysPolicy(),
        "raw_ambiguity": RawAmbiguityPolicy(),
        "prompted_heuristic": PromptedHeuristicPolicy(),
        "ecu": ECUPolicy(),
        "ecu_threshold": ECUThresholdPolicy(),
        "learned_controller": LearnedControllerPolicy(),
    }
    if not names:
        return list(all_policies.values())
    missing = [name for name in names if name not in all_policies]
    if missing:
        raise ValueError(f"Unknown policies: {missing}")
    return [all_policies[name] for name in names]


def success_class_distribution(episode: dict) -> dict[str, float]:
    scores: dict[str, float] = defaultdict(float)
    for intent in episode["candidate_intents"]:
        scores[intent["success_equivalence_class"]] += intent["prior"]
    return dict(scores)


def expected_act_utility(episode: dict) -> float:
    scores = success_class_distribution(episode)
    p_success = max(scores.values())
    return p_success * 1.0 + (1.0 - p_success) * (-float(episode["wrong_action_cost"]))


def expected_ask_utility(episode: dict) -> float:
    return 1.0 - float(episode["ask_cost"])
