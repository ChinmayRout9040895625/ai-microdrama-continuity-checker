# Drift experiment (S1): does limited-context AI drafting produce continuity errors?

**Setup.** `eval/generate_series.py` asked Claude Sonnet 5.5 to draft a 12-episode original microdrama
("The Housekeeper's Secret"), **one episode per call**. Each call saw only the premise, the character names, and a 2–3
sentence summary of the *previous* episode. That mimics a cheap, context-limited generation pipeline. The prompt asked
for "concrete specifics (ages, years, amounts, places, job titles)". No character sheet with fixed ages was given, so
the age drift is partly induced by this setup.

**Run.** `outputs/S1_generated_20261121-173053/` · 12 episodes · 225 grounded facts (1 dropped) · 57 flags ·
154k input / 35k output tokens · 70 s wall time.

## Labels (all 57 flags, `eval/S1_labels.json`)

| Label | Count |
|---|---|
| Real continuity error | **53** (3 of them cite an imprecise line as evidence: #9, #24, #30) |
| Intentional twist, correctly marked "could be intentional" | 2 (#48, #49: the same cliffhanger flagged twice) |
| Debatable | 1 (#19) |
| Not an issue | 1 (#46: two characters disagree, which is a plot device) |

Flag precision: **53/57 strict (93%)**, or 55/57 (96%) counting correctly-marked twists.
*Labelled by the AI assistant and spot-checked against the scripts. A human pass is still pending.*
**Recall is unknown:** there is no gold list for S1, and nobody has read all 12 episodes line by line yet.

## What drifted (distinct underlying problems, ~15)

- **Ages of all 6 main characters** changed episode to episode (e.g. Julian: 33 → 32 → 34 → 35 → 36 → 34 → 32 → 34 → 32 → 35 → 34). These produce 42 of the 57 flags.
- **Wedding date**: June 14, 2018 (Ep1) vs June 9, 2018 (Ep2).
- **Wedding venue**: Harbor Chapel (Ep2) vs St. Anne's (Ep4).
- **Julian's eye colour**: green (Ep1–2) vs gray (Ep8) vs "dark" (Ep10).
- **Where Julian woke up**: St. Luke's (Ep7) vs St. Margaret's (Ep8) vs a Zurich clinic (Ep10).
- **How long ago**: "six years ago" (Ep4) vs "seven years ago" (Ep8).
- **Julian's own account of the wedding night**: waited at the church (Ep2) / never left (Ep4) / amnesia (Ep8) / "I left you the night before" (Ep12).
- **Knowledge regression**: Nora tells Julian "your son" (Ep5), then in Ep9 he only "begins to realize" Leo may be his.
- **Location jump**: Leo is at the Ashford mansion at the end of Ep10 and is kidnapped from the Grandview hotel at the start of Ep11.

## Takeaways

1. Limited-context drafting **does** drift, a lot, even with a strong model. This supports the problem being real for any
   pipeline that generates episodes without a maintained series bible.
2. The tool's flags were overwhelmingly correct, but **one drifting attribute produces many flags** (one per episode
   pair). The editor needs them **grouped** ("Julian's age is inconsistent across 11 episodes: pick one"). This is the top UX fix.
3. The same `bible.json` the checker builds could be fed **into** the generator as context, preventing most of this drift
   rather than only detecting it.
