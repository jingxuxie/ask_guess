# Ask, Don’t Guess: Concrete Plan for a High-Impact LSEI Workshop Paper

Prepared: 2026-06-27  
Target venue: Learning from Situated and Embodied Interaction @ COLM 2026  
Assumptions: no local LLMs available; one NVIDIA 4090 available for ordinary Python/data processing; approximately $100 in API credit.

---

## 0. Recommended paper in one sentence

Build a lightweight situated-instruction environment where an API-based language agent must decide whether to **act immediately** or **ask one clarifying question**, learn a cheap interaction-derived ask/act policy from automatic task-success rewards, and show that **net communicative utility** is a better objective than raw ambiguity detection or “ask whenever uncertain.”

Recommended title:

> **Ask, Don’t Guess: Learning When to Clarify in Situated Instruction Following**

Backup titles:

> **Clarify-to-Act: Communicative Utility for Situated Language Agents**  
> **When Should an Agent Ask? Self-Play Calibration for Clarification in Situated Interaction**  
> **Beyond Ambiguity Detection: Utility-Calibrated Clarification in Embodied Language Tasks**

---

## 1. Core thesis

Most work on clarification treats the problem as: “Is the user query ambiguous?”  
Your paper should instead frame the problem as:

> **A situated agent should ask only when the expected value of clarification exceeds the interaction cost.**

That distinction is important and publishable. In many real interactions, language is underspecified but the environment resolves the intent; in others, the language is ambiguous but all interpretations lead to the same safe action; in others, a seemingly small ambiguity is high-risk and should trigger a question.

The high-impact claim:

> **Clarification is not a binary property of language; it is a situated decision under uncertainty, cost, and task consequences.**

This fits LSEI because the workshop asks how interaction with environments, humans, and agents can provide learning signals for language models, including pragmatic grounding and social signals. The workshop CFP explicitly includes multi-agent interaction, cooperative interaction, and evaluation/objectives for pragmatic reasoning.

---

## 2. Paper contributions

Aim for three crisp contributions.

### Contribution 1: A small but diagnostic benchmark

Introduce **Clarify-to-Act**, a procedurally generated situated-instruction benchmark where an agent receives a scene and a user instruction, then must output either:

```json
{"type": "ASK", "question": "Which red mug do you mean?"}
```

or:

```json
{"type": "ACT", "action": "pick_up", "target_id": "mug_red_dirty"}
```

The environment then gives a deterministic reward based on whether the final action matches the hidden user intent, minus the cost of unnecessary clarification.

### Contribution 2: A utility-based clarification objective

Define an automatic **Expected Communicative Utility** objective:

\[
EU(\text{act}) = p_{\max} \cdot R_{success} + (1-p_{\max}) \cdot R_{wrong}
\]

\[
EU(\text{ask}) = R_{success} - C_{ask}
\]

The oracle asks when:

\[
EU(\text{ask}) > EU(\text{act}) + \epsilon
\]

This gives you labels and a task score without human annotation.

### Contribution 3: A cheap interaction-learning method

Use simulated interaction trajectories to learn a small ask/act controller around an API LLM. This can be done without local LLM training:

1. Generate train scenarios with hidden intents and candidate interpretations.
2. Let baseline agents act or ask.
3. Score trajectories automatically.
4. Learn a lightweight controller or threshold over features such as number of candidate intents, prior entropy, wrong-action cost, ask cost, and contextual disambiguation strength.
5. At test time, the API LLM proposes candidate interpretations/questions, while the learned controller decides whether asking is worth it.

This lets you say you are learning from situated interaction while staying within a small compute/API budget.

---

## 3. Related work positioning

Use this positioning in the intro and related work.

| Prior direction | What it shows | Gap your paper fills |
|---|---|---|
| Ambiguity/clarification benchmarks such as CLAMBER | LLMs struggle to identify and clarify ambiguous user queries; CoT/few-shot can increase overconfidence and only marginally help | Mostly query-level; not grounded in action success or interaction cost |
| Situated Instruction Following | Real-world instructions are ambiguous, context-dependent, and temporally situated | Full embodied tasks are heavy; you provide a cheap controlled diagnostic benchmark |
| Tool/agent clarification work such as “Learning to Ask” / Ask-when-Needed | Agents need to ask under unclear instructions, especially before tool calls | You isolate the pragmatic decision rule and evaluate net task utility under interaction |
| LLM-as-agent evaluation | Many agent scores rely on judges or open-ended outcomes | You use deterministic rewards and only optional judge/human audits |

