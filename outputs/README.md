# Raw outputs (unedited)

Every folder is one run of `cli.py`: `report.md` (what the editor reads), `report.json`, `bible.json`, `run_meta.json`
(model, effort, tokens, time), and `raw/`, which holds every LLM response exactly as returned, facts dropped by the quote
check, and flags the model retracted.

| Run | Input | Version | Notes |
|---|---|---|---|
| `S2_planted_20261121-172354` | planted set | v1 (extract effort `low`) | 9/12 planted errors found. Ep 2 extraction collapsed to 1 fact |
| `S2_clean_20261121-172502` | clean set | v1 | 3 flags (false-alarm candidates) |
| `S2_planted_20261121-172732` | planted set | **v2** | 12/12 found |
| `S2_clean_20261121-172732` | clean set | **v2** | 1 low flag |
| `repeats/r2/*`, `repeats/r3/*` | planted + clean | v2, no cache | 9/12 and 10/12 found; 0 and 1 clean flags (run-to-run variance) |
| `S1_generated_20261121-173053` | AI-drafted 12-episode series | v2 | 57 flags; **the run labelled** in `eval/S1_labels.json` |
| `S1_generated_20261121-173414` | same series | final (v2 prompts + alias fix + grouping) | re-rendered from cache: identical 57 flags, adds the "Recurring problems" table |
| `S2_planted_20261121-173418` | planted set | final | 12/12 found (extraction reused from cache; check step re-run) |
| `S2_clean_20261121-173434` | clean set | final | 0 flags |
| `fresh_env/S2_planted_20261121-174434` | planted set | final, fresh venv, no cache | 12/12 found |
| `fresh_env/S2_clean_20261121-174516` | clean set | final, fresh venv | 1 low flag (Ep5 "she tells no one" vs Ep7 Chloe knows: debatable) |

Scores: `eval/results_v1_effort-low.md`, `eval/results_v2.md`, `eval/results_v2_repeat2.md`, `eval/results_v2_repeat3.md`,
`eval/results_v3_final.md`, `eval/results_fresh_env.md`, `eval/results_S1.md`.

Note: `eval/results_v1_effort-low.md` was scored before the P11 gold-label correction (9/12). Re-scoring the same raw v1
output with the current `data/planted.json` gives 10/12. The file has been left as originally produced.

Quote check (`python eval/audit_outputs.py`): in every run with v2+ prompts, all quoted lines appear verbatim in the
input scripts. The two v1 runs contain 11 quotes with stray `}` / `</br>` characters (fuzzy match 89–99); v2 fixed this
by replacing quotes with the exact script text.

v1 → v2 changes: extraction effort `low` → `medium`; the extraction prompt asks for exhaustive facts; the model now writes its
reasoning *before* an `is_real_contradiction` verdict, and retracted flags are dropped in code; quotes are snapped to
the exact script text; and the P11 gold label was corrected (Ep 3 is also a valid source).
