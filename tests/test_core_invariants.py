from __future__ import annotations

import json
import random
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from clarify_to_act.api_client import CachedResponsesClient, OpenAIAPIError, stable_hash
from clarify_to_act.environment import action_success, compute_reward
from clarify_to_act.generator import (
    EVERYDAY_TYPES,
    HELDOUT_TYPES,
    eu_advantage,
    make_equivalent_outcome,
    make_preference_social,
    make_referential,
    oracle_should_ask,
)
from make_ambiguity_mix_shift import HELDOUT_MAKERS, SEEN_MAKERS, make_split
from clamber_external_sanity import confusion, read_clamber
from api_utility_sensitivity import adjusted_rows as adjusted_api_utility_rows
from make_style_stress_episodes import transform_episode
from run_api_experiment import api_equivalence_allowed, visible_scene


class UtilityDecisionTests(unittest.TestCase):
    def test_oracle_asks_when_uncertainty_is_costly(self) -> None:
        candidates = [
            {"intent_id": "i1", "target_id": "a", "action": "bring", "prior": 0.55, "success_equivalence_class": "a"},
            {"intent_id": "i2", "target_id": "b", "action": "bring", "prior": 0.45, "success_equivalence_class": "b"},
        ]

        self.assertTrue(oracle_should_ask(candidates, ask_cost=0.05, wrong_action_cost=1.0))
        self.assertGreater(eu_advantage(candidates, ask_cost=0.05, wrong_action_cost=1.0), 0.0)

    def test_oracle_does_not_ask_for_equivalent_success_class(self) -> None:
        candidates = [
            {"intent_id": "i1", "target_id": "a", "action": "move", "prior": 0.5, "success_equivalence_class": "any_spare"},
            {"intent_id": "i2", "target_id": "b", "action": "move", "prior": 0.5, "success_equivalence_class": "any_spare"},
        ]

        self.assertFalse(oracle_should_ask(candidates, ask_cost=0.1, wrong_action_cost=0.5))
        self.assertLess(eu_advantage(candidates, ask_cost=0.1, wrong_action_cost=0.5), 0.0)


class EnvironmentInvariantTests(unittest.TestCase):
    def test_equivalent_action_success_allows_interchangeable_target(self) -> None:
        episode = make_equivalent_outcome(2, "test", random.Random(4), EVERYDAY_TYPES)
        hidden = next(intent for intent in episode["candidate_intents"] if intent["intent_id"] == episode["hidden_intent_id"])
        equivalent = next(intent for intent in episode["candidate_intents"] if intent["target_id"] != hidden["target_id"])

        final_action = {"type": "ACT", "action": equivalent["action"], "target_id": equivalent["target_id"]}

        self.assertTrue(action_success(episode, final_action))
        self.assertEqual(compute_reward(episode, success=True, asked=True), 1.0 - episode["ask_cost"])

    def test_wrong_action_reward_uses_episode_cost(self) -> None:
        episode = make_referential(3, "test", random.Random(2), EVERYDAY_TYPES)

        self.assertEqual(compute_reward(episode, success=False, asked=False), -episode["wrong_action_cost"])

    def test_tidy_away_alias_matches_put_away_intent(self) -> None:
        episode = make_preference_social(2, "test", random.Random(0), EVERYDAY_TYPES)
        hidden = next(intent for intent in episode["candidate_intents"] if intent["intent_id"] == episode["hidden_intent_id"])

        final_action = {"type": "ACT", "action": "tidy_away", "target_id": hidden["target_id"]}

        self.assertTrue(action_success(episode, final_action))

    def test_surface_action_aliases_match_ontology(self) -> None:
        bring_episode = make_referential(3, "test", random.Random(2), EVERYDAY_TYPES)
        bring_hidden = next(intent for intent in bring_episode["candidate_intents"] if intent["intent_id"] == bring_episode["hidden_intent_id"])

        self.assertTrue(
            action_success(
                bring_episode,
                {"type": "ACT", "action": "pick up", "target_id": bring_hidden["target_id"]},
            )
        )
        self.assertTrue(
            action_success(
                bring_episode,
                {"type": "ACT", "action": "pickup", "target_id": bring_hidden["target_id"]},
            )
        )
        self.assertTrue(
            action_success(
                bring_episode,
                {"type": "ACT", "action": "bring to current_user", "target_id": bring_hidden["target_id"]},
            )
        )
        self.assertTrue(
            action_success(
                bring_episode,
                {"type": "ACT", "action": "pass to user", "target_id": bring_hidden["target_id"]},
            )
        )
        self.assertTrue(
            action_success(
                bring_episode,
                {"type": "ACT", "action": "pick up and hand over", "target_id": bring_hidden["target_id"]},
            )
        )
        self.assertTrue(
            action_success(
                bring_episode,
                {"type": "ACT", "action": "deliver", "target_id": bring_hidden["target_id"]},
            )
        )

        put_away_episode = make_preference_social(2, "test", random.Random(0), EVERYDAY_TYPES)
        put_away_hidden = next(
            intent for intent in put_away_episode["candidate_intents"] if intent["intent_id"] == put_away_episode["hidden_intent_id"]
        )

        self.assertTrue(
            action_success(
                put_away_episode,
                {
                    "type": "ACT",
                    "action": "move to storage or designated place",
                    "target_id": put_away_hidden["target_id"],
                },
            )
        )

        equivalent_episode = make_equivalent_outcome(6, "test", random.Random(6), EVERYDAY_TYPES)
        equivalent_hidden = next(
            intent
            for intent in equivalent_episode["candidate_intents"]
            if intent["intent_id"] == equivalent_episode["hidden_intent_id"]
        )
        self.assertTrue(
            action_success(
                equivalent_episode,
                {"type": "ACT", "action": "move a spare box to the table", "target_id": equivalent_hidden["target_id"]},
            )
        )


