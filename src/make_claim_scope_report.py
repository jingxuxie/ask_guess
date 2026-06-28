from __future__ import annotations

import argparse
import re
from pathlib import Path
from statistics import mean

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--api-cot-results", default="data/runs/api_eval_100_cot_results.jsonl")
    parser.add_argument("--api-style-results", default="data/runs/api_style_stress_50_results.jsonl")
    parser.add_argument("--api-second-model-results", default="data/runs/api_second_model_25_results.jsonl")
    parser.add_argument("--api-gpt54-mini-results", default="data/runs/api_gpt_5_4_mini_test100_results.jsonl")
    parser.add_argument("--api-gpt55-results", default="data/runs/api_gpt_5_5_test100_results.jsonl")
    parser.add_argument("--ambiguity-mix-results", default="data/runs/ambiguity_mix_shift_results.jsonl")
    parser.add_argument("--claim-verification", default="paper/claim_verification.md")
    parser.add_argument("--out", default="paper/claim_scope.md")
    return parser.parse_args()


def stats_for(rows: list[dict], split: str, policy: str) -> dict:
    grouped = group_rows(rows, ("split", "policy"))
    return aggregate(grouped[(split, policy)])


def paired_delta(rows: list[dict], policy_a: str, policy_b: str, split: str = "test") -> float:
    filtered = [row for row in rows if row["split"] == split and row["policy"] in {policy_a, policy_b}]
    by_policy = {
        policy: {row["episode_id"]: float(row["reward"]) for row in filtered if row["policy"] == policy}
        for policy in {policy_a, policy_b}
    }
    shared = sorted(set(by_policy[policy_a]) & set(by_policy[policy_b]))
    return mean(by_policy[policy_a][episode_id] - by_policy[policy_b][episode_id] for episode_id in shared)


def claim_verification_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    match = re.search(r"Overall status:\s+\*\*(PASS|FAIL)\*\*", path.read_text(encoding="utf-8"))
    return match.group(1) if match else "unknown"


