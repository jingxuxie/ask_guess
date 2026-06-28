# Additional Experiment Plan for *Ask, Don't Guess*

**Goal:** make the workshop paper stronger by showing that the Clarify-to-Act conclusion is not an artifact of one older API model, one prompt wording, or one small stratified subset.

**Current repo state:** the existing paper has a strong core result: on a 100-episode stratified GPT-4.1-mini API evaluation, `api_ecu` reaches 0.976 net utility and 100% success, while `api_ask_needed` reaches 0.632 utility, misses 58.3% of oracle-ask cases, and asks unnecessarily in 32.7% of oracle-act cases. The repo also has offline diagnostics, a 50-episode style-stress set, a 25-episode GPT-4.1-nano sanity check, component ablations, cost sensitivity, and reproducibility/claim-verification reports.

**Current OpenAI model note, as of June 28, 2026:** official OpenAI API docs list `gpt-5.5` as the flagship model and `gpt-5.4-mini` / `gpt-5.4-nano` as lower-cost, lower-latency variants. The docs list `gpt-5.5` pricing as $5 per input MTok and $30 per output MTok, and `gpt-5.4-mini` pricing as $0.75 per input MTok and $4.50 per output MTok. Check the pricing page again before running the final sweep.

---

## High-level story to prove

The strongest final paper should make this claim:

> Even with stronger current models, asking good clarification questions is not just a matter of detecting ambiguity or prompting the model to “ask when needed.” A utility-calibrated policy is more reliable because it separates three decisions: enumerate plausible intents, compute whether information has value, and ask only when the expected benefit exceeds interaction cost.

The paper becomes much stronger if you can show one of the following:

1. **Robust positive result:** `api_ecu` beats direct prompting across GPT-4.1-mini, GPT-5.4-mini, and GPT-5.5.
2. **Scaling result:** GPT-5.5 improves direct prompting, but `api_ecu` remains better on risk-sensitive, equivalent-outcome, or preference/social slices.
3. **Ceiling result:** GPT-5.5 nearly solves the 100-episode set, but cheaper models still benefit from `api_ecu`, making the method valuable as a low-cost wrapper and diagnostic benchmark.

All three outcomes are publishable if framed honestly.

---

## Priority 1: Current-model sweep

### Research question

Does the Clarify-to-Act result hold for current stronger models, or was the gap specific to GPT-4.1-mini?

### Models

Run the same policies on the same stratified 100-episode subset:

- `gpt-5.5`
- `gpt-5.4-mini`
- `gpt-5.4-nano`, if available in your account
- existing cached `gpt-4.1-mini` as historical baseline
- existing cached `gpt-4.1-nano` as weak-model sanity check

### Policies

Run:

- `api_direct_act`
- `api_ask_needed`
- `api_ask_needed_cot`
- `api_ecu`

The key comparison is `api_ecu - api_ask_needed` within each model, using paired episodes.

### Suggested command pattern

```bash
for model in gpt-5.5 gpt-5.4-mini gpt-5.4-nano; do
  safe_model=$(echo "$model" | tr '.' '_' | tr '-' '_')
  conda run -n ask_dont_guess python src/run_api_experiment.py \
    --episodes data/generated/episodes.jsonl \
    --out data/runs/api_${safe_model}_test100_results.jsonl \
    --summary-out paper/tables/api_${safe_model}_test100_results.md \
    --cache data/runs/api_${safe_model}_cache.jsonl \
    --model $model \
    --split test \
    --limit-per-category 20 \
    --policies api_direct_act,api_ask_needed,api_ask_needed_cot,api_ecu

done
```

Then add or adapt an analysis script that creates one cross-model table:

| Model | Direct utility | Ask-Needed utility | CoT Ask-Needed utility | ECU utility | ECU - AskNeeded | 95% paired CI | ECU missed | ECU unnecessary |
|---|---:|---:|---:|---:|---:|---|---:|---:|

### What to add to the paper

Add a new table in Results:

**Table X: Current-model API sweep.**

Add a paragraph like:

