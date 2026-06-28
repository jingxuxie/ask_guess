# Ask, Don't Guess: Learning When to Clarify in Situated Instruction Following

## Abstract

Language agents deployed in situated environments must decide not only what an instruction might mean, but whether it is useful to act on that interpretation. Existing ambiguity and clarification evaluations often frame this as a static language-understanding problem: detect ambiguity and ask a question. We argue that clarification is instead a situated decision under uncertainty, interaction cost, and task consequences. We introduce **Clarify-to-Act**, a procedurally generated benchmark in which an agent receives a structured scene and a user instruction, then must either act immediately or ask one clarifying question before acting. The environment provides deterministic rewards based on final task success minus clarification cost, enabling cheap learning from interaction without human labels or model weight updates. In a 100-episode stratified API evaluation with GPT-4.1-mini, a prompted ask-when-needed baseline reaches 0.632 net utility and misses 58.3% of oracle clarification cases, while an expected-communicative-utility policy reaches 0.976 net utility with 100% task success and no missed or unnecessary clarifications. Offline sweeps further show that utility-aware clarification adapts to ask cost and wrong-action cost, whereas ambiguity-driven prompting does not. These results support the view that pragmatic clarification should be evaluated as a utility-calibrated situated policy, not as ambiguity detection alone.

## 1. Introduction

Situated language agents frequently face instructions that are under-specified relative to the action space. A household assistant asked to "bring the red mug" may see two red mugs. A file-management agent asked to "delete the old draft" may see two plausible drafts with very different consequences. In these cases, the agent must decide whether to act immediately or ask a clarifying question.

The standard framing is to ask whether the user query is ambiguous. That framing is incomplete. Some ambiguous instructions are resolved by the environment: if only one cup is reachable on the active workspace, "bring me the cup" should not trigger a question. Some under-specified instructions are harmless because all choices are equivalent: "move a spare chair to the table" does not require identifying a particular spare chair. Other cases are high risk: even a likely interpretation of "delete the old file" may warrant clarification if a wrong deletion is costly.

We study clarification as a situated decision problem. The relevant question is not simply whether language admits multiple interpretations, but whether the expected value of clarification exceeds its interaction cost. This reframes clarification as a policy-level problem around a frozen language model: the system should ask when a question improves expected task utility and act when the environment or outcome structure already makes action sufficient.

This paper makes three contributions.

First, we introduce **Clarify-to-Act**, a lightweight procedural benchmark for ask-or-act decisions in structured scenes. Each episode contains a scene, a natural-language instruction, hidden user intent, candidate intents, a deterministic simulated user, and a task reward.

Second, we define an expected communicative utility objective that provides automatic oracle ask labels and net-utility scores. This objective distinguishes ambiguity that matters from ambiguity that does not.

Third, we evaluate deterministic baselines, lightweight learned controllers, and API-based language-agent policies. The main result is that expected-utility calibration improves net utility by reducing both guessing and unnecessary clarification. The effect appears in both full offline evaluation and a bounded API evaluation.

## 2. Clarify-to-Act Benchmark

### Task

In each episode, an agent observes a structured scene and a user instruction. It must return one of two JSON actions:

```json
{"type": "ACT", "action": "bring", "target_id": "mug_red_dirty_sink"}
```

or:

```json
{"type": "ASK", "question": "Which red mug do you mean?"}
```

If the agent asks, the simulated user returns one deterministic answer generated from the hidden intent, and the agent must then act. The episode is at most two turns.

The LaTeX draft includes an inline task-overview figure showing the full protocol: scene and instruction, first-turn ASK/ACT decision, simulated answer when needed, final action, and deterministic reward minus clarification cost.

### Categories

Clarify-to-Act contains five diagnostic categories.

The generated category table in `paper/tables/benchmark_categories.md` reports 280 episodes per category, oracle ask rates, expected behavior, diagnostic role, and a representative instruction. The LaTeX draft includes the same information as the benchmark category table.

**Referential ambiguity.** Multiple objects match the instruction and wrong target selection matters. The agent should ask.

**Context-resolved underspecification.** Multiple objects exist, but reachability, salience, or explicit context resolves the instruction. The agent should act.

**Equivalent-outcome underspecification.** Multiple choices exist but all satisfy the instruction equally. The agent should act rather than waste a question.

**Risk-sensitive ambiguity.** One interpretation may be likely, but wrong action has high cost. The agent should ask.