Suggested citations to include:

- Zhang et al. 2024, **CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in Large Language Models**. ACL 2024. https://aclanthology.org/2024.acl-long.578/
- Min et al. 2024, **Situated Instruction Following**. ECCV 2024. https://arxiv.org/abs/2407.12061
- Qian et al. 2024, **Tell Me More! Towards Implicit User Intention Understanding of Language Model Driven Agents**. https://arxiv.org/abs/2402.09205
- Kuhn et al. 2022, **CLAM: Selective Clarification for Ambiguous Questions with Generative Language Models**. https://arxiv.org/abs/2212.07769
- Rao and Daumé III 2018, **Learning to Ask Good Questions: Ranking Clarification Questions using Neural Expected Value of Perfect Information**. https://arxiv.org/abs/1805.04655
- Madge et al. 2025, **Referential ambiguity and clarification requests: comparing types of clarification requests in task-oriented dialogue**. https://aclanthology.org/2025.crac-1.1/
- LSEI workshop page. https://learning-situated-interaction.github.io/

---

## 4. Concrete environment design

### 4.1 Environment name

Use one of these:

- **Clarify-to-Act** — clear and descriptive.
- **SitAsk** — short, but less self-explanatory.
- **C2A** — good as an acronym after introducing Clarify-to-Act.

I recommend **Clarify-to-Act**.

### 4.2 Task setting

Use a simple text/JSON “household assistant” environment, not a simulator. The 4090 is enough for dataset generation, evaluation, plotting, and maybe running embedding models if needed, but you do not need any local LLM.

Each episode contains:

- a structured scene,
- a natural-language user instruction,
- a hidden true intent,
- a set of candidate intents,
- a simulated user who answers clarifying questions,
- a deterministic reward function.

The agent sees the scene and instruction. It does **not** see the hidden intent or the oracle label.

### 4.3 Scenario JSON schema

```json
{
  "episode_id": "ref_000123",
  "split": "test",
  "ambiguity_type": "referential",
  "scene": {
    "rooms": ["kitchen", "living_room"],
    "objects": [
      {
        "id": "mug_red_dirty_sink",
        "type": "mug",
        "color": "red",
        "state": "dirty",
        "location": "kitchen_sink",
        "owner": "Alex",
        "salience": 0.55
      },
      {
        "id": "mug_red_clean_table",
        "type": "mug",
        "color": "red",
        "state": "clean",
        "location": "living_room_table",
        "owner": "Sam",
        "salience": 0.45
      }
    ]
  },
  "user_instruction": "Can you bring me the red mug?",
  "candidate_intents": [
    {
      "intent_id": "i1",
      "target_id": "mug_red_dirty_sink",
      "action": "bring",
      "prior": 0.55,
      "success_equivalence_class": "dirty_red_mug"
    },
    {
      "intent_id": "i2",
      "target_id": "mug_red_clean_table",
      "action": "bring",
      "prior": 0.45,
      "success_equivalence_class": "clean_red_mug"
    }
  ],
  "hidden_intent_id": "i1",
  "ask_cost": 0.08,
  "wrong_action_cost": 1.0,
  "oracle_should_ask": true,
  "oracle_clarifying_answers": {
    "state": "the dirty one",
    "location": "the one by the sink",
    "owner": "Alex's mug"
  }
}
```

### 4.4 Ambiguity categories

Create 5 main categories, each with 150–400 examples.

#### Category A: Referential ambiguity — should ask

Multiple objects match the instruction and wrong target matters.

Example:

> “Bring me the red mug.”  
> Scene: two red mugs, one clean and one dirty.  
> Correct behavior: ask “Which red mug do you mean?”

#### Category B: Context-resolved ambiguity — should not ask

The phrase is underspecified, but context or salience resolves it.

Example:

> “Bring me the cup.”  
> Scene: one cup is on the active workspace; others are in storage.  
> Correct behavior: act.

This category is important because it prevents trivial “ask whenever ambiguous” systems from winning.

#### Category C: Equivalent-outcome ambiguity — should not ask

Multiple interpretations exist but lead to the same task success.

Example:

> “Move a spare chair to the table.”  
> Scene: three identical spare chairs.  
> Correct behavior: act; asking wastes interaction.

