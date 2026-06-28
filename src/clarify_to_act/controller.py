from __future__ import annotations

import math

from .environment import action_success, compute_reward


RISK_VALUE = {"low": 0.0, "medium": 0.5, "high": 1.0}


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def featurize(episode: dict) -> list[float]:
    features = episode["features"]
    num_candidates = max(float(features["num_candidates"]), 1.0)
    num_classes = float(features["num_success_classes"])
    entropy = float(features["prior_entropy"])
    max_entropy = math.log(num_candidates) if num_candidates > 1 else 1.0
    return [
        1.0,
        num_candidates / 4.0,
        num_classes / num_candidates,
        float(features["top_prior"]),
        entropy / max(max_entropy, 1e-8),
        float(episode["ask_cost"]) * 10.0,
        float(episode["wrong_action_cost"]) / 3.0,
        float(features["salience_gap"]),
        float(features.get("eu_ask_minus_act", 0.0)),
        1.0 if episode.get("context_resolves_instruction") else 0.0,
        1.0 if episode.get("candidates_equivalent_for_success") else 0.0,
        RISK_VALUE.get(episode.get("risk_level", "medium"), 0.5),
    ]


class LogisticAskController:
    def __init__(self, learning_rate: float = 0.08, epochs: int = 1200, l2: float = 0.001) -> None:
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.l2 = l2
        self.weights: list[float] = []
        self.threshold = 0.5

    def fit(self, train: list[dict], dev: list[dict]) -> None:
        if not train:
            raise ValueError("Need non-empty train episodes")
        width = len(featurize(train[0]))
        self.weights = [0.0 for _ in range(width)]
        for _ in range(self.epochs):
            gradients = [0.0 for _ in range(width)]
            for episode in train:
                x = featurize(episode)
                y = 1.0 if episode["oracle_should_ask"] else 0.0
                pred = sigmoid(sum(w * xi for w, xi in zip(self.weights, x)))
                for j, value in enumerate(x):
                    gradients[j] += (pred - y) * value
            scale = 1.0 / float(len(train))
            for j in range(width):
                regularizer = self.l2 * self.weights[j] if j else 0.0
                self.weights[j] -= self.learning_rate * (gradients[j] * scale + regularizer)
        if dev:
            self.threshold = tune_probability_threshold(self, dev)

    def predict_proba_one(self, episode: dict) -> float:
        if not self.weights:
            raise ValueError("Controller has not been fit")
        x = featurize(episode)
        return sigmoid(sum(w * xi for w, xi in zip(self.weights, x)))

    def should_ask(self, episode: dict) -> bool:
        return self.predict_proba_one(episode) > self.threshold


def decision_reward(episode: dict, ask: bool, act_when_not_asking: dict, act_after_asking: dict) -> float:
    final = act_after_asking if ask else act_when_not_asking
    success = action_success(episode, final)
    return compute_reward(episode, success=success, asked=ask)


def tune_probability_threshold(controller: LogisticAskController, dev: list[dict]) -> float:
    from .environment import act_from_intent, best_intent_by_success_class, choose_intent_after_answer, simulated_user_answer
    from .policies import diagnostic_question

    best_threshold = 0.5
    best_reward = float("-inf")
    candidates = [i / 100.0 for i in range(5, 96, 2)]
    for threshold in candidates:
        total = 0.0
        for episode in dev:
            p_ask = controller.predict_proba_one(episode)
            ask = p_ask > threshold
            act_now = act_from_intent(best_intent_by_success_class(episode))
            question = diagnostic_question(episode)
            answer = simulated_user_answer(episode, question)
            act_later = act_from_intent(choose_intent_after_answer(episode, answer))
            total += decision_reward(episode, ask, act_now, act_later)
        mean_reward = total / max(len(dev), 1)
        if mean_reward > best_reward:
            best_reward = mean_reward
            best_threshold = threshold
    return best_threshold