class PreferencePrivacyTests(unittest.TestCase):
    def test_hidden_owner_preference_redacts_objects_and_keeps_neutral_state(self) -> None:
        episode = make_preference_social(1, "test", random.Random(0), EVERYDAY_TYPES)

        self.assertEqual(episode["variant"], "owner_hidden")
        self.assertTrue(all(obj["visible_owner"] is False for obj in episode["scene"]["objects"]))
        self.assertEqual({obj["state"] for obj in episode["scene"]["objects"]}, {"unlabeled"})
        self.assertTrue(all(obj["id"].startswith("pref_") for obj in episode["scene"]["objects"]))
        self.assertFalse(any(owner.lower() in obj["id"].lower() for obj in episode["scene"]["objects"] for owner in ("Alex", "Sam", "Jordan", "Taylor", "Riley", "Morgan")))

        model_scene = visible_scene(episode)
        self.assertEqual({obj["owner"] for obj in model_scene["objects"]}, {"unknown"})

    def test_visible_owner_preference_exposes_current_user(self) -> None:
        episode = make_preference_social(2, "test", random.Random(0), EVERYDAY_TYPES)

        self.assertEqual(episode["variant"], "owner_visible")
        self.assertIn("current_user", episode["scene"])
        self.assertTrue(all(obj["visible_owner"] is True for obj in episode["scene"]["objects"]))
        self.assertIn(episode["scene"]["current_user"], {obj["owner"] for obj in episode["scene"]["objects"]})

    def test_style_stress_transform_preserves_hidden_owner_redaction(self) -> None:
        episode = make_preference_social(1, "test", random.Random(0), EVERYDAY_TYPES)
        transformed = transform_episode(episode)

        self.assertEqual(transformed["hidden_intent_id"], episode["hidden_intent_id"])
        self.assertEqual(transformed["oracle_should_ask"], episode["oracle_should_ask"])
        self.assertNotEqual(transformed["user_instruction"], episode["user_instruction"])
        self.assertTrue(all(obj["visible_owner"] is False for obj in transformed["scene"]["objects"]))
        self.assertEqual({obj["state"] for obj in transformed["scene"]["objects"]}, {"unlabeled"})
        self.assertEqual({obj["owner"] for obj in visible_scene(transformed)["objects"]}, {"unknown"})