#### Category D: Risk-sensitive ambiguity — should ask

Even moderate ambiguity should trigger clarification because the wrong action is costly.

Example:

> “Delete the old draft.”  
> Scene: two old drafts, one shared and one private.  
> Correct behavior: ask before acting.

#### Category E: Preference/social ambiguity — should ask or infer depending on context

The target depends on owner, social convention, or preference.

Example:

> “Put my mug away.”  
> Scene: two mugs; one owned by the user, one by a guest.  
> If ownership is visible, act. If not, ask.

### 4.5 Train/dev/test sizes

Minimum viable version:

| Split | Episodes | Purpose |
|---:|---:|---|
| Train | 600 | learn threshold/controller; choose few-shot examples |
| Dev | 200 | tune prompts and ask-cost threshold |
| Test | 400 | final reported results |

Stronger version:

| Split | Episodes | Purpose |
|---:|---:|---|
| Train | 2,000 | learn robust controller |
| Dev | 500 | prompt/model selection |
| Test | 1,000 | final results with confidence intervals |
| OOD test | 500 | held-out object types, paraphrases, user styles |

---

## 5. Interaction protocol

The episode is two turns at most.

### Turn 1

Agent receives:

```text
Scene: ...
User instruction: "Can you bring me the red mug?"
You may either ACT or ASK one clarifying question.
Return strict JSON.
```

Agent returns either:

```json
{"type": "ACT", "action": "bring", "target_id": "mug_red_dirty_sink"}
```

or:

```json
{"type": "ASK", "question": "Which red mug do you mean?"}
```

### Turn 2, only if the agent asks

The simulated user answers deterministically using the hidden intent:

```text
User: The dirty one by the sink.
```

The agent then must act:

```json
{"type": "ACT", "action": "bring", "target_id": "mug_red_dirty_sink"}
```

### Reward

Use a simple reward:

\[
R = \mathbb{1}[\text{final action succeeds}] - C_{ask}\mathbb{1}[\text{asked}] - C_{wrong}\mathbb{1}[\text{wrong action}]
\]

Recommended defaults:

- `R_success = +1.0`
- `C_ask = 0.05` for ordinary tasks
- `C_ask = 0.10` for low-stakes tasks
- `C_wrong = 0.5` for low-risk tasks
- `C_wrong = 1.0` for ordinary tasks
- `C_wrong = 3.0` for high-risk tasks

This lets you show that the right ask/act policy depends on **stakes**, not just ambiguity.

---

## 6. Main methods to compare

You need a table of methods that are easy to run and scientifically interpretable.

### Method 1: DirectAct

Prompt the model to act immediately and never ask.

Purpose: measures guessing bias.

Expected behavior: high success on context-resolved cases; poor on true ambiguity and high-risk ambiguity.

### Method 2: AskAlways

Agent always asks one question before acting.

Purpose: measures the cost of over-clarification.

Expected behavior: high final accuracy, lower net utility because it asks unnecessarily.

### Method 3: Prompted Ask-When-Needed

A standard prompt:

```text
Ask a clarifying question only if the instruction is ambiguous and acting could be wrong.
Otherwise act immediately.
```

Purpose: strong simple baseline.

### Method 4: CoT Ask-When-Needed

Same as Method 3, but with private reasoning before producing JSON. Do not include the private reasoning in the final output.

Purpose: tests whether reasoning helps ask/act calibration.

### Method 5: Expected Communicative Utility, zero-shot

Pipeline:

1. API LLM proposes candidate interpretations and rough probabilities.
2. Python computes expected utility of acting vs asking.
3. If asking wins, API LLM generates one targeted question.
4. After simulated user answer, API LLM acts.

This is the main method.

### Method 6: Expected Communicative Utility + learned threshold

Use train episodes to tune a threshold:

\[
\text{ask if } EU(ask) - EU(act) > \tau
\]

Learn `tau` on dev or train using automatic rewards.

This is the minimal “learning from interaction” method.

### Method 7: Lightweight learned ask/act controller

Train a logistic regression or gradient-boosted tree using scenario features:

- number of candidate targets,
- entropy of candidate probabilities,
- top candidate probability,
- ask cost,
- wrong-action cost,
- whether candidates are outcome-equivalent,
- context-salience gap,
- ambiguity category.

