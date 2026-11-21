# Microdrama Continuity Checker

Kuku AI Generalist Assignment, Problem 3.

AI-drafted microdramas run to 50+ one-minute episodes, and facts drift between them: ages change, a dead father
reappears, a character is "shocked" by something she already knew. This tool reads a series' episode scripts and
reports every place where a later episode contradicts an earlier one, **with both lines quoted verbatim from the
script**, so the script editor can fix them before the episodes go to video generation.

- **User:** the script editor reviewing AI-drafted episodes
- **Input:** episode scripts (plain text)
- **Output:** a continuity report (`report.md` / `report.json`) plus a per-character fact sheet (`bible.json`)

Write-up: [docs/SOLUTION_DOC.md](docs/SOLUTION_DOC.md) · Problem analysis: [docs/PROBLEM_ANALYSIS.md](docs/PROBLEM_ANALYSIS.md) ·
Design plan: [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) · Audit: [docs/FINAL_AUDIT.md](docs/FINAL_AUDIT.md)

## Features

- Flags contradictions in age, life status, job, relationships, knowledge (who knows what), places, money, names and timelines.
- Every flag quotes the two conflicting lines exactly as written in the script, with episode numbers.
- Severity (high / medium / low), a "could be intentional" marker for likely twists, and a suggested fix.
- A **Recurring problems** table groups repeated flags (e.g. one character's age drifting across 11 episodes).
- Streamlit UI where the editor marks each flag *Fix*, *Intentional twist* or *Not an issue* (saved to `labels.json`).
- Model, provider and reasoning effort set per step in `.env`. Responses are cached, so re-runs on unchanged input are free.

## How it works

```
episode files
   │
   ├─ 1. split into episodes ............................................ code
   ├─ 2. extract checkable facts per episode, each with a verbatim quote .. LLM (structured JSON)
   ├─ 3. find each quote in the script; replace it with the exact text,
   │     or drop the fact if it isn't there ............................. code (fuzzy match ≥ 85)
   ├─ 4. merge character aliases; for each episode, select earlier
   │     facts about the same characters ................................. code
   ├─ 5. "which new facts contradict which earlier facts?" (fact IDs only,
   │     reasoning written before a yes/no verdict) ...................... LLM
   ├─ 6. validate IDs, drop retracted flags, group repeats, write report .. code
   └─ 7. Fix / Intentional twist / Not an issue ......................... human (UI)
```

The LLM never writes evidence into the report. It can only point at fact IDs whose quotes step 3 has already found in
the script, so a flag cannot cite a line that does not exist.

Code: `continuity_checker/`: `ingest.py` (1) · `extract.py` (2–3) · `ledger.py` (4) · `check.py` (5) ·
`report.py` (6) · `pipeline.py` (orchestration) · `llm.py` (provider switch + cache) · `prompts.py` · `schemas.py` · `config.py`.

## Setup

Requires Python 3.10+ (developed and tested on Python 3.14, Windows 11).

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env
# open .env and set ANTHROPIC_API_KEY
```

## Usage

```bash
python cli.py data/S2_planted          # check a folder of episodes; prints the report
streamlit run app.py                    # UI: choose a sample or upload files, then label flags
```

Input is either a folder of `ep01.txt, ep02.txt, …` or **one** `.txt`/`.md` file with `EPISODE 1`, `EPISODE 2` …
headings. An optional `_aliases.json` in the folder (`{"Alexander Grant": ["Alex", "Mr. Grant"]}`) fixes name merges.
Each run writes `outputs/<series>_<timestamp>/` containing `report.md`, `report.json`, `bible.json`, `run_meta.json`
(model, tokens, time) and `raw/` (every LLM response unedited, dropped facts, retracted flags).

### Swapping the model

| `.env` setting | Default | Notes |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` | `ollama` for a free local model (`OLLAMA_MODEL`, `OLLAMA_URL`) |
| `MODEL_EXTRACT`, `MODEL_CHECK` | `claude-sonnet-5-5` | different models per step are allowed |
| `EFFORT_EXTRACT`, `EFFORT_CHECK` | `medium`, `medium` | `low` extraction lost facts in testing (see results) |
| `MAX_WORKERS` | `4` | parallel LLM calls |

## Sample output

From `outputs/S2_planted_20261121-173418/report.md` (planted test set):

> **2. 🔴 HIGH · timeline · Maya Collins (Ep 1 vs Ep 6)**
>
> | | Episode | Line | Fact |
> |---|---|---|---|
> | Earlier | 1 | "I know. Eighty thousand dollars. I'll find it. I promise." | needs eighty thousand dollars (for his care) |
> | Later | 6 | "A hundred and twenty thousand dollars, Sam. It's covered. You just focus on getting stronger." | is covering a $120,000 cost for Sam |
>
> **Why:** Sam's care was established as costing eighty thousand dollars (repeated in Ep2 and Ep5), but Maya now says it is a hundred and twenty thousand with no explanation of the increase.
> **Suggested fix:** Change the line to 'Eighty thousand dollars, Sam' or add a line explaining that complications raised the cost to $120,000.

From `outputs/S1_generated_20261121-173414/report.md` (AI-drafted series):

> | Character | Fact type | Flags | Episodes involved |
> |---|---|---|---|
> | Julian Ashford | age | 10 | 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
> | Sienna Vale | age | 9 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 |

## Results

All with Claude Sonnet 5.5. Details: [eval/](eval/) and [outputs/README.md](outputs/README.md).

| Test | Result |
|---|---|
| 12 planted contradictions, 5 runs of the final version | found 12, 9, 10, 12, 12 (≈92%) |
| Same series with no contradictions, 5 runs | 1, 0, 1, 0, 1 flags |
| v1 (extraction effort `low`), for comparison | 9/12 as originally scored (10/12 with the corrected P11 label); 3 clean-set flags |
| AI-drafted 12-episode series (unseen) | 57 flags: 53 real errors, 2 intentional twists correctly marked, 1 debatable, 1 not an issue |
| Cost / time | ≈86k input + 16k output tokens per 10-episode run (≈$0.33), under 1 minute |

## Deployment

**Results site (Vercel, static):** https://ai-microdrama-continuity-checker.vercel.app shows the stored scores,
every run report and the docs, all generated from this repo by `site/build_site.py`. It does not run the model.

```bash
pip install markdown
python site/build_site.py              # writes site/public/
vercel deploy site/public --prod
```

**Live app (Streamlit Community Cloud):** Vercel cannot host the Streamlit UI, which needs a long-running server.
To deploy it on Streamlit Community Cloud:
1. Go to share.streamlit.io and choose *Create app* → *Deploy from GitHub*.
2. Select this repository, branch `main` and main file `app.py`. Under *Advanced settings*, pick Python 3.12.
3. Under *Secrets*, add the following:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
   The app is open to anyone with the link, and every run uses this key (about $0.33 per 10-episode run).
   You can cap spending with a monthly limit in the Anthropic Console. Setting an `APP_PASSWORD` secret
   would put the app behind a password, but this deployment leaves it unset.

## Reproducing the evaluation

```bash
python eval/make_planted.py             # rebuilds data/S2_planted from data/S2_clean + data/planted.json
python cli.py data/S2_planted
python cli.py data/S2_clean
python eval/evaluate.py --planted outputs/<S2_planted run> --clean outputs/<S2_clean run> --out eval/results_new.md
python eval/audit_outputs.py            # checks every quoted line in every run against the scripts
python eval/generate_series.py --episodes 12 --out data/S1_new   # optional: new drift experiment
```

Re-scoring the stored runs with `eval/evaluate.py` reproduces the saved `eval/results_*.md` files exactly. The one
exception is v1, which was scored before the P11 gold-label correction. New LLM runs vary (see the 5-run spread above).

## Limitations

- **Twists vs errors:** the tool cannot know authorial intent; lies, disguises and amnesia plots will be flagged. A human decides.
- **Run-to-run variance:** extraction sometimes misses a fact, and a contradiction is then not flagged (recall 9–12 of 12 across runs).
- **Optimistic test numbers:** prompts were tuned after seeing v1 on the same planted set. Recall on the AI-drafted series is unmeasured.
- **Self-made test data:** all scripts are original and written for this project (the confidential Kuku input pack was not used). Real scripts may be harder.
- **Noise:** one drifting attribute produces a flag per episode pair. The recurring-problems table groups them, but the flag list stays long.
- **Scope:** English text only; no visual, audio or subtitle continuity.
- **Free local path unvalidated:** the Ollama provider is implemented, but `llama3.2:3b` on a CPU-only laptop did not finish one episode in 20 minutes. All reported results use the paid Anthropic API.
- **Labels:** the 57 drift-experiment labels (`eval/S1_labels.json`) were made with AI assistance and spot-checked against the scripts. They have not been independently reviewed.

## Repository layout

```
continuity_checker/   pipeline package (see "How it works")
cli.py, app.py        command line and Streamlit UI
data/                 S2_clean/ (hand-checked series), S2_planted/ (generated), planted.json (gold), S1_generated/ (AI-drafted)
eval/                 make_planted.py, evaluate.py, audit_outputs.py, generate_series.py, results_*.md/json, S1_labels.json
outputs/              raw, unedited run outputs (index in outputs/README.md)
docs/                 solution doc, problem analysis, implementation plan, final audit
```
