from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Callable


COLORS = ["red", "blue", "green", "white", "black", "yellow"]
OWNERS = ["Alex", "Sam", "Jordan", "Taylor", "Riley", "Morgan"]
ROOMS = ["kitchen", "living_room", "office", "bedroom", "hallway"]
SURFACES = ["sink", "table", "counter", "shelf", "desk", "cabinet"]
EVERYDAY_TYPES = ["mug", "cup", "bowl", "book", "box", "folder"]
HELDOUT_TYPES = ["charger", "keys", "remote", "notebook", "water_bottle"]


def humanize(value: str) -> str:
    return value.replace("_", " ")


def normalize(probs: list[float]) -> list[float]:
    total = sum(probs)
    return [p / total for p in probs]


def entropy(probs: list[float]) -> float:
    return -sum(p * math.log(max(p, 1e-12)) for p in probs)


def oracle_should_ask(candidate_intents: list[dict], ask_cost: float, wrong_action_cost: float, epsilon: float = 0.0) -> bool:
    class_probs: dict[str, float] = defaultdict(float)
    for intent in candidate_intents:
        class_probs[intent["success_equivalence_class"]] += intent["prior"]
    p_best = max(class_probs.values())
    eu_act = p_best * 1.0 + (1.0 - p_best) * (-wrong_action_cost)
    eu_ask = 1.0 - ask_cost
    return eu_ask > eu_act + epsilon


def eu_advantage(candidate_intents: list[dict], ask_cost: float, wrong_action_cost: float) -> float:
    class_probs: dict[str, float] = defaultdict(float)
    for intent in candidate_intents:
        class_probs[intent["success_equivalence_class"]] += intent["prior"]
    p_best = max(class_probs.values())
    eu_act = p_best * 1.0 + (1.0 - p_best) * (-wrong_action_cost)
    eu_ask = 1.0 - ask_cost
    return eu_ask - eu_act


def choose_hidden_intent(candidate_intents: list[dict], rng: random.Random) -> str:
    draw = rng.random()
    cumulative = 0.0
    for intent in candidate_intents:
        cumulative += intent["prior"]
        if draw <= cumulative:
            return intent["intent_id"]
    return candidate_intents[-1]["intent_id"]


def object_record(
    object_id: str,
    object_type: str,
    color: str,
    state: str,
    location: str,
    owner: str,
    salience: float,
    reachable: bool = True,
    visible_owner: bool = True,
) -> dict:
    return {
        "id": object_id,
        "type": object_type,
        "color": color,
        "state": state,
        "location": location,
        "owner": owner,
        "salience": round(salience, 3),
        "reachable": reachable,
        "visible_owner": visible_owner,
    }


def candidate(intent_id: str, target: dict, action: str, prior: float, success_class: str) -> dict:
    return {
        "intent_id": intent_id,
        "target_id": target["id"],
        "action": action,
        "prior": round(prior, 4),
        "success_equivalence_class": success_class,
    }


def answer_map_for_target(target: dict) -> dict:
    state = humanize(target["state"])
    location = humanize(target["location"])
    owner = target["owner"]
    return {
        "default": f"the {state} one in the {location}",
        "state": f"the {state} one",
        "location": f"the one in the {location}",
        "owner": f"{owner}'s one",
    }


def finalize_episode(
    episode_id: str,
    split: str,
    ambiguity_type: str,
    variant: str,
    scene: dict,
    instruction: str,
    candidate_intents: list[dict],
    ask_cost: float,
    wrong_action_cost: float,
    rng: random.Random,
    context_resolves_instruction: bool = False,
    candidates_equivalent_for_success: bool = False,
    risk_level: str = "medium",
) -> dict:
    # Keep priors normalized after rounding-resistant template authoring.
    probs = normalize([float(c["prior"]) for c in candidate_intents])
    for c, p in zip(candidate_intents, probs):
        c["prior"] = round(p, 4)

    hidden_intent_id = choose_hidden_intent(candidate_intents, rng)
    target_by_id = {obj["id"]: obj for obj in scene["objects"]}
    intent_by_id = {intent["intent_id"]: intent for intent in candidate_intents}
    hidden_target = target_by_id[intent_by_id[hidden_intent_id]["target_id"]]
    oracle_answers = answer_map_for_target(hidden_target)
    probs = [c["prior"] for c in candidate_intents]
    top = max(probs)
    saliences = sorted((obj["salience"] for obj in scene["objects"]), reverse=True)
    salience_gap = saliences[0] - saliences[1] if len(saliences) > 1 else 1.0
    should_ask = oracle_should_ask(candidate_intents, ask_cost, wrong_action_cost)

    return {
        "episode_id": episode_id,
        "split": split,
        "ambiguity_type": ambiguity_type,
        "variant": variant,
        "scene": scene,
        "user_instruction": instruction,
        "candidate_intents": candidate_intents,
        "hidden_intent_id": hidden_intent_id,
        "ask_cost": ask_cost,
        "wrong_action_cost": wrong_action_cost,
        "oracle_should_ask": should_ask,
        "oracle_clarifying_answers": oracle_answers,
        "context_resolves_instruction": context_resolves_instruction,
        "candidates_equivalent_for_success": candidates_equivalent_for_success,
        "risk_level": risk_level,
        "features": {
            "num_candidates": len(candidate_intents),
            "num_success_classes": len({c["success_equivalence_class"] for c in candidate_intents}),
            "top_prior": round(top, 4),
            "prior_entropy": round(entropy(probs), 4),
            "salience_gap": round(salience_gap, 4),
            "eu_ask_minus_act": round(eu_advantage(candidate_intents, ask_cost, wrong_action_cost), 4),
        },
    }