The controller chooses ASK vs ACT; the API LLM only generates the natural-language question/action.

This is cheap, transparent, and useful for analysis.

### Optional Method 8: In-context self-play memory

From train trajectories, retrieve 2–4 similar successful examples into the prompt. This gives you a “learning without weights” condition.

Do this only after Methods 1–7 are working.

---

## 7. API-only implementation plan

### 7.1 Use APIs only where needed

No API needed for:

- scenario generation,
- oracle labels,
- simulated user answers,
- reward computation,
- statistics and plotting,
- learned controller training.

API needed for:

- agent decisions,
- candidate interpretation generation,
- final action generation,
- optional paraphrase generation,
- optional LLM audit of question naturalness.

### 7.2 Suggested model allocation

Use a low-cost model for almost everything. Use a stronger model only for small audit sets.

Example allocation:

| Use | Model tier | Calls | Rationale |
|---|---:|---:|---|
| Main agent policies | cheapest capable text model | 10k–50k | many small structured calls |
| Candidate interpretation | cheapest capable text model | 5k–20k | output short JSON |
| Paraphrase/OOD test generation | cheap or mid-tier | 1k–5k | one-time data augmentation |
| Naturalness audit | stronger model | 200–1,000 | not part of main metric |

OpenAI’s public pricing pages currently list GPT-4o mini at $0.15 per 1M input tokens and $0.60 per 1M output tokens, and GPT-4.1 mini at $0.40 per 1M input tokens and $1.60 per 1M output tokens. Check current prices immediately before running.

### 7.3 Approximate cost budget

Conservative run:

- 1,000 test episodes
- 6 policies
- average 2 API calls per policy/episode
- average 900 input tokens + 180 output tokens per call

Total:

- calls: about 12,000
- input tokens: about 10.8M
- output tokens: about 2.16M

Approximate cost:

- With GPT-4o mini pricing: about $2.92
- With GPT-4.1 mini pricing: about $7.78

Large run:

- 2,000 episodes
- 8 policies
- average 3 calls per policy/episode
- average 1,000 input tokens + 200 output tokens per call

Total:

- calls: about 48,000
- input tokens: about 48M
- output tokens: about 9.6M

Approximate cost:

- With GPT-4o mini pricing: about $12.96
- With GPT-4.1 mini pricing: about $34.56

Reserve the rest of the $100 for retries, stronger-model audits, and mistakes.

---

## 8. Metrics

Report both accuracy-like and utility-like metrics.

### Primary metric: net utility

Average reward per episode:

\[
\bar{R} = \frac{1}{N}\sum_i R_i
\]

This should be the headline metric.

### Secondary metrics

| Metric | Definition | Why it matters |
|---|---|---|
| Final task success | final action matches hidden intent/equivalence class | basic competence |
| Ask rate | fraction of episodes where agent asks | detects over-questioning |
| Missed clarification rate | did not ask when oracle says ask | detects guessing |
| Unnecessary clarification rate | asked when oracle says act | detects annoying/helpful tradeoff |
| Question resolution rate | after answer, candidate set becomes uniquely identifiable | question quality |
| Action-after-answer success | success conditional on asking | whether question was useful |
| Calibration error | ask probability vs oracle ask label / EV gap | whether confidence tracks utility |
| Robustness drop | performance loss under paraphrase/user-style shift | generalization |

### Confidence intervals

Use bootstrap confidence intervals over episodes. Because methods are evaluated on the same episodes, also report paired bootstrap differences in net utility.

---

## 9. Experiments

### Experiment 1: Main benchmark results

Question:

> Which policy best balances task success and interaction cost?

Table template:

| Method | Net utility ↑ | Success ↑ | Ask rate ↓/calibrated | Missed clarif. ↓ | Unnecessary clarif. ↓ |
|---|---:|---:|---:|---:|---:|
| DirectAct | | | | | |
| AskAlways | | | | | |
| Prompted Ask-Needed | | | | | |
| CoT Ask-Needed | | | | | |
| ECU zero-shot | | | | | |
| ECU + threshold | | | | | |
| Learned controller | | | | | |

Strong expected pattern, not to be claimed until tested:

- DirectAct: too few questions.
- AskAlways: too many questions.
- Prompted Ask-Needed: better but poorly calibrated.
- ECU/controller: best net utility.

### Experiment 2: By ambiguity category