**Preference/social ambiguity.** The correct target depends on ownership or preference. If owner information is visible and tied to the current user, the agent should act; if it is hidden, the agent should ask.

The current dataset contains 1,400 episodes: 600 train, 200 dev, 400 test, and 200 out-of-distribution test episodes. The splits are balanced across the five categories, and the overall oracle ask rate is 0.50.

### Reward

The environment computes deterministic reward:

\[
R = \mathbb{1}[\text{success}] - C_{ask}\mathbb{1}[\text{asked}] - C_{wrong}\mathbb{1}[\text{wrong}]
\]

where success is determined by matching the hidden intent's success-equivalence class. This allows equivalent actions to succeed without requiring arbitrary target identity matches.

### Oracle Ask Label

Let \(p_{max}\) be the probability mass of the best success-equivalence class. The expected utility of acting is:

\[
EU(act) = p_{max} \cdot 1 + (1 - p_{max}) \cdot (-C_{wrong})
\]

The expected utility of asking is:

\[
EU(ask) = 1 - C_{ask}
\]

The oracle asks when:

\[
EU(ask) > EU(act) + \epsilon
\]

This label is not a human annotation of ambiguity. It is a task-level decision rule that depends on uncertainty, cost, and outcome equivalence.

### Leakage Fixes

During API smoke testing, the preference/social category exposed possible scene leakage. The final benchmark uses neutral target IDs, redacts hidden object owners from API prompts, gives hidden-owner objects neutral state labels, and includes `current_user` only as user identity rather than as a target hint. Visible-owner cases remain resolvable because owner fields are visible; hidden-owner cases require clarification.

## 3. Methods

### DirectAct

The agent acts immediately and never asks. This measures guessing bias.

### AskAlways

The agent always asks before acting. This measures the cost of indiscriminate clarification.

### Raw Ambiguity

The agent asks whenever more than one candidate target exists. This baseline tests ambiguity detection without utility calibration.

### Prompted Ask-Needed

An API language model receives a prompt instructing it to ask only when acting could plausibly fail. This is the strongest simple prompting baseline.

### Expected Communicative Utility

The ECU policy asks the language model to propose candidate interpretations with probabilities and metadata. Python computes expected utility from the model's candidates, the ask cost, and the wrong-action cost. If the expected utility margin favors asking, the model generates one clarifying question; otherwise, the agent acts on the best candidate.

The final API ECU policy uses a small ask margin of 0.075 to avoid asking on tiny probability tails, a visibility redaction rule for hidden-owner cases, and a conservative equivalence guard so the model can only collapse candidates into one success class when the instruction contains equivalence cues such as "spare" or "any."

### Learned Controller

The offline learned controller is a lightweight logistic ask/act model trained from automatic oracle labels. It uses features such as number of candidates, number of success classes, top prior, entropy, ask cost, wrong-action cost, salience gap, risk, context resolution, equivalence, and expected-utility margin. This studies policy-level learning around frozen language behavior.

## 4. Experiments

We report three groups of experiments.

**Offline benchmark evaluation.** We evaluate deterministic and learned policies on 400 test episodes and 200 OOD episodes. This isolates benchmark mechanics and utility calibration without API noise.

**API evaluation.** We run GPT-4.1-mini on a 100-episode stratified test subset, with 20 episodes per category. We also run a 50-episode paraphrase and answer-style stress set derived from the test split. API calls are cached, and total cached usage is 914 responses, 271,208 input tokens, and 49,117 output tokens.

**Cost sensitivity.** We vary ask cost and wrong-action cost to test whether policies adapt to interaction stakes.

**Reproducibility.** The artifact package includes a generated reproducibility report with dataset/result hashes, recomputed metrics, cache token totals, and exact commands. It also includes automated claim-verification and simulated-user answer audits. The API evaluation can be replayed in cache-only mode, which fails on any cache miss rather than making a network call.

## 5. Results

### Main API Result

The main API result is shown in Figure `paper/figures/api_main_net_utility.svg` and Table 1.

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarification | Unnecessary clarification |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| DirectAct | 100 | 0.420 | [0.180, 0.640] | 0.770 | 0.000 | 1.000 | 0.000 |
| Prompted Ask-Needed | 100 | 0.632 | [0.431, 0.810] | 0.880 | 0.370 | 0.583 | 0.327 |
| API ECU | 100 | 0.976 | [0.972, 0.981] | 1.000 | 0.480 | 0.000 | 0.000 |