> We rerun the 100-episode stratified API evaluation on current OpenAI models. The utility-calibrated policy remains competitive across model scales. Stronger base models reduce some prompting failures, but the residual failures remain concentrated in the same diagnostic slices: risk-sensitive under-asking and equivalent-outcome over-asking.

Adjust this sentence after seeing the data.

### Interpretation contingencies

If GPT-5.5 direct prompting is still weak:

> This strengthens the paper: even frontier reasoning models need explicit utility calibration for pragmatic ask-or-act decisions.

If GPT-5.5 direct prompting nearly matches ECU:

> This is still useful. Emphasize that Clarify-to-Act detects a capability improved by model scaling, while ECU offers a cheap, interpretable scaffold that lets smaller models approach frontier behavior.

If GPT-5.5 beats ECU:

> Analyze where ECU fails. It may mean model-derived candidate probabilities or equivalence flags need better calibration. This becomes a valuable benchmark result, not a paper failure.

---

## Priority 2: Full 400-episode API test for the strongest two models

### Research question

Does the 100-episode headline result hold on the full canonical test split?

### Recommended scope

Run only the two most important policies on 400 episodes to control cost:

- `api_ask_needed`
- `api_ecu`

Run this for:

- `gpt-5.5`
- `gpt-5.4-mini`

Optional: include `api_direct_act` if budget allows, but direct action is less important because the offline/direct story is already clear.

### Suggested command pattern

`run_api_experiment.py` currently selects `limit_per_category` episodes per category. The test split has 80 episodes per category. Use:

```bash
for model in gpt-5.5 gpt-5.4-mini; do
  safe_model=$(echo "$model" | tr '.' '_' | tr '-' '_')
  conda run -n ask_dont_guess python src/run_api_experiment.py \
    --episodes data/generated/episodes.jsonl \
    --out data/runs/api_${safe_model}_test400_results.jsonl \
    --summary-out paper/tables/api_${safe_model}_test400_results.md \
    --cache data/runs/api_${safe_model}_cache.jsonl \
    --model $model \
    --split test \
    --limit-per-category 80 \
    --policies api_ask_needed,api_ask_needed_cot,api_ecu

done
```

### What this buys you

This is the most reviewer-visible improvement. The current 100-episode result is good, but a reviewer may ask whether the API subset was cherry-picked or too small. A full 400-episode current-model result removes that concern.

### Paper addition

Replace or supplement the main API table with:

| Model | Split | N | Method | Utility | Success | Ask | Missed | Unnecessary |
|---|---|---:|---|---:|---:|---:|---:|---:|

Then keep the 100-episode GPT-4.1-mini result as historical/cost comparison.

---

## Priority 3: Prompt and scene-serialization robustness

### Research question

Is ECU robust because it captures utility, or because the prompt/JSON format accidentally helps it?

### Conditions

For `gpt-5.5` and `gpt-5.4-mini`, run the 100-episode set under:

1. **Original JSON scene**: current setup.
2. **Shuffled object order**: same scene, objects permuted.
3. **Compact natural-language scene**: convert JSON into short text.
4. **Distractor-heavy scene**: add irrelevant objects that are not candidate intents.
5. **Paraphrased prompts**: same policy but with different wording.

### Minimal implementation

Add a `--scene-format` argument to `run_api_experiment.py`:

```bash
--scene-format json
--scene-format shuffled_json
--scene-format natural_language
--scene-format distractors
```

Or create separate generated episode files:

```bash
conda run -n ask_dont_guess python src/make_prompt_robustness_sets.py
```

### Metrics

Report:

- Net utility
- Ask/oracle agreement
- Missed clarification
- Unnecessary clarification
- Category breakdown
- Object-order sensitivity: percent of episodes whose first-turn decision changes under object shuffle

### Strong paper claim

> The ECU wrapper improves not by exploiting one serialization but by preserving the same ask-or-act decision under superficial prompt and scene perturbations.

---

## Priority 4: LLM-simulated user answer robustness

### Research question

Does the benchmark result survive less templated user answers?