Question:

> Does the method distinguish genuine ambiguity from context-resolved or outcome-equivalent underspecification?

Figure/table:

| Ambiguity type | DirectAct success | AskAlways utility | ECU utility | Learned controller utility |
|---|---:|---:|---:|---:|
| Referential | | | | |
| Context-resolved | | | | |
| Equivalent-outcome | | | | |
| Risk-sensitive | | | | |
| Preference/social | | | | |

This is likely to be one of your most important analyses.

### Experiment 3: Cost sensitivity

Vary ask cost and wrong-action cost.

Plot:

- x-axis: wrong-action cost or ask cost,
- y-axis: ask rate / net utility,
- lines: Prompted vs ECU vs Learned controller.

Key claim:

> A good clarification policy adapts to stakes; a pure ambiguity detector does not.

### Experiment 4: Robustness under user/scene shift

Create held-out conditions:

1. **Instruction paraphrase:** “bring me the red mug” → “could you grab the red cup-ish mug?”
2. **User answer style:** direct, terse, indirect, over-informative.
3. **Held-out object types:** train on mugs/books/boxes; test on keys/chargers/documents.
4. **Held-out ambiguity mix:** train mostly referential; test risk-sensitive/preference.

Report robustness drop:

\[
\Delta = R_{in\text{-}domain} - R_{OOD}
\]

### Experiment 5: Optional external smoke test on CLAMBER

Do not make this central. Use a small subset to show that your ask/act framing is compatible with existing ambiguity benchmarks.

Possible setup:

- Map each CLAMBER item to ASK vs ANSWER.
- Evaluate whether your prompts/controller ask when the query is ambiguous.
- Report this as a small transfer analysis, not your main contribution.

---

## 10. Figures to include

### Figure 1: Task overview

A simple diagram:

```text
Scene + instruction
       |
       v
Agent chooses: ACT or ASK
       |             |
       |             v
       |        Simulated user answer
       |             |
       v             v
       Final action in environment
       |
       v
Deterministic task reward - interaction cost
```

### Figure 2: Clarification is utility-dependent

Show three examples side by side:

1. ambiguous and should ask,
2. ambiguous but context-resolved and should act,
3. ambiguous but high-risk and should ask.

### Figure 3: Main results bar chart

Net utility by method.

### Figure 4: Calibration/cost curve

Ask rate or net utility as a function of wrong-action cost.

### Table 1: Benchmark categories

Number of examples and description per ambiguity type.

### Table 2: Main quantitative results

Net utility, success, ask rate, missed clarification, unnecessary clarification.

### Table 3: Qualitative examples

One success and one failure per method/category.

---

## 11. Prompt templates

### 11.1 DirectAct prompt

```text
You are a household robot assistant. You will receive a structured scene and a user instruction.
Choose the final action that best satisfies the user.
You must not ask a question.
Return only valid JSON with this schema:
{"type":"ACT", "action": string, "target_id": string}

Scene:
{scene_json}

User instruction:
{instruction}
```

### 11.2 Ask-When-Needed prompt

```text
You are a household robot assistant. You will receive a structured scene and a user instruction.
You may either act immediately or ask exactly one clarifying question.
Ask only when acting now could plausibly fail because the user's intent is under-specified.
Do not ask if the scene context clearly resolves the instruction.
Do not ask if multiple choices are equivalent for task success.
Return only valid JSON.

Allowed schemas:
{"type":"ASK", "question": string}
{"type":"ACT", "action": string, "target_id": string}

Scene:
{scene_json}

User instruction:
{instruction}
```

### 11.3 Candidate interpretation prompt for ECU

```text
List the plausible candidate interpretations of the user's instruction in this scene.
Return only valid JSON.
Each candidate should include target_id, action, probability, and a short reason.
Probabilities must sum to 1.

Schema:
{
  "candidates": [
    {"target_id": string, "action": string, "probability": number, "reason": string}
  ],
  "context_resolves_instruction": boolean,
  "candidates_equivalent_for_success": boolean,
  "risk_level": "low" | "medium" | "high"
}

Scene:
{scene_json}

User instruction:
{instruction}
```

### 11.4 Clarifying question generation prompt

```text
Generate one concise clarifying question that would identify which candidate interpretation the user intends.
The question should be answerable from the user's perspective.
Do not ask multiple questions.
Return only valid JSON:
{"question": string}

Scene:
{scene_json}
Instruction: {instruction}
Candidates: {candidate_json}
```