DirectAct fails because it never asks, producing low success and high cost in referential and risk-sensitive cases. Prompted Ask-Needed improves over DirectAct but remains poorly calibrated: it misses 58.3% of oracle clarification cases and asks unnecessarily in 32.7% of oracle-act cases. A private-reasoning variant of Ask-Needed does not improve net utility (0.632) and still misses 60.4% of oracle clarification cases. API ECU reaches 0.976 net utility and 100% success, with no missed or unnecessary clarifications in this stratified evaluation. Because all policies run on the same episodes, paired bootstrap deltas are the appropriate comparison: ECU exceeds Ask-Needed by 0.343 net utility with 95% paired CI [0.168, 0.559], and exceeds the private-reasoning variant by 0.344 [0.171, 0.564].

### Category Breakdown

Figure `paper/figures/api_category_net_utility.svg` shows that the ECU advantage is not driven by a single category.

| Category | DirectAct utility | Prompted Ask-Needed utility | API ECU utility | API ECU ask rate | Oracle ask rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Context-resolved | 1.000 | 0.993 | 1.000 | 0.000 | 0.000 |
| Preference/social | 0.400 | 0.400 | 0.980 | 0.400 | 0.400 |
| Equivalent-outcome | 1.000 | 0.920 | 1.000 | 0.000 | 0.000 |
| Referential | -0.100 | 0.857 | 0.950 | 1.000 | 1.000 |
| Risk-sensitive | -0.200 | -0.008 | 0.950 | 1.000 | 1.000 |

Prompted Ask-Needed performs well on referential ambiguity but over-asks equivalent-outcome cases and misses most risk-sensitive cases. ECU asks in all referential and risk-sensitive cases, avoids all context-resolved and equivalent-outcome cases, and matches the oracle ask rate in preference/social cases.

A no-API subset-stability diagnostic further checks the 100-episode result. ECU minus Ask-Needed remains positive after omitting any one category (minimum +0.190) or any one episode (minimum +0.307), and a category-stratified bootstrap gives 95% CI [0.183, 0.541].

### Ambiguity Is Not Enough

A no-API diagnostic isolates the central distinction from raw ambiguity detection. All 400 canonical test episodes have multiple candidate interpretations, but exactly 200 are oracle-act cases and 200 are oracle-ask cases. A surface-ambiguity policy therefore asks on every episode, reaching 0.920 utility with unnecessary clarification rate 1.000. A supervised uncertainty-only controller trained only on candidate count, top prior, and prior entropy reaches 0.900 utility, but still misses 7.0% of oracle-ask cases and asks unnecessarily in 40.0% of oracle-act cases. ECU and the full learned controller reach 0.958 utility while eliminating both missed and unnecessary clarification on the same offline test split.

A situated contrast diagnostic makes the same point at the slice level. Among two-candidate `bring` episodes, all 80 context-resolved cases are oracle-act while all 80 referential cases are oracle-ask. For `put_away` preference episodes, visible ownership gives oracle-act on 40/40 cases, while hidden ownership gives oracle-ask on 40/40. High-entropy equivalent-outcome cases are oracle-act because all candidates share one success class, whereas high-top-prior risk-sensitive cases are oracle-ask because the wrong-action cost is high.

### Utility-Margin Calibration

We bin episodes by the oracle expected-utility margin `EU(ask) - EU(act)`. On the main API set, ECU asks on 0/40 act-preferred episodes and 48/48 ask-preferred episodes. Prompted Ask-Needed asks on 17/40 act-preferred episodes and only 20/48 ask-preferred episodes. On the paraphrase/style stress set, ECU asks on 0/20 act-preferred and 23/23 ask-preferred episodes, while Ask-Needed asks on 7/20 and 12/23. This shows that the prompted baseline is not calibrated to value of information: it asks at similar rates when asking is harmful and when asking is useful.

As an internal cached-row diagnostic, the API ECU's model-derived candidate-margin threshold agrees with the oracle ask label on 99/100 main API rows; after the effective context override, final ask/oracle agreement is 100/100. This supports that the API-side candidate scoring is aligned on the evaluated subset, but it is not an independent benchmark.

### ECU Decision Ablation

We replayed the cached GPT-4.1-mini candidate interpretations from the final API evaluation to isolate the first-turn decision rule without making new API calls. The current rule replay matches actual API ECU ask decisions and rewards on 100/100 episodes. Accepting every model-declared equivalence flag drops utility to 0.745 and misses 37.5% of oracle-ask cases. Never collapsing equivalent candidates keeps success at 100% but raises unnecessary clarification to 38.5%. This supports the conservative equivalence guard: collapse candidates only when the instruction or scene contains explicit equivalence evidence.