The current simulated user is deterministic. That is good for reproducibility, but reviewers may ask whether the second turn is too easy.

### Design

For oracle-ask episodes only, replace the deterministic answer with a model-generated user answer constrained by the hidden intent.

Example prompt:

```text
You are the user. The assistant asked a clarification question.
Answer naturally and briefly, using only information from the hidden intended object.
Do not reveal object IDs. Do not add unrelated preferences.
```

Generate three answer styles:

1. **Direct:** “The one on the kitchen counter.”
2. **Terse:** “Kitchen counter.”
3. **Messy human:** “Oh, the one I was using earlier, on the counter.”

### Recommended models

Use `gpt-5.4-mini` for simulated user answers to control cost. Optionally run a small `gpt-5.5` user-answer set for 50 episodes.

### Metrics

- Post-answer action success
- Answer grounding failure rate
- Question diagnosticity
- Whether ECU still improves first-turn utility

### What to add to the paper

Add a paragraph in Results or Limitations:

> To test whether our conclusions depend on templated answers, we replace deterministic simulated-user replies with model-generated answers in three styles. The first-turn calibration result remains stable; failures, when they occur, are second-turn grounding errors rather than ask-or-act errors.

Again, update after seeing the data.

---

## Priority 5: Human audit, small but high value

### Research question

Are the synthetic labels and generated clarification questions convincing to humans?

### Design

Sample 100 episodes:

- 20 per category
- Include 50 oracle-act and 50 oracle-ask cases
- Blind the annotator to the oracle label

Ask annotators:

1. Is the scene/instruction coherent?
2. Should the agent ask before acting?
3. If a question is shown, is it diagnostic?
4. If the agent acts, is the action acceptable?

### Minimal setup

A simple CSV or Google Form is enough. You can do one author audit plus one outside annotator. Even one external annotator makes the paper stronger than only saying “author audit.”

### Metrics

- Agreement with oracle ask label
- Diagnosticity of ECU questions
- Diagnosticity of Ask-Needed questions
- Category-level disagreements

### Paper language

Do not overclaim. Write:

> A small blinded human audit supports the coherence of the generated scenarios and the diagnosticity of ECU questions, but it is not a replacement for a full user study.

---

## Priority 6: Candidate-probability calibration analysis

### Research question

Does ECU work because the model estimates candidate probabilities well, or because the utility rule is robust to rough probabilities?

### Analysis to add

For API ECU runs, extract `debug.api_candidates` and compare model candidate probabilities to benchmark candidate priors/success classes.

Report:

- Top-candidate match rate
- Expected calibration error over binned top probabilities
- Brier score for hidden success class
- Correlation between model-derived `EU(ask)-EU(act)` and oracle margin
- Ask/oracle agreement as a function of margin size

### Why this matters

A reviewer may say ECU is just using hidden benchmark structure. This analysis shows what the model contributes and where deterministic utility computation takes over.

### Paper claim

> ECU does not require perfectly calibrated probabilities; it mainly needs candidate sets and rough relative plausibility. Most residual risk appears near small utility margins.

Only make this claim if supported.

---

## Priority 7: Counterfactual cost adaptation

### Research question

Can policies adapt when interaction cost or wrong-action cost changes?

The repo already has fixed-output cost sensitivity. Add one adaptive experiment where the model is explicitly told the costs and must make a new ask-or-act decision.

### Conditions

For 100 episodes and `gpt-5.5` / `gpt-5.4-mini`, run:

- ask cost: 0.01, 0.05, 0.20, 0.35
- wrong-action cost: 0.2, 1.0, 3.0

Use a prompt that includes:

```text
Clarification cost: {ask_cost}
Wrong action cost: {wrong_action_cost}
Ask only if the expected value of clarification exceeds its cost.
```

### Metrics

- Ask rate vs oracle ask rate under each cost
- Net utility
- Missed and unnecessary clarification
- Slope of ask rate as ask cost increases
- Slope of ask rate as wrong-action cost increases

### Paper value