### 11.5 Act after answer prompt

```text
You asked the user a clarifying question and received an answer.
Choose the final action.
Return only valid JSON:
{"type":"ACT", "action": string, "target_id": string}

Scene:
{scene_json}
Original instruction: {instruction}
Question: {question}
User answer: {answer}
```

---

## 12. Implementation structure

Suggested repository:

```text
clarify-to-act/
  README.md
  requirements.txt
  data/
    raw/
    generated/
    runs/
  src/
    generate_scenarios.py
    environment.py
    oracle.py
    simulated_user.py
    api_client.py
    policies.py
    run_experiment.py
    metrics.py
    train_controller.py
    analyze_results.py
  prompts/
    direct_act.txt
    ask_when_needed.txt
    candidate_interpretations.txt
    generate_question.txt
    act_after_answer.txt
  notebooks/
    01_sanity_checks.ipynb
    02_results.ipynb
  paper/
    figures/
    tables/
```

### 12.1 Core evaluation pseudocode

```python
def run_episode(policy, episode):
    first = policy.first_turn(episode.scene, episode.user_instruction)

    asked = first["type"] == "ASK"

    if asked:
        answer = simulated_user_answer(episode, first["question"])
        final = policy.second_turn(
            episode.scene,
            episode.user_instruction,
            first["question"],
            answer,
        )
    else:
        answer = None
        final = first

    success = environment_success(episode, final)
    reward = compute_reward(
        success=success,
        asked=asked,
        ask_cost=episode.ask_cost,
        wrong_action_cost=episode.wrong_action_cost,
    )

    return {
        "episode_id": episode.episode_id,
        "policy": policy.name,
        "asked": asked,
        "question": first.get("question"),
        "answer": answer,
        "final_action": final,
        "success": success,
        "reward": reward,
        "oracle_should_ask": episode.oracle_should_ask,
    }
```

### 12.2 Oracle ask label pseudocode

```python
def oracle_should_ask(candidate_intents, ask_cost, wrong_action_cost, epsilon=0.0):
    # Collapse equivalent intents: if several candidates lead to the same success class,
    # acting on any member of the best equivalence class is okay.
    class_probs = defaultdict(float)
    for intent in candidate_intents:
        class_probs[intent.success_equivalence_class] += intent.prior

    p_best = max(class_probs.values())
    eu_act = p_best * 1.0 + (1.0 - p_best) * (-wrong_action_cost)
    eu_ask = 1.0 - ask_cost

    return eu_ask > eu_act + epsilon
```

### 12.3 Learned controller pseudocode

```python
from sklearn.linear_model import LogisticRegression

X_train, y_train = featurize(train_episodes), [ep.oracle_should_ask for ep in train_episodes]
controller = LogisticRegression(max_iter=1000)
controller.fit(X_train, y_train)

# At test time:
p_ask = controller.predict_proba(X_test)[:, 1]
ask = p_ask > threshold_tuned_on_dev
```

---

## 13. Paper outline for a 4–8 page submission

### Abstract, 150–200 words

Claim that clarification should be evaluated as a situated decision under costs, not as ambiguity detection alone. Introduce Clarify-to-Act and summarize the main result.

### 1. Introduction, about 1 page

Structure:

1. Real agents must decide when to ask and when to act.
2. Asking is useful but not free.
3. Static ambiguity benchmarks miss task success and interaction cost.
4. You introduce a situated benchmark and utility objective.
5. Your result: utility-based/self-play-calibrated agents outperform direct action, ask-always, and prompted ask-when-needed baselines.

End with contributions.

### 2. Clarify-to-Act Benchmark, 1.5–2 pages

Cover:

- scene representation,
- ambiguity categories,
- interaction protocol,
- simulated user,
- reward function,
- oracle ask label.

Include Figure 1 and Table 1 here.

### 3. Methods, 1–1.5 pages

Describe baselines and your ECU/controller method.

Keep it simple. Do not overclaim model learning if you only tune a controller. Say:

> We study learning at the language-agent policy level: interaction outcomes supervise a lightweight ask/act controller around a frozen API LLM.

### 4. Experiments, 1.5–2 pages

Report:

- main results,
- category breakdown,
- cost-sensitivity,
- robustness.