def make_referential(idx: int, split: str, rng: random.Random, object_pool: list[str]) -> dict:
    object_type = rng.choice(object_pool)
    color = rng.choice(COLORS)
    state_a, state_b = rng.sample(["clean", "dirty", "cracked", "new", "old"], 2)
    room_a, room_b = rng.sample(ROOMS, 2)
    loc_a = f"{room_a}_{rng.choice(SURFACES)}"
    loc_b = f"{room_b}_{rng.choice(SURFACES)}"
    owner_a, owner_b = rng.sample(OWNERS, 2)
    obj_a = object_record(f"{object_type}_{color}_{state_a}_{idx}_a", object_type, color, state_a, loc_a, owner_a, 0.54)
    obj_b = object_record(f"{object_type}_{color}_{state_b}_{idx}_b", object_type, color, state_b, loc_b, owner_b, 0.46)
    priors = normalize([rng.uniform(0.48, 0.58), rng.uniform(0.42, 0.52)])
    intents = [
        candidate("i1", obj_a, "bring", priors[0], f"{obj_a['id']}_success"),
        candidate("i2", obj_b, "bring", priors[1], f"{obj_b['id']}_success"),
    ]
    return finalize_episode(
        f"{split}_referential_{idx:06d}",
        split,
        "referential",
        "two_matching_objects",
        {"rooms": sorted({room_a, room_b}), "objects": [obj_a, obj_b]},
        f"Can you bring me the {color} {object_type}?",
        intents,
        ask_cost=0.05,
        wrong_action_cost=1.0,
        rng=rng,
        risk_level="medium",
    )


def make_context_resolved(idx: int, split: str, rng: random.Random, object_pool: list[str]) -> dict:
    object_type = rng.choice(object_pool)
    color = rng.choice(COLORS)
    active_room = rng.choice(["kitchen", "office", "living_room"])
    storage_room = rng.choice([r for r in ROOMS if r != active_room])
    active = object_record(
        f"{object_type}_{color}_active_{idx}_a",
        object_type,
        color,
        "in_use",
        f"{active_room}_{rng.choice(['table', 'desk', 'counter'])}",
        rng.choice(OWNERS),
        0.96,
        reachable=True,
    )
    stored = object_record(
        f"{object_type}_{color}_stored_{idx}_b",
        object_type,
        color,
        "stored",
        f"{storage_room}_cabinet",
        rng.choice(OWNERS),
        0.04,
        reachable=False,
    )
    intents = [
        candidate("i1", active, "bring", 0.97, f"{active['id']}_success"),
        candidate("i2", stored, "bring", 0.03, f"{stored['id']}_success"),
    ]
    instruction = rng.choice(
        [
            f"Bring me the {object_type}.",
            f"Could you grab the {color} {object_type} from here?",
            f"Pass me the {object_type} I'm using.",
        ]
    )
    return finalize_episode(
        f"{split}_context_{idx:06d}",
        split,
        "context_resolved",
        "active_workspace_salience",
        {"rooms": sorted({active_room, storage_room}), "objects": [active, stored]},
        instruction,
        intents,
        ask_cost=0.15,
        wrong_action_cost=0.2,
        rng=rng,
        context_resolves_instruction=True,
        risk_level="low",
    )


def make_equivalent_outcome(idx: int, split: str, rng: random.Random, object_pool: list[str]) -> dict:
    object_type = rng.choice(["chair", "box", "folder"])
    color = rng.choice(["gray", "white", "black", "brown"])
    room = rng.choice(["office", "living_room", "hallway"])
    objects = []
    for suffix, salience in zip(["a", "b", "c"], [0.36, 0.33, 0.31]):
        objects.append(
            object_record(
                f"spare_{object_type}_{color}_{idx}_{suffix}",
                object_type,
                color,
                "spare",
                f"{room}_{rng.choice(['wall', 'shelf', 'corner'])}_{suffix}",
                rng.choice(OWNERS),
                salience,
            )
        )
    priors = normalize([0.36, 0.33, 0.31])
    intents = [
        candidate(f"i{k+1}", obj, "move", priors[k], f"any_spare_{object_type}_success")
        for k, obj in enumerate(objects)
    ]
    return finalize_episode(
        f"{split}_equivalent_{idx:06d}",
        split,
        "equivalent_outcome",
        "interchangeable_targets",
        {"rooms": [room], "objects": objects},
        f"Move a spare {object_type} to the table.",
        intents,
        ask_cost=0.10,
        wrong_action_cost=0.5,
        rng=rng,
        candidates_equivalent_for_success=True,
        risk_level="low",
    )