This makes the utility story much more direct. It tests whether models can condition on explicit costs, not merely whether fixed outputs remain good under rescoring.

---

## Recommended final experiment set

If time is limited, do only these four:

1. **100-episode current-model sweep**: `gpt-5.5`, `gpt-5.4-mini`, optional `gpt-5.4-nano`.
2. **400-episode full test**: `gpt-5.5` and `gpt-5.4-mini`, only Ask-Needed, CoT Ask-Needed, ECU.
3. **Prompt/scene robustness**: object shuffle + prompt paraphrase on the 100-episode set.
4. **Small human audit**: 100 episodes, one external annotator if possible.

This would make the paper substantially more complete without needing local models or training.

---

## Cost estimate

The current main cache reports about 271k input tokens and 49k output tokens for 914 GPT-4.1-mini responses. If a comparable run uses the same token profile:

- `gpt-5.5`: about 0.271M input × $5 + 0.049M output × $30 ≈ **$2.83**
- `gpt-5.4-mini`: about 0.271M input × $0.75 + 0.049M output × $4.50 ≈ **$0.42**

These are rough estimates, not guarantees. Larger 400-episode sweeps may cost roughly 4× the 100-episode run. With a $100 budget, the recommended experiments are realistic, assuming no unusually long outputs or repeated failed runs.

Cost-saving tips:

- Keep `max_output_tokens` low.
- Use separate cache files per model.
- Run `--limit-per-category 2` smoke tests before 20 or 80.
- Always archive cache files and use `--cache-only` replay for analysis.
- Do not rerun GPT-5.5 when a cached result already exists.

---

## New tables and figures to add

### Table: model sweep

| Model | N | Method | Utility | Success | Ask | Missed | Unnecessary | ECU - AskNeeded |
|---|---:|---|---:|---:|---:|---:|---:|---:|

### Table: full 400-episode current-model evaluation

| Model | Method | N | Utility | 95% CI | Success | Ask | Missed | Unnecessary |
|---|---|---:|---:|---|---:|---:|---:|---:|

### Figure: category failure modes by model

A grouped bar chart with categories on the x-axis and net utility on the y-axis, one bar for Ask-Needed and one for ECU.

### Figure: cost adaptation

Ask rate versus ask cost, with oracle ask rate as a dashed reference line.

### Table: human audit

| Category | N | Oracle/human ask agreement | ECU question diagnostic | Ask-Needed question diagnostic |
|---|---:|---:|---:|---:|

---

## Paper edits after running new experiments

### Abstract

Update the final sentence to mention current models:

> We further show that the result persists across current GPT-5.5/GPT-5.4 model sweeps and prompt perturbations, suggesting that clarification is best evaluated as a situated utility-calibration problem rather than static ambiguity detection.

Only use this wording if the sweep supports it.

### Introduction

Add one sentence:

> We evaluate both historical and current API models to test whether stronger base models solve the ask-or-act decision directly or whether explicit utility calibration remains useful.

### Methods

Add a subsection:

```latex
\paragraph{Current-model sweep.}
We rerun the same cached-evaluable policies with GPT-5.5 and GPT-5.4-mini, using identical episode subsets and paired bootstrap comparisons.
```

### Results

Add:

```latex
\subsection{Does model scaling solve clarification?}
```

Then report the model sweep.

### Limitations

If you only have API models and no local models, say:

> We evaluate hosted API models rather than open-weight local models; this improves relevance to deployed assistants but limits reproducibility of model internals.

---

## Acceptance-oriented checklist

Before submission, make sure the repo has:

- [ ] One command to regenerate the dataset.
- [ ] One command to replay cached API results.
- [ ] One command to reproduce every table in the paper.
- [ ] Claim verification passes after new experiments.
- [ ] No API keys or local paths in the supplement.
- [ ] The abstract numbers exactly match generated tables.
- [ ] The paper does not claim GPT-5.5 results until the sweep is actually run.
- [ ] Limitations clearly state that the environment is synthetic and the user is simulated.
- [ ] The paper explains why ambiguity detection, uncertainty, and clarification utility are different.