### Offline Results

On the full 400-episode test set, ECU and the learned controller reach 0.958 net utility, compared with 0.938 for the prompted heuristic, 0.920 for AskAlways, and 0.498 for DirectAct. On the 200-episode OOD split, ECU reaches 0.975 utility versus 0.955 for the prompted heuristic. The OOD split preserves all five diagnostic categories and shifts object types where supported by the generator; 102 OOD episodes contain at least one held-out object type. On this held-out-object slice, ECU and the learned controller reach 0.975 utility and 100% success, while keeping ask rate at 0.500. This supports the same conclusion without relying on stochastic API behavior.

We also run a no-API held-out ambiguity-mix diagnostic. Train/dev/test episodes contain only referential, context-resolved, and equivalent-outcome cases; the held-out split contains risk-sensitive and preference/social cases. ECU transfers with 0.962 held-out utility, nearly unchanged from 0.963 on the seen-category test split. The tuned threshold and learned controller reach 0.950 but ask on all held-out episodes, over-clarifying visible preference/social cases. This is a useful boundary on the learning claim: the controller is transparent and effective when diagnostic categories are represented, while the expected-utility rule is more stable under this category shift.

As an external query-level sanity check, we map CLAMBER's `require_clarification` field to an ASK label. The benchmark's provided `predict_ambiguous` field has 0.284 recall and 0.716 missed-clarification rate against that label. This is not a situated task-utility result, but it supports the motivation that ambiguity prediction alone can under-identify clarification needs.

### API Paraphrase and Answer-Style Stress

On the 50-episode stress set, API ECU reaches 0.977 net utility and 100% success. Prompted Ask-Needed reaches 0.814 utility, 0.920 success, misses 47.8% of oracle clarification cases, and asks unnecessarily in 25.9% of oracle-act cases. DirectAct reaches 0.320 utility. The paired ECU-minus-Ask-Needed utility difference is +0.163 with 95% CI [0.040, 0.321]. This is a small robustness check, not a broad transfer claim, but it shows that the main API pattern survives paraphrased instructions and shifted user-answer style.

### Cost Sensitivity

Figures `paper/figures/cost_sensitivity_ask_cost.svg` and `paper/figures/cost_sensitivity_wrong_cost.svg` show that ECU adapts to costs while ambiguity-based heuristics do not. When ask cost increases from 0.01 to 0.35 with wrong-action cost fixed at 1.0, ECU ask rate drops from 0.800 to 0.455. The prompted heuristic keeps ask rate fixed at 0.700 and loses utility. When wrong-action cost rises from 0.2 to 3.0 with ask cost fixed at 0.05, DirectAct utility falls from 0.751 to 0.170, while ECU remains near 0.96.

We also re-score the fixed cached API outputs under alternate global costs without rerunning the model. ECU retains a positive paired utility delta over Ask-Needed in all tested settings: +0.201 to +0.239 across the ask-cost sweep and +0.138 to +0.475 across the wrong-action-cost sweep, with all paired bootstrap lower bounds above zero (minimum +0.070). This does not test adaptive retuning, but it shows the main API advantage is not tied to one narrow reward parameterization.

### Author Audit

We audited 100 stratified test scenarios and 100 sampled API clarification questions. All 100 scenario labels were marked coherent with the visible scene, hidden target, and utility oracle. For clarification questions, 73 of 100 were marked `ok`, 19 were marked `minor_issue`, and 8 were marked `bad_question`. All audited ECU questions for oracle-ask cases were natural and diagnostic. The question issues were expected baseline failures: prompted Ask-Needed asked natural but unnecessary questions, or extra non-diagnostic table/preference questions, in oracle-act equivalent-outcome and context-resolved cases.

## 6. Qualitative Analysis

A failure event is any wrong final action or first-turn ask/act decision that disagrees with the utility oracle. This counts successful but unnecessary questions and lucky unsafe guesses as calibration failures. On the main API set plus the private-reasoning baseline, DirectAct has 48 failure events, Ask-Needed has 45, and Ask-Needed with private reasoning has 47; API ECU has 0. The largest failure modes are risk blindness (57 events), equivalence blindness (33), and referential guessing (25). The style-stress set shows the same pattern at smaller scale: DirectAct has 23 events, Ask-Needed has 18, and ECU has 0.

Prompted Ask-Needed exhibits two recurring failure modes.

