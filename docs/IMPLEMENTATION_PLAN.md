# Problem 3 — Implementation Plan: Script Continuity Checker

> Status: this is the plan as approved before building. It is kept unchanged below; the differences in the built version are listed here. See `PROBLEM_ANALYSIS.md` for why this problem was chosen.

### As built (differences from this plan)

| Plan | As built | Why |
|---|---|---|
| Step 5 finds candidate conflicts in code; step 6 has an LLM verify each pair | Code selects earlier facts about the characters in each episode; one LLM call per episode returns conflicting fact-ID pairs | Fixed attribute grouping missed paraphrased facts; per-episode checking stays linear in cost |
| Verdict labels CONTRADICTION / PLAUSIBLE_CHANGE / SAME / UNSURE | `is_real_contradiction` (written after the explanation) + `could_be_intentional` | Simpler; dropped self-retracted flags in v2 |
| OpenAI-compatible client | Official `anthropic` SDK (Claude Sonnet 5.5) + Ollama REST for local | Owner chose Sonnet 5.5; no server-side model fallback, so every call uses the configured model |
| `aliases.yaml`, `intentional.yaml`, `prompts/` folder | `_aliases.json` in the input folder; `prompts.py`; intentional-twist suppression not implemented (the UI label covers it) | Time |
| Extraction effort `low` | `medium` | `low` collapsed episode 2 to one fact (v1 result) |
| S1 hand-labelled `gold.json` | `eval/S1_labels.json`: labels on the tool's 57 flags (precision only, no recall) | Full line-by-line gold for 12 episodes not done |
| — | Added: quote snapping to exact script text, recurring-problems grouping, `eval/audit_outputs.py` | Found necessary during evaluation |
| Model comparison, hosted demo | Not done | Out of time / owner's choice of one model |

**One-liner:** Feed in the episode scripts of a microdrama series. Get back a continuity report: every place where one episode contradicts another, with the two quoted lines side by side. A character/fact sheet comes out as a by-product.

---

## 1. Scope

**In scope**
- Text scripts (screenplay or transcript), English, one file per episode or one file split by episode headings.
- Contradiction types: character attributes (age, job, family, relationship), life state (alive/dead, injured, pregnant, married/divorced), knowledge (who knows which secret), names and aliases, timeline order, key possessions or locations.
- A CLI and a minimal Streamlit UI.
- A model that can be swapped with one config value.

**Out of scope (stated in doc as limits)**
- Visual continuity (faces, wardrobe), audio, subtitles timing.
- Auto-fixing the script. We suggest fixes; we don't rewrite.
- Judging story quality, pacing, or hooks.

---

## 2. Architecture

```
 episodes/*.txt
      │
      ▼
 [1] Ingest & split ──────────── code (regex on "EPISODE n" / filenames)
      │  list[Episode{num, text, lines[]}]
      ▼
 [2] Fact extraction ─────────── LLM, one call per episode, strict JSON schema
      │  list[Fact{entity, attribute, value, episode, quote}]
      ▼
 [3] Quote check ─────────────── code: fuzzy-match each quote against the source text
      │  drop/mark facts whose quote isn't in the episode (anti-hallucination)
      ▼
 [4] Fact ledger (series bible) ─ code: normalise names + alias map, group by (entity, attribute)
      │
      ▼
 [5] Candidate conflicts ──────── code: same (entity, attribute), different values, different episodes
      │  bounded pairs, not all-vs-all
      ▼
 [6] Conflict verifier ────────── LLM, one call per candidate: CONTRADICTION / PLAUSIBLE_CHANGE / SAME / UNSURE
      │  must explain + suggest fix
      ▼
 [7] Report ──────────────────── code: report.md + report.json + bible.json, sorted by severity
      │
      ▼
 Human editor: Fix / Intentional twist / Not an issue  (labels saved → feedback data)
```

### Who does what (for the "Approach" lens)
| Step | Done by | Why |
|---|---|---|
| Splitting, normalising, grouping, pairing, quote checks, report | **Code / rules** | Deterministic, free, testable. |
| Reading prose and pulling out facts; judging whether two facts really conflict | **LLM** | Needs language understanding (e.g. "she's been dead for years" vs "Mom called"). |
| Final call: error vs deliberate twist | **Human** | Microdramas rely on intended reversals; the model can't know intent. |