### 5. Analysis and Discussion, 1 page

Include:

- qualitative examples,
- why direct prompting fails,
- when the controller fails,
- implications for situated interaction learning.

### 6. Limitations, 0.5 page

Mention:

- synthetic text world,
- simplified simulated users,
- no visual perception/robotics,
- no model weight updates unless you add optional fine-tuning,
- human validation is limited or absent.

### 7. Related Work, 0.5–1 page

Keep concise. Focus on CLAMBER, Situated Instruction Following, clarification in QA/agents, and value-of-information style clarification.

---

## 14. Minimum viable submission vs stronger submission

### Minimum viable submission

This is enough for a credible workshop paper:

- 1,000 generated episodes.
- 5 ambiguity categories.
- Baselines: DirectAct, AskAlways, Prompted Ask-Needed, ECU, ECU + threshold.
- Deterministic simulated users.
- Main results + category breakdown + 10 qualitative examples.
- Release generator and prompts.

### Stronger submission

Add:

- learned logistic-regression controller,
- OOD paraphrase/user-style split,
- cost-sensitivity curve,
- small CLAMBER transfer sanity check,
- small human/author audit of 100 generated examples and 100 model questions.

### Stretch, only if everything else is done

Add API fine-tuning on successful ask/act trajectories or use a provider’s hosted fine-tuning. This is not necessary for the workshop paper and may distract from the clean core result.

---

## 15. Concrete sprint plan

Use this as a work checklist.

### Phase 1: Build the benchmark

- [ ] Define object attributes and scene templates.
- [ ] Implement 5 ambiguity categories.
- [ ] Implement hidden intents and candidate priors.
- [ ] Implement oracle ask label using expected utility.
- [ ] Implement deterministic simulated user answers.
- [ ] Generate 50 examples and manually inspect them.
- [ ] Generate final train/dev/test splits.

### Phase 2: Implement baselines

- [ ] DirectAct prompt.
- [ ] AskAlways prompt.
- [ ] Ask-When-Needed prompt.
- [ ] CoT/private-reasoning variant.
- [ ] JSON parsing and retry logic.
- [ ] Caching for all API calls.

### Phase 3: Implement your method

- [ ] Candidate interpretation prompt.
- [ ] ECU calculation in Python.
- [ ] Question generation prompt.
- [ ] Act-after-answer prompt.
- [ ] Threshold tuning on dev.
- [ ] Optional learned controller.

### Phase 4: Run experiments

- [ ] Run small 50-episode smoke test.
- [ ] Fix JSON failures and ambiguous schemas.
- [ ] Run full dev set.
- [ ] Freeze prompts.
- [ ] Run final test set once.
- [ ] Run robustness/OOD split.
- [ ] Save all raw logs.

### Phase 5: Analyze

- [ ] Main results table.
- [ ] Category breakdown table.
- [ ] Cost-sensitivity plot.
- [ ] Ask calibration plot.
- [ ] Qualitative examples.
- [ ] Failure taxonomy.
- [ ] Bootstrap confidence intervals.

### Phase 6: Write paper

- [ ] Write abstract and introduction first.
- [ ] Add benchmark diagram.
- [ ] Add method table.
- [ ] Add main results.
- [ ] Add qualitative examples.
- [ ] Add limitations.
- [ ] Add reproducibility checklist.
- [ ] Create anonymized repository or supplementary zip.

---

## 16. Result narratives you can use depending on what happens

### If ECU/controller wins

Main story:

> Situated clarification should be optimized for net communicative utility. A lightweight interaction-trained controller substantially reduces both guessing and unnecessary questions compared with prompted LLM baselines.

### If Prompted Ask-Needed is surprisingly strong

Main story:

> Even strong prompted agents need utility-aware evaluation: they may match success but still ask too often or fail under cost/risk shifts. The benchmark exposes calibration differences hidden by success-only metrics.

### If all methods perform poorly

Main story:

> Current API LLM agents lack robust clarification calibration. They either guess under true ambiguity or ask when the environment already resolves intent. Clarify-to-Act provides a diagnostic benchmark and a failure taxonomy for situated pragmatic reasoning.

### If AskAlways has the highest success

Main story:

> Task success alone rewards socially inefficient agents. Net utility reveals that indiscriminate clarification is not pragmatic competence.

---

## 17. Failure taxonomy to include