First, it over-clarifies equivalent-outcome instructions. For example, when asked to "move a spare folder to the table," it often asks which spare folder the user means even though any spare folder succeeds.

Second, it under-clarifies high-risk actions. In several "delete the old file" or "delete the old folder" cases, the prompt baseline acts immediately despite the wrong-action cost being high.

API ECU avoids these failures because its decision rule explicitly compares the value of asking to the value of acting. It does not ask merely because multiple objects exist; it asks when multiple success classes matter and the expected cost of being wrong exceeds the cost of clarification.

## 7. Limitations

Clarify-to-Act is a synthetic text/JSON environment, not a physical simulator. This is intentional: the benchmark isolates ambiguity, context, equivalence, ask cost, and wrong-action cost in a controlled setting. However, the current results do not test perception, long-horizon planning, or real human interaction.

The simulated user answers deterministically from the hidden intent. The released audit verifies that generated oracle-ask answers identify the hidden success class from visible scene fields in 1233/1233 cases, and actual API asked-row answers do so in 184/184 cases. This supports benchmark clarity, but it is not a human-response study and does not capture all variation in human clarification behavior; a small human-response study remains future work.

The API evaluation uses one mini model, a 100-episode main subset, and a 50-episode paraphrase/style stress set. The offline results cover larger generated splits, but claims about general LLM behavior should be expanded with additional models after the paper draft identifies which comparisons matter most.

The learned controller is lightweight and interpretable rather than a model-weight training result. We frame this as policy-level learning from situated interaction outcomes around frozen language models.

## 8. Related Work

Clarification has been studied in question answering, dialogue, and language-agent settings. CLAMBER evaluates whether language models identify and clarify ambiguous information needs, showing that LLMs can struggle with ambiguity detection and calibration. CLAM and value-of-information approaches study when clarification questions improve answer quality. Task-oriented dialogue work studies referential clarification and the form of clarification requests.

Situated instruction following work emphasizes that instructions are grounded in context, environment state, and action consequences. Clarify-to-Act follows this perspective but provides a lightweight diagnostic environment rather than a full embodied simulator. The benchmark is designed to vary the pragmatic variables that determine whether clarification is useful.

Our core distinction is that clarification is not treated as a property of language alone. The same sentence may call for asking or acting depending on salience, outcome equivalence, and stakes.

## 9. Conclusion

Clarification should be evaluated as a situated decision under uncertainty, interaction cost, and task consequences. Clarify-to-Act provides a controlled benchmark for this decision. Across offline and API evaluations, expected communicative utility improves net task utility by asking when clarification changes the expected outcome and acting when it does not. These results suggest that pragmatic clarification is best studied as utility-calibrated interaction policy rather than ambiguity detection alone.

## Artifact Pointers

- Results summary: `RESULTS_SUMMARY.md`
- Claim verification: `paper/claim_verification.md`
- Benchmark category table: `paper/tables/benchmark_categories.md`
- Main API table: `paper/tables/api_eval_100_corrected_results.md`
- API category table: `paper/tables/api_eval_100_corrected/category_breakdown.md`
- Extended API table with private-reasoning baseline: `paper/tables/api_eval_100_extended/main_results.md`
- API style-stress table: `paper/tables/api_style_stress_50/main_results.md`
- Utility-margin calibration: `paper/tables/api_eval_100_corrected/calibration_by_margin.md`
- API ECU candidate-margin diagnostic: `paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md`
- Failure taxonomy: `paper/tables/api_eval_100_extended/failure_taxonomy.md`
- Paired utility differences: `paper/tables/api_eval_100_corrected/paired_differences.md`
- API subset stability: `paper/tables/api_eval_100_corrected/subset_stability.md`
- ECU decision ablation: `paper/tables/api_eval_100_corrected/ecu_ablation.md`
- API utility sensitivity: `paper/tables/api_eval_100_corrected/utility_sensitivity.md`
- API cache replay verification: `paper/tables/api_cache_replay_verification.md`
- Simulated-user answer audit: `paper/tables/simulated_user_audit.md`
- Robustness breakdown: `paper/tables/robustness_breakdown.md`
- Held-out ambiguity-mix diagnostic: `paper/tables/ambiguity_mix_shift.md`
- CLAMBER external sanity check: `paper/tables/clamber_external_sanity.md`
- Figures: `paper/figures/`
- Audit packet: `paper/audits/`
- Reproducibility report: `paper/reproducibility.md`
- Working references: `paper/references.md`