### Key design decisions
- **Quotes are mandatory and checked in code.** Every fact and every flag carries verbatim quotes, and step [3] rejects quotes not found in the source (fuzzy ratio ≥ 0.85). Grounding the LLM this way is the main guard against hallucination.
- **Candidate generation is code, not LLM.** Keeps verifier calls proportional to real conflicts, not to N² episode pairs. This is what makes cost scale.
- **Extraction is per episode.** Small context, so small local models can handle it, and it runs incrementally when a new episode arrives.
- **Attribute vocabulary is fixed** (`age, occupation, relation_to:<X>, status, knows_secret:<X>, location, possession, name/alias, event_time`) so grouping works. Free-text `other` is allowed but only compared by the LLM within the same entity.
- **Alias handling:** extraction returns `aliases`; code merges entities whose names or aliases overlap (case-insensitive, first-name match). An `aliases.yaml` override lets the user fix bad merges.

---

## 3. Technology stack (all free)

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11 | Fast to build. |
| LLM access | **OpenAI-compatible client** (`openai` SDK) pointed at a configurable `BASE_URL` + `MODEL` | One code path for Ollama (local), Groq / Gemini OpenAI-compat endpoint (free tiers), or any API Kuku provides. Model swap = change `.env`. |
| Default model | Ollama `qwen2.5:7b-instruct` or `llama3.1:8b` locally. Fallback is a free-tier hosted model if the laptop is too slow. | Free, offline-capable. |
| Structured output | `pydantic` models + JSON mode, with one retry on a parse failure | Reliable schema. |
| Fuzzy matching | `rapidfuzz` | Quote verification, name matching. |
| UI | `streamlit` (upload files → run → table of flags with label buttons) | Easy demo; free hosting on Streamlit Community Cloud if using a hosted API. |
| Storage | JSON files (prototype); SQLite optional | Simple, rerunnable. |
| Caching | Per-episode extraction cached by hash(text + model + prompt version) | Re-runs are instant; cheap iteration. |

---

## 4. Input / output format

### Input
- A folder: `ep01.txt, ep02.txt, …` **or** one `.txt/.md` file with `EPISODE 1` / `Episode 1:` headings.
- Optional `aliases.yaml` (e.g. `Alexander: [Alex, Mr. Grant]`).
- Optional `intentional.yaml`, a list of known twists to suppress (e.g. "Lily is secretly the CEO's daughter").

### Output (`outputs/<run_id>/`)
- `report.md`: human-readable report, e.g.:

```
## ⚠ HIGH — Ethan's mother: dead vs alive
Ep 3  "My mother died when I was twelve." (ETHAN)
Ep 17 "Mom's flying in tomorrow, she wants to meet you." (ETHAN)
Verdict: CONTRADICTION (confidence 0.86)
Why: Ep 3 states his mother is dead; no resurrection/adoption/step-mother is introduced in between.
Suggested fix: change Ep 17 to "My aunt — she raised me after Mom died."
```
- `report.json`: the same data, machine-readable (for evaluation and integration).
- `bible.json`: per-character facts with episode + quote (useful on its own to writers).
- `run_meta.json`: model, prompt version, timings, token counts, number of facts dropped by the quote check.
- `raw/`: unedited LLM responses (satisfies the "raw outputs" requirement).

---

## 5. Test inputs

Since the Kuku pack is unavailable/confidential, we use:
1. **Series S1, generated drift set:** a 12–15 episode original microdrama drafted episode-by-episode by a free LLM with limited context (this is also our "is the problem real?" experiment). Every true contradiction is hand-labelled in `gold.json`.
2. **Series S2, planted-error set:** a clean, hand-checked ~10-episode script into which we plant **10–15 known contradictions**, spread over types and distances (adjacent episodes vs 8+ apart). `planted.json` records each one.
3. **Series S1-clean / S2-clean:** the same scripts with contradictions removed, used to measure false alarms.
4. **Interview input:** any new script folder. Nothing in the pipeline is tuned to S1/S2 content.

*(All inputs are original, so raw outputs can be published.)*

---

## 6. Evaluation strategy

### Offline (what goes in the doc, from real runs)
| Metric | How |
|---|---|
| **Recall** on planted errors | flagged ∩ planted / planted, broken down by type and by episode distance |
| **Precision** | manually label every flag on S1/S2 as true / false; report the count |
| **False alarms on clean scripts** | flags per 10 episodes on the cleaned versions |
| **Grounding rate** | % of extracted quotes that pass the verbatim check (shows how much the LLM hallucinates) |
| **Cost / speed** | wall-clock time and tokens per episode, per model |
| **Model comparison** (if time allows) | same test set with a local 7–8B model vs a free hosted larger model, which shows why model swapping matters |