class AmbiguityMixShiftTests(unittest.TestCase):
    def test_ambiguity_mix_holds_out_risk_and_preference_categories(self) -> None:
        rng = random.Random(29)
        train = make_split("train", SEEN_MAKERS, 2, rng, EVERYDAY_TYPES, 0)
        heldout = make_split("ood_ambiguity_mix", HELDOUT_MAKERS, 2, rng, HELDOUT_TYPES, 100)

        self.assertEqual(
            {episode["ambiguity_type"] for episode in train},
            {"referential", "context_resolved", "equivalent_outcome"},
        )
        self.assertEqual(
            {episode["ambiguity_type"] for episode in heldout},
            {"risk_sensitive", "preference_social"},
        )
        self.assertTrue(all(episode["split"] == "ood_ambiguity_mix" for episode in heldout))


class CLAMBERExternalSanityTests(unittest.TestCase):
    def test_read_clamber_accepts_double_encoded_jsonl(self) -> None:
        first = {
            "question": "Which account should I use?",
            "require_clarification": 1,
            "predict_ambiguous": 0,
            "category": "MC",
            "subclass": "what",
        }
        second = {
            "question": "What is the capital of France?",
            "require_clarification": 0,
            "predict_ambiguous": 0,
            "category": "FD",
            "subclass": "none",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clamber.jsonl"
            path.write_text(json.dumps(json.dumps(first)) + "\n" + json.dumps(second) + "\n", encoding="utf-8")
            rows = read_clamber(path)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["question"], first["question"])
        stats = confusion(rows)
        self.assertEqual(stats["fn"], 1)
        self.assertEqual(stats["tn"], 1)


class APIUtilitySensitivityTests(unittest.TestCase):
    def test_adjusted_rows_rescore_fixed_api_decisions(self) -> None:
        episode = make_referential(3, "test", random.Random(2), EVERYDAY_TYPES)
        row = {
            "episode_id": episode["episode_id"],
            "split": "test",
            "policy": "api_ask_needed",
            "asked": True,
            "success": False,
            "reward": 0.0,
            "oracle_should_ask": False,
        }

        adjusted = adjusted_api_utility_rows([row], {episode["episode_id"]: episode}, ask_cost=0.2, wrong_action_cost=3.0)[0]

        self.assertTrue(adjusted["asked"])
        self.assertFalse(adjusted["success"])
        self.assertEqual(adjusted["reward"], -3.2)
        self.assertTrue(adjusted["oracle_should_ask"])


class APIReplayTests(unittest.TestCase):
    def test_cache_only_miss_raises_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            client = CachedResponsesClient(
                api_key="",
                model="gpt-4.1-mini",
                cache_path=str(Path(tmp) / "api_cache.jsonl"),
                cache_only=True,
            )
            client._post = lambda body: self.fail("cache-only miss attempted a network call")  # type: ignore[method-assign]

            with self.assertRaises(OpenAIAPIError):
                client.complete_json("Return JSON.", max_output_tokens=42)

    def test_cache_hit_returns_cached_json(self) -> None:
        model = "gpt-4.1-mini"
        prompt = "Return JSON."
        body = {
            "model": model,
            "input": prompt,
            "temperature": 0,
            "max_output_tokens": 42,
            "store": False,
            "text": {"format": {"type": "json_object"}},
        }
        parsed = {"type": "ACT", "action": "bring", "target_id": "x"}
        row = {
            "cache_key": stable_hash(body),
            "model": model,
            "created_at": 0,
            "prompt_hash": stable_hash(prompt),
            "parsed": parsed,
            "output_text": json.dumps(parsed),
            "usage": {},
            "response_id": "cached",
        }

        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "api_cache.jsonl"
            cache_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            client = CachedResponsesClient(api_key="", model=model, cache_path=str(cache_path), cache_only=True)
            client._post = lambda body: self.fail("cache hit attempted a network call")  # type: ignore[method-assign]

            returned, meta = client.complete_json(prompt, max_output_tokens=42)

        self.assertEqual(returned, parsed)
        self.assertEqual(meta["response_id"], "cached")

    def test_api_equivalence_guard_requires_equivalence_cue(self) -> None:
        referential = make_referential(5, "test", random.Random(5), EVERYDAY_TYPES)
        equivalent = make_equivalent_outcome(6, "test", random.Random(6), EVERYDAY_TYPES)

        self.assertFalse(api_equivalence_allowed(referential))
        self.assertTrue(api_equivalence_allowed(equivalent))


if __name__ == "__main__":
    unittest.main()
