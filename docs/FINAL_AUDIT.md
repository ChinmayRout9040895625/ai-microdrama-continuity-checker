# Final submission audit

Date: 2026-11-21 · Scope: the 9 checks requested before submission. Nothing was committed, pushed or initialised as a
git repository in the project folder. No evaluation labels were changed.

## Summary

| # | Check | Result |
|---|---|---|
| 1 | Project structure; unnecessary files removed | **Pass** (bytecode caches removed; nothing important deleted) |
| 2 | Tests and evaluation results reproducible | **Pass, one exception** (v1 result file predates a gold-label fix) |
| 3 | `eval/S1_labels.json` consistent with raw outputs | **Pass on structure, one wrong note** (#9), not changed |
| 4 | Every reported contradiction has verifiable quotes | **Pass** for all v2+ runs; v1 runs have 11 quotes with stray characters |
| 5 | `docs/SOLUTION_DOC.md` meets Problem 3 requirements, ≤ 2 pages | **Pass** after edits (renders to 2 A4 pages); one sentence depends on item A below |
| 6 | Professional README | **Done** (rewritten) |
| 7 | Secrets and confidential files excluded from Git | **Pass** (`.gitignore` updated) |
| 8 | Runs from a fresh environment with documented commands | **Pass** |
| 9 | Raw outputs and results organised | **Pass** (`outputs/README.md` indexes every run) |

## What passed

**1. Structure.** Removed: `__pycache__/` folders (regenerated automatically). Kept: everything else, including the v1
runs, which document the v1 → v2 improvement. Added: `eval/audit_outputs.py` (read-only checker for quotes and labels),
`outputs/fresh_env/` and `eval/results_fresh_env.*` (from check 8), and an "As built" section in
`docs/IMPLEMENTATION_PLAN.md` listing where the build differs from the plan. No working code was changed.

**2. Reproducibility.**
- `eval/make_planted.py` in a fresh copy rebuilds `data/S2_planted/` byte-identical to the committed files.
- Re-scoring every stored run with `eval/evaluate.py` reproduces `results_v2.md`, `results_v2_repeat2.md`,
  `results_v2_repeat3.md` and `results_v3_final.md` exactly (diffed).
- Cached re-runs of `cli.py` reproduce identical reports. Uncached LLM runs vary, which is reported as a result
  (recall 12, 9, 10, 12, 12 across five runs), not hidden.

**3. Labels.** All 57 labels in `eval/S1_labels.json` point at `outputs/S1_generated_20261121-173053`. Each label's ID,
episode pair, issue type and severity match the raw `report.json`, and there are no duplicate IDs. The later re-render
`S1_generated_20261121-173414` contains the same 57 issue IDs.

**4. Quotes.** `python eval/audit_outputs.py` checks every quoted line in every run against the input scripts:

| Runs | Flags | Quotes verbatim in script | Quotes fuzzy-only |
|---|---|---|---|
| 12 runs with v2+ prompts (incl. repeats, S1, final, fresh env) | 190 | **380 / 380** | 0 |
| 2 runs with v1 prompts | 24 | 37 | 11 (trailing `}` / `</br>`; text otherwise present, match 89–99) |

**5. Solution doc vs the brief.** Every item the brief asks for is present: problem and why (vs Problems 1 and 2),
who has it and how we know, assumptions, how it works (AI vs code vs human), scale and cost, quality with real runs and
failures, how we'd know it worked with a real team, AI tools used and one place they went wrong, model swappability, and
confidentiality of the input pack. Changes made:
- trimmed from 1,335 to about 1,020 words. A test render (A4, 11 pt, 18 mm margins, headless Edge) is **2 pages**, with
  about half of page 2 free;
- added the brief's paid-vs-free point: results use the paid Sonnet API (your choice); the free Ollama path exists but
  is unvalidated;
- updated the numbers to include the fresh-environment run (5 runs, ≈92%);
- stated v1 as "9/12 (10/12 after correcting one of my gold labels)";
- removed the word "independent" from "5 runs", because two of them reused cached extractions.

**6. README.** Rewritten with: purpose and user, features, architecture diagram with the AI/code/human split, setup,
usage, model swapping, real sample output (copied from stored reports), results, reproduction commands, limitations, and layout.

**7. Git exclusions.** `.gitignore` now covers `.env`, `.venv/`, `.cache/`, `.cache_*/`, `__pycache__/`, `*.pyc`, the
Kuku brief PDF (`Kuku*.pdf`) and UI demo labels (`outputs/**/labels.json`). I checked this with a dry-run `git add` on
a mirror of the file names (empty placeholder files, no contents, in a temporary folder): 430 files would be added,
including `.env.example`, and none of the excluded files. The API key string appears only in `.env`. No file outside
`.env`/`.venv`/`.cache` contains your username, local paths or email. The Kuku input pack was never in this folder.

**8. Fresh environment.** I copied the project (without `.venv`, `.cache`, `.env` or the PDF) to a temporary folder,
created a new venv, and ran `pip install -r requirements.txt`, which installed all six packages. Then I ran:
- `eval/make_planted.py`: output identical to the committed files;
- `cli.py data/S2_planted` (live API): 12/12 found;
- `cli.py data/S2_clean`: 1 low flag;
- `eval/evaluate.py`: scored correctly;
- `cli.py --help`;
- a headless Streamlit `AppTest` of both UI pages: no exceptions.

The two new runs were copied to `outputs/fresh_env/`. The first install attempt failed because drive C: was full
(about 72 MB free at that point). It passed once space was available.

**9. Organisation.** `outputs/README.md` lists every run with input, version and headline result, and links each
`eval/results_*.md`. Every run folder has `report.md`, `report.json`, `bible.json`, `run_meta.json` and `raw/` (unedited
LLM responses, dropped facts, retracted flags).

## What failed or is inconsistent (not fixed: needs your decision)

- **A. Label note #9 is wrong.** The note says the flag "cites Julian's age line as the 'earlier' evidence instead of
  the green-eyes line", but the cited quote is *"Julian Ashford (33, tailored charcoal suit, tired green eyes) stares at
  his mother."* It does contain the green eyes. The label (`true_error`) is right; only the note is wrong. As a result,
  "three drift flags cited an imprecise line" in `docs/SOLUTION_DOC.md` and "#9, #24, #30" in `eval/results_S1.md`
  should say **two (#24, #30)**.
- **B. `eval/results_v1_effort-low.md` says 9/12**, because it was scored before the P11 gold label was corrected.
  Re-scored against the current `data/planted.json` it is 10/12. The README, the solution doc and `outputs/README.md`
  state both figures; the file itself is unchanged.
- **C. Label #47** is `true_error` while the tool marked it "could be intentional". This is consistent with my
  reasoning (Julian's own accounts contradict each other), but the label has no note explaining it.
- **D. Fresh-env clean-set flag** (Ep5 "She tells no one" vs Ep7 Chloe knows) is not labelled anywhere. I consider it
  debatable: possibly a real slip in my own clean script.

## Remaining limitations (documented in README and solution doc)

- Tuned on the same planted set the prompts were tested on, so ≈92% recall is optimistic.
- Recall on the AI-drafted series is unmeasured (no line-by-line gold).
- Run-to-run extraction variance (recall 9–12 of 12).
- All test scripts are self-written; real Kuku scripts may be harder.
- One drifting fact yields many flags; grouping helps only partly.
- English text only; no visual or audio continuity.
- The free Ollama path is implemented but unvalidated.
- S1 labels are AI-assisted and spot-checked, not independently reviewed.
- Evidence sources: the Techloy and Morphic claims, and "reviews mostly mention paywalls", come from web-search
  summaries; the pages were not read in full. `docs/PROBLEM_ANALYSIS.md` still has unfinished **[TO COLLECT]** items
  (a review sample and a viewing log) and **[TO VERIFY]** arXiv references; the solution doc does not cite the arXiv papers.

## Exact files required for submission

| Submission item | What to provide |
|---|---|
| Solution doc (PDF, ≤ 2 pages) | Export `docs/SOLUTION_DOC.md` after filling in name, roll no., branch and links |
| Prototype link (repo) | `README.md`, `requirements.txt`, `.env.example`, `.gitignore`, `cli.py`, `app.py`, `continuity_checker/` (10 `.py` files), `eval/*.py` (4 scripts), `data/` (`S2_clean/`, `S2_planted/`, `planted.json`, `S1_generated/`), `docs/` (`SOLUTION_DOC.md`, `PROBLEM_ANALYSIS.md`, `IMPLEMENTATION_PLAN.md`, `FINAL_AUDIT.md`) |
| Raw outputs (unedited) | `outputs/` (all run folders + `outputs/README.md`), `eval/results_*.md` / `.json`, `eval/S1_labels.json` |
| Walkthrough video (optional) | e.g. `streamlit run app.py` on the `S2_planted` sample |

Must **not** be submitted or published: `.env`, `.venv/`, `.cache/`, `Kuku — AI Generalist Assignment (1).pdf`.

## Actions requiring your approval

1. **Fix item A:** correct the #9 note in `eval/S1_labels.json` and change "three"/"#9, #24, #30" to "two"/"#24, #30"
   in `docs/SOLUTION_DOC.md` and `eval/results_S1.md`.
2. **Item B:** either leave `eval/results_v1_effort-low.md` as originally produced (current state, explained in three
   places), or regenerate it against the corrected gold label.
3. **Items C and D:** add a note to label #47, and decide whether to record the fresh-env clean flag as debatable.
4. **Review the 57 S1 labels yourself** before submission; they are currently AI-assisted.
5. **Rotate the Anthropic API key.** It was pasted into the chat transcript.
6. **Git:** initialise the repo, make the first commit and push to GitHub (not done, as instructed).
7. **Verify the two web sources** (Techloy, Morphic) by opening them, or drop that sentence from the solution doc.
8. Fill in name, roll no., branch, repo and video links in `docs/SOLUTION_DOC.md`, then export it to PDF.
9. Optional: delete `.cache/` (git-ignored, about 0.5 MB). Keeping it makes re-runs of existing inputs free.