def make_risk_sensitive(idx: int, split: str, rng: random.Random, object_pool: list[str]) -> dict:
    object_type = rng.choice(["draft", "file", "folder"])
    color = rng.choice(["blue", "white", "gray"])
    shared_owner, private_owner = rng.sample(OWNERS, 2)
    obj_a = object_record(
        f"old_{object_type}_private_{idx}_a",
        object_type,
        color,
        "old_private",
        f"office_{rng.choice(['desk', 'folder'])}",
        private_owner,
        0.78,
    )
    obj_b = object_record(
        f"old_{object_type}_shared_{idx}_b",
        object_type,
        color,
        "old_shared",
        f"office_{rng.choice(['shelf', 'cabinet'])}",
        shared_owner,
        0.22,
    )
    priors = normalize([rng.uniform(0.75, 0.85), rng.uniform(0.15, 0.25)])
    intents = [
        candidate("i1", obj_a, "delete", priors[0], f"{obj_a['id']}_success"),
        candidate("i2", obj_b, "delete", priors[1], f"{obj_b['id']}_success"),
    ]
    return finalize_episode(
        f"{split}_risk_{idx:06d}",
        split,
        "risk_sensitive",
        "high_wrong_action_cost",
        {"rooms": ["office"], "objects": [obj_a, obj_b]},
        f"Delete the old {object_type}.",
        intents,
        ask_cost=0.05,
        wrong_action_cost=3.0,
        rng=rng,
        risk_level="high",
    )


def make_preference_social(idx: int, split: str, rng: random.Random, object_pool: list[str]) -> dict:
    object_type = rng.choice(["mug", "cup", "notebook", "charger"] if object_pool is HELDOUT_TYPES else ["mug", "cup", "book", "box"])
    color = rng.choice(COLORS)
    owner_a, owner_b = rng.sample(OWNERS, 2)
    visible = idx % 2 == 0
    loc_a = f"{rng.choice(['kitchen', 'office'])}_{rng.choice(['table', 'desk'])}"
    loc_b = f"{rng.choice(['kitchen', 'office'])}_{rng.choice(['counter', 'shelf'])}"
    obj_a = object_record(
        f"pref_{object_type}_{color}_{idx}_a",
        object_type,
        color,
        "personal" if visible else "unlabeled",
        loc_a,
        owner_a,
        0.99 if visible else 0.55,
        visible_owner=visible,
    )
    obj_b = object_record(
        f"pref_{object_type}_{color}_{idx}_b",
        object_type,
        color,
        "guest" if visible else "unlabeled",
        loc_b,
        owner_b,
        0.01 if visible else 0.45,
        visible_owner=visible,
    )
    priors = [0.99, 0.01] if visible else normalize([0.55, 0.45])
    intents = [
        candidate("i1", obj_a, "put_away", priors[0], f"{obj_a['id']}_success"),
        candidate("i2", obj_b, "put_away", priors[1], f"{obj_b['id']}_success"),
    ]
    episode = finalize_episode(
        f"{split}_preference_{idx:06d}",
        split,
        "preference_social",
        "owner_visible" if visible else "owner_hidden",
        {
            "rooms": sorted({loc_a.split("_")[0], loc_b.split("_")[0]}),
            "objects": [obj_a, obj_b],
        },
        f"Put my {object_type} away.",
        intents,
        ask_cost=0.05,
        wrong_action_cost=1.0,
        rng=rng,
        context_resolves_instruction=visible,
        risk_level="medium",
    )
    intent_lookup = {intent["intent_id"]: intent for intent in episode["candidate_intents"]}
    hidden_target_id = intent_lookup[episode["hidden_intent_id"]]["target_id"]
    target_by_id = {obj["id"]: obj for obj in episode["scene"]["objects"]}
    episode["scene"]["current_user"] = target_by_id[hidden_target_id]["owner"]
    return episode


MAKERS: list[Callable[[int, str, random.Random, list[str]], dict]] = [
    make_referential,
    make_context_resolved,
    make_equivalent_outcome,
    make_risk_sensitive,
    make_preference_social,
]


def generate_split(split: str, n: int, rng: random.Random, object_pool: list[str]) -> list[dict]:
    episodes = []
    for idx in range(n):
        maker = MAKERS[idx % len(MAKERS)]
        episodes.append(maker(idx, split, rng, object_pool))
    rng.shuffle(episodes)
    return episodes


def generate_dataset(train: int, dev: int, test: int, ood_test: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    episodes = []
    episodes.extend(generate_split("train", train, rng, EVERYDAY_TYPES))
    episodes.extend(generate_split("dev", dev, rng, EVERYDAY_TYPES))
    episodes.extend(generate_split("test", test, rng, EVERYDAY_TYPES))
    if ood_test:
        episodes.extend(generate_split("ood_test", ood_test, rng, HELDOUT_TYPES))
    return episodes