def main() -> None:
    args = parse_args()
    offline_rows = read_jsonl(args.offline_results)
    api_rows = read_jsonl(args.api_results)
    cot_rows = read_jsonl(args.api_cot_results)
    style_rows = read_jsonl(args.api_style_results)
    second_rows = read_jsonl(args.api_second_model_results)
    gpt54_rows = read_jsonl(args.api_gpt54_mini_results)
    gpt55_rows = read_jsonl(args.api_gpt55_results)
    ambiguity_mix_rows = read_jsonl(args.ambiguity_mix_results)

    main_direct = stats_for(api_rows, "test", "api_direct_act")
    main_ask = stats_for(api_rows, "test", "api_ask_needed")
    main_ecu = stats_for(api_rows, "test", "api_ecu")
    cot = stats_for(cot_rows, "test", "api_ask_needed_cot")
    style_ask = stats_for(style_rows, "style_test", "api_ask_needed")
    style_ecu = stats_for(style_rows, "style_test", "api_ecu")
    second_ask = stats_for(second_rows, "test", "api_ask_needed")
    second_ecu = stats_for(second_rows, "test", "api_ecu")
    gpt54_ask = stats_for(gpt54_rows, "test", "api_ask_needed")
    gpt54_cot = stats_for(gpt54_rows, "test", "api_ask_needed_cot")
    gpt54_ecu = stats_for(gpt54_rows, "test", "api_ecu")
    gpt55_ask = stats_for(gpt55_rows, "test", "api_ask_needed")
    gpt55_cot = stats_for(gpt55_rows, "test", "api_ask_needed_cot")
    gpt55_ecu = stats_for(gpt55_rows, "test", "api_ecu")
    offline_test_ecu = stats_for(offline_rows, "test", "ecu")
    offline_ood_ecu = stats_for(offline_rows, "ood_test", "ecu")
    ambiguity_mix_ecu = stats_for(ambiguity_mix_rows, "ood_ambiguity_mix", "ecu")
    ambiguity_mix_controller = stats_for(ambiguity_mix_rows, "ood_ambiguity_mix", "learned_controller")
    verification = claim_verification_status(Path(args.claim_verification))

    supported_claim_rows = [
        [
            "Clarification is a utility-sensitive situated decision.",
            "Use as the central thesis.",
            "Ambiguity/utility diagnostic shows all 400 test episodes are surface-ambiguous while only half should ask; situated contrast slices show context, ownership, equivalence, and risk flipping ask/act decisions; cost sweep changes ECU ask rate.",
            "Do not claim that ambiguity detection is useless in all settings.",
        ],
        [
            "ECU improves first-turn net utility over prompted Ask-Needed on the main API set.",
            f"Main result: ECU {format_float(main_ecu['net_utility'])} vs Ask-Needed {format_float(main_ask['net_utility'])}; paired delta {format_float(paired_delta(api_rows, 'api_ecu', 'api_ask_needed'))}.",
            "data/runs/api_eval_100_corrected_results.jsonl; paired bootstrap and subset-stability tables.",
            "Do not describe this as a universal model improvement across tasks.",
        ],
        [
            "The gap is ask timing, not inability to act after useful answers.",
            f"Ask-Needed post-answer success is 1.000 but ask recall is 0.417; ECU ask precision/recall is 1.000/1.000.",
            "paper/tables/api_eval_100_extended/question_usefulness.md",
            "Do not claim open-ended dialogue competence.",
        ],
        [
            "API ECU's model-derived candidate margins align on the main cached API subset.",
            "The candidate-margin threshold agrees with the oracle ask label on 0.990 of rows; final ask/oracle agreement is 1.000 after the effective context override.",
            "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
            "Do not treat this internal cached-row diagnostic as an independent external benchmark.",
        ],
        [
            "API ECU uses rough candidate probabilities rather than perfect hidden-intent calibration.",
            "On the main cached API subset, the model top success class matches the benchmark top-prior class on 0.970 of rows, but the sampled hidden class on 0.770; model and oracle utility margins have Pearson correlation 0.948.",
            "paper/tables/api_candidate_calibration.md",
            "Do not claim the model estimates exact user-intent probabilities.",
        ],
        [
            "Private reasoning alone does not close the calibration gap.",
            f"GPT-4.1-mini CoT Ask-Needed utility {format_float(cot['net_utility'])}; GPT-5.4-mini CoT {format_float(gpt54_cot['net_utility'])} remains below ECU {format_float(gpt54_ecu['net_utility'])}. GPT-5.5 CoT ties ECU on this subset.",
            "data/runs/api_eval_100_cot_results.jsonl; data/runs/api_gpt_5_4_mini_test100_results.jsonl; data/runs/api_gpt_5_5_test100_results.jsonl; paper/tables/current_model_sweep.md",
            "Do not claim all private-reasoning prompts fail or that ECU always beats CoT at frontier scale.",
        ],
        [
            "Current hosted-model sweeps preserve the plain Ask-Needed calibration gap.",
            f"GPT-5.4-mini: ECU {format_float(gpt54_ecu['net_utility'])} vs Ask-Needed {format_float(gpt54_ask['net_utility'])}; GPT-5.5: ECU {format_float(gpt55_ecu['net_utility'])} vs Ask-Needed {format_float(gpt55_ask['net_utility'])}. ECU has zero missed and unnecessary clarifications in both rows.",
            "data/runs/api_gpt_5_4_mini_test100_results.jsonl; data/runs/api_gpt_5_5_test100_results.jsonl; paper/tables/current_model_sweep.md; paper/tables/current_model_category_failure_modes.md",
            "Do not present the 100-episode OpenAI-only sweep as full cross-family or full-test coverage.",
        ],
        [
            "The API utility advantage survives fixed-output reward rescoring.",
            "Cached API outputs keep positive ECU minus Ask-Needed deltas over the tested ask-cost and wrong-action-cost grid; the smallest paired bootstrap lower bound is +0.070.",
            "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
            "Do not claim the API policy was rerun or adaptively retuned under each cost.",
        ],
        [
            "The result survives small paraphrase and answer-style stress.",
            f"Style set ECU {format_float(style_ecu['net_utility'])} vs Ask-Needed {format_float(style_ask['net_utility'])}.",
            "data/runs/api_style_stress_50_results.jsonl",
            "Do not call this broad linguistic robustness.",
        ],
        [
            "A tiny second-model check supports the direction.",
            f"gpt-4.1-nano 25: ECU {format_float(second_ecu['net_utility'])} vs Ask-Needed {format_float(second_ask['net_utility'])}.",
            "data/runs/api_second_model_25_results.jsonl",
            "Do not present this tiny nano check as the main model-robustness evidence.",
        ],
        [
            "The API evidence is reproducible from shipped caches.",
            "Cache-only replay reproduces all 2225 canonical API rows with zero stable-row mismatches.",
            "paper/tables/api_cache_replay_verification.md",
            "Do not present cache replay as a fresh model evaluation.",
        ],
        [
            "The main API advantage is not carried by a single category or episode.",
            "Leave-one-category minimum ECU minus Ask-Needed delta is 0.190; leave-one-episode minimum is 0.307; stratified bootstrap lower bound is 0.183.",
            "paper/tables/api_eval_100_corrected/subset_stability.md",
            "Do not present this as a substitute for a larger paid API sweep.",
        ],
        [
            "The simulated user is visibly diagnostic in the released benchmark.",
            "Generated oracle-ask answers resolve 1233/1233 hidden success classes, and actual API asked-row answers resolve 184/184 from visible scene fields.",
            "paper/tables/simulated_user_audit.md",
            "Do not claim this replaces human-response validation.",
        ],
        [
            "Author-style audits support benchmark and question sanity.",
            "100/100 sampled scenario labels are ok; all audited ECU oracle-ask questions are natural and diagnostic.",
            "paper/audits/AUDIT_SUMMARY.md",
            "Do not call this an independent human-subject study.",
        ],
        [
            "Offline controller and OOD checks support the mechanism.",
            f"Offline ECU test {format_float(offline_test_ecu['net_utility'])}; OOD {format_float(offline_ood_ecu['net_utility'])}; held-out ambiguity-mix ECU {format_float(ambiguity_mix_ecu['net_utility'])}.",
            "data/runs/offline_results.jsonl; robustness, ambiguity-mix, and controller tables.",
            "Do not overstate as real-world deployment robustness.",
        ],
        [
            "The learned controller has a category-transfer boundary.",
            f"With risk-sensitive and preference/social absent from training, learned-controller held-out utility is {format_float(ambiguity_mix_controller['net_utility'])} and ask rate is {format_float(ambiguity_mix_controller['ask_rate'])}.",
            "data/runs/ambiguity_mix_shift_results.jsonl; paper/tables/ambiguity_mix_shift.md",
            "Do not claim the learned controller generalizes to unseen ambiguity types without coverage.",
        ],
        [
            "CLAMBER provides external motivation for clarification calibration.",
            "Provided CLAMBER ambiguity prediction recall is 0.284 against `require_clarification`, with missed clarification rate 0.716.",
            "paper/tables/clamber_external_sanity.md",
            "Do not present this as a Clarify-to-Act method transfer result.",
        ],
    ]

    reviewer_rows = [
        [
            "Synthetic benchmark",
            "High",
            "Frame as controlled diagnostic benchmark; emphasize deterministic rewards and category design.",
            "Do not claim physical robot deployment or real household generalization.",
        ],
        [
            "Model coverage",
            "Medium",
            "Use GPT-4.1-mini as historical headline, GPT-5.4-mini/GPT-5.5 as current hosted-model sweeps, and GPT-4.1-nano as a tiny weak-model sanity check.",
            "Full 400-episode current-model sweeps, open-weight models, multimodal agents, and non-OpenAI model families remain future work.",
        ],
        [
            "Small paid API subset",
            "Medium",
            "Report paired CIs, subset-stability checks, full offline splits, cache-only replay, and style-stress set.",
            "Do not hide that the main API set is 100 episodes.",
        ],
        [
            "Category-shift learning boundary",
            "Medium",
            "Use the held-out ambiguity-mix diagnostic to separate ECU's rule-based transfer from learned-controller over-asking.",
            "Do not present the learned controller as robust to unseen ambiguity categories.",
        ],
        [
            "External CLAMBER sanity check",
            "Low",
            "Use as motivation that query-level ambiguity prediction can miss clarification needs.",
            "Do not claim CLAMBER has situated action rewards or that ECU was evaluated on it.",
        ],
        [
            "Fixed-output API cost sensitivity",
            "Low",
            "Use to show the observed API outputs are not fragile to one reward parameter setting.",
            "Do not imply decisions were recomputed under new costs.",
        ],
        [
            "Simulated user",
            "Medium",
            "State that answers are deterministic, visible-field diagnostic, and enable reproducible first-turn calibration.",
            "Human interaction study is not included.",
        ],
        [
            "ECU uses generated candidate probabilities",
            "Medium",
            "Present as a controller around frozen LLM candidates, with ablations of equivalence safeguards.",
            "Do not imply model weights were trained.",
        ],
        [
            "Action scoring aliases",
            "Low",
            "Document that aliases normalize surface verbs to benchmark actions and are tested.",
            "Do not use overly broad aliases that collapse distinct actions.",
        ],
        [
            "Author audit rather than independent human evaluation",
            "Medium",
            "Use as sanity audit only; keep deterministic metrics as primary evidence.",
            "Do not call it a human study.",
        ],
    ]

    do_not_claim_rows = [
        ["Real-world embodied performance", "No perception, physics, long-horizon planning, or human-in-the-loop deployment is evaluated."],
        ["General dialogue mastery", "Episodes are one ask-or-act decision plus one answer before final action."],
        ["Model training breakthrough", "The learned component is a lightweight controller; API model weights are frozen."],
        ["Broad cross-family model robustness", "The evidence includes GPT-4.1-mini, GPT-5.4-mini, GPT-5.5, and a tiny GPT-4.1-nano check, but no open-weight, multimodal, or non-OpenAI model families."],
        ["Learned-controller category transfer", "When trained without risk-sensitive and preference/social categories, the controller over-asks held-out preference/social cases."],
        ["External benchmark transfer", "CLAMBER analysis uses the dataset's provided ambiguity prediction, not a Clarify-to-Act agent running in CLAMBER."],
        ["Human preference validation", "The user model is deterministic; author audits check coherence and question naturalness."],
    ]

    upgrade_rows = [
        ["Broader model sweep", "Run full 400-episode current-model tests and add open-weight or non-OpenAI model families."],
        ["Human/user study", "Ask humans to answer sampled clarification questions and rate whether questions are necessary."],
        ["External transfer", "Map a small CLAMBER or situated-instruction subset into ask/act utility labels."],
        ["Realistic action backend", "Connect the first-turn ask/act policy to a simulator or tool environment with irreversible actions."],
    ]

    text = "\n".join(
        [
            "# Claim Scope and Reviewer Risk Report",
            "",
            "This generated report is a writing guardrail. It separates claims supported by the current evidence package from claims that would overreach.",
            "",
            "## Status",
            "",
            markdown_table(
                ["Item", "Value"],
                [
                    ["Claim verification", verification],
                    ["Headline API model", "gpt-4.1-mini"],
                    ["Headline API episodes", "100 stratified test episodes"],
                    ["Auxiliary stress evidence", "100-episode GPT-5.4-mini/GPT-5.5 sweeps; 50 style-stress episodes; 25 gpt-4.1-nano episodes; offline held-out ambiguity-mix diagnostic"],
                ],
            ),
            "## Supported Claims",
            "",
            markdown_table(["Safe claim", "Recommended wording", "Evidence", "Avoid"], supported_claim_rows),
            "## Reviewer Risk Register",
            "",
            markdown_table(["Risk", "Severity", "How to frame", "Boundary"], reviewer_rows),
            "## Claims Not Supported",
            "",
            markdown_table(["Do not claim", "Reason"], do_not_claim_rows),
            "## Evidence That Would Upgrade the Claim",
            "",
            markdown_table(["Upgrade", "Concrete next evidence"], upgrade_rows),
        ]
    )
    write_text(args.out, text)
    print(f"wrote claim scope report to {args.out}")


if __name__ == "__main__":
    main()