Manually label 50–100 failures into these buckets:

| Failure type | Description | Example |
|---|---|---|
| Guessing under ambiguity | Acts despite multiple plausible targets | chooses one red mug without asking |
| Over-clarification | Asks when context resolves intent | asks which cup when only one is reachable |
| Non-diagnostic question | Question does not distinguish candidates | “Can you clarify?” |
| Multi-question overload | Asks several questions at once | “Which mug and where should I put it?” |
| Bad post-answer grounding | Asks good question but ignores answer | user says dirty one; agent picks clean one |
| Social/risk blindness | Acts despite high wrong-action cost | deletes wrong draft |
| Equivalence blindness | Asks despite candidates being interchangeable | asks which identical spare chair |

This qualitative section can make the paper feel much stronger.

---

## 18. Key reviewer objections and how to preempt them

### “This is synthetic.”

Response:

> Yes. The goal is controlled diagnosis of clarification as a situated decision. The benchmark isolates pragmatic variables—ambiguity, context, action equivalence, ask cost, and wrong-action cost—that are difficult to vary independently in full embodied simulators.

### “This is not model training.”

Response:

> We study learning at the agent-policy level around frozen language models. Interaction outcomes supervise when the agent should query the user, which is a practical and compute-efficient form of learning from situated interaction. The setup can later be used for SFT/RL, but does not require expensive training.

### “Why not just ask whenever ambiguous?”

Response:

> Because ambiguity alone is not the correct objective. Some ambiguous instructions are context-resolved; some are outcome-equivalent; some low-probability ambiguities are high-risk. The right policy depends on expected utility.

### “Why not use LLM-as-judge?”

Response:

> The primary reward is deterministic task success plus interaction cost. LLM/human judgments are only optional audits of question naturalness.

### “Does this transfer to real interaction?”

Response:

> The benchmark is a diagnostic first step. Robustness tests with paraphrases, held-out object types, and user-answer styles evaluate whether policies learn the underlying ask/act principle rather than memorizing templates.

---

## 19. What makes this high-impact

The project is high-impact if you emphasize these points:

1. **Clarification is decision-theoretic, not just linguistic.**  
   The same sentence can require asking or acting depending on context, stakes, and equivalence of outcomes.

2. **Net utility is a better metric than success or ambiguity accuracy alone.**  
   Success-only rewards AskAlways; ambiguity-only rewards over-cautious agents.

3. **Interaction provides cheap supervision.**  
   Simulated user answers and final task success generate labels for ask/act calibration without human annotation or large-scale training.

4. **The benchmark is small, controlled, and reproducible.**  
   Workshop reviewers often appreciate a clear diagnostic benchmark with released code more than an expensive but opaque training result.

5. **It aligns with situated/embodied interaction even without robotics.**  
   The core issue—whether language should trigger action or clarification—appears in robotics, web agents, tool agents, and collaborative assistants.

---

## 20. Concrete abstract draft

> Language agents deployed in situated environments must decide not only what an instruction means, but whether it is safe and useful to act on that interpretation. Existing ambiguity and clarification benchmarks often evaluate this as a static language-understanding problem: detect ambiguity and ask a question. We argue that clarification is instead a situated decision under uncertainty, interaction cost, and task consequences. We introduce Clarify-to-Act, a procedurally generated benchmark in which an agent receives a scene and an underspecified instruction, then must either act immediately or ask one clarifying question before acting. The environment provides deterministic rewards based on final task success minus clarification cost, enabling cheap learning from interaction without human labels or large-scale model training. We compare direct action, ask-always, prompted ask-when-needed, and expected-communicative-utility policies around frozen API language models. Our analysis measures task success, net utility, missed clarification, unnecessary clarification, and robustness under paraphrase and user-answer shifts. Clarify-to-Act shows how communicative success can supervise pragmatic ask/act calibration, and offers a controlled testbed for studying situated interaction as a learning signal for language agents.

---

## 21. Final recommendation

Build **Clarify-to-Act** and write the paper around this question:

> **When should a situated language agent ask a clarifying question rather than act?**

Do not frame the paper as “we trained an LLM.” Frame it as:

> **We introduce a diagnostic interaction objective and show that cheap interaction-derived policies improve pragmatic clarification calibration around frozen LLM agents.**

That is feasible with limited API credit, scientifically clean, and well aligned with the LSEI workshop.