Failures are written up individually, e.g. "missed: implied timeline contradiction across 3 episodes" or "false alarm: deliberate lie by a character".

### In production (how we'd know it worked with a real team)
- **Flag acceptance rate:** % of flags the editor marks *Fix*. Target: high enough that editors don't start ignoring the tool (e.g. >50%; to be tuned).
- **Escapes:** continuity errors found *after* video generation or in viewer comments, per show, before vs after adoption.
- **Editor time** for the continuity pass per show, before vs after.
- **Re-generation spend** attributable to script-level continuity errors.
- The *Intentional twist* labels become a growing dataset for tuning prompts and suppression rules.

---

## 7. Build plan (~2.5–3 h)

| # | Task | Time |
|---|---|---|
| 1 | Repo skeleton, `.env` config, LLM client wrapper with JSON retry + cache | 20 min |
| 2 | Ingest/splitter + pydantic schemas | 15 min |
| 3 | Extraction prompt + quote verifier | 30 min |
| 4 | Ledger: alias merge, grouping, candidate pairs | 25 min |
| 5 | Verifier prompt + report writer (md/json) | 25 min |
| 6 | Build test sets S1 (generated) and S2 (planted) + gold labels | 30 min |
| 7 | Eval script (recall / precision / false alarms / cost), run, save raw outputs | 20 min |
| 8 | Streamlit UI (upload → run → table → label buttons) | 20 min |
| 9 | README with run steps; notes for the 2-page doc (incl. AI-tool-got-it-wrong log) | 15 min |

**If time runs short, cut in this order:** Streamlit UI → model comparison → S1 generated set. Keep the CLI, S2 planted set, and the eval script.

### Proposed repo layout
```
continuity_checker/
  config.py        # BASE_URL, MODEL, API_KEY from .env
  llm.py           # OpenAI-compatible client, JSON mode, retry, cache
  ingest.py        # split into episodes
  schemas.py       # Fact, Conflict, Verdict (pydantic)
  extract.py       # step 2 + 3
  ledger.py        # step 4 + 5
  verify.py        # step 6
  report.py        # step 7
  prompts/         # versioned prompt files
cli.py             # python cli.py data/S2 --out outputs/
app.py             # streamlit
eval/evaluate.py   # compares report.json against planted.json/gold.json
data/S1, data/S2   # inputs + gold labels
outputs/           # raw, unedited run outputs
docs/
```

---

## 8. Limitations (to state honestly)
- **Twists vs errors:** the tool can't know authorial intent. Expect false alarms on lies, disguises and amnesia plots, which are staples of the genre. Mitigated by the verifier's `PLAUSIBLE_CHANGE` label and `intentional.yaml`, but not solved.
- **Implicit contradictions** (timeline arithmetic, "it's been 5 years" vs dates) are harder than explicit ones; we expect lower recall there and will measure it.
- **Fixed attribute vocabulary** misses facts outside it.
- **Small local models** extract less reliably. Grounding catches invented quotes, but it can't catch facts the model missed.
- **Alias merging** can wrongly merge two characters who share a first name. The `aliases.yaml` override exists for this.
- **Synthetic test data:** our planted errors may be easier than real ones. We'll say so; the S1 generated set is partly there to address this.
- **Text only**, English only.

---

## 9. How it scales in production
- **Incremental:** when episode N arrives, extract only N and compare against the stored ledger. Cost is linear in episodes, not quadratic.
- **Parallel extraction** across episodes and shows. Stateless workers plus a queue.
- **Storage:** ledger in Postgres/SQLite per show; the bible doubles as a writer reference and could be fed back *into* the script generator as context, preventing drift instead of only detecting it (the natural next step).
- **Cost (rough estimate, to be replaced by measured numbers):** a 1–2 min episode is a few hundred words. Extraction is roughly 2–4k tokens per episode including prompt; verification is ~1k tokens per candidate. A 60-episode show is therefore on the order of a few hundred thousand tokens. That is free on a local model and small on a cheap hosted model. We'll report measured tokens from real runs instead of quoting prices.
- **Model tiering:** small/cheap model for extraction, stronger model only for the verifier step (few calls). The `.env` switch supports per-step models.
- **Integration:** run automatically when a script batch is saved; post the report to the editor's review tool; editor labels flow back as training/eval data.
- **Extensions (not now):** multilingual scripts; visual continuity by checking generated storyboard frames against the bible; adaptation flagging (Idea B) using the same ledger.
