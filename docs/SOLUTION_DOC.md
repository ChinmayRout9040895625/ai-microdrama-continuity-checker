# Microdrama Continuity Checker

Kuku AI Generalist Assignment, Problem 3 · [Name] · [Roll no.] · [Branch]

Prototype: [repo link] · Raw outputs: `outputs/` · Video: [link]

## Problem, user, and why it matters

A microdrama runs to 50+ one-minute episodes, and Kuku ships new shows every week. When an LLM drafts episodes one at a time, facts drift: an age changes, a dead father is "asked tonight", a character is shocked by a secret she learned three episodes earlier. The script editor has to catch this before scripts go to video generation. Once an error reaches generated clips, fixing it means regenerating video instead of editing a line.

I chose this over Problems 1 and 2 because it sits upstream: a promo (Problem 1) is only as good as the episodes it is cut from, and Problem 2 is outside Kuku's product. Problem 1 is closer to revenue. My case is about avoiding wasted generation and quality loss at volume.

**Evidence.** Public reviews of microdrama apps mostly complain about paywalls, not plot holes, so I do not claim viewers are angry about continuity. The evidence is on the production side. Vendor guides on AI microdramas (Techloy, Morphic) treat cross-episode consistency as the core problem. More directly, I had Claude Sonnet 5.5 draft a 12-episode series one episode per call, each seeing only the premise and the previous episode's summary. All six characters' ages changed between episodes, and so did the wedding date, venue, the hero's eye colour and the hospital he woke up in. No fixed character sheet was given, so the age drift is partly my setup; the rest is not.

## What I built

The editor uploads episode scripts (Streamlit UI or CLI) and gets a report. Each flag shows the two conflicting lines quoted from the script, a severity, a "could be intentional" marker and a suggested fix. A table at the top groups repeats ("Julian's age: 10 flags across 11 episodes"). The editor marks each flag Fix, Intentional twist or Not an issue.

| Step | Done by |
|---|---|
| Split into episodes; merge character aliases; pick earlier facts about the same people | Code |
| Extract checkable facts per episode, each with a verbatim quote | LLM (structured JSON) |
| Confirm each quote is in the script and replace it with the exact text, else drop the fact | Code |
| Say which new fact contradicts which earlier fact, by ID only | LLM |
| Error or deliberate twist? | Human |

The model never writes evidence into the report; it can only point at facts whose quotes the code has already found. Provider, model and effort are set per step in `.env`, so a stronger model can be plugged in without code changes. I used Claude Sonnet 5.5 (paid API, my own key). The free path is a local Ollama model behind the same switch, but on my CPU-only laptop a 3B model did not finish one episode in 20 minutes, so all results below are from Sonnet.

**Assumptions.** A human reviews a text-script stage before generation; episodes arrive as ordered text; twists are common, so the tool flags and a person decides; English only; visual continuity is out of scope. The Kuku input pack is confidential and was not used.

## How I know it works, and where it fails

I wrote a 10-episode series, checked it by hand, then planted 12 contradictions (age, death, job, money, address, name, relationship, knowledge, timeline) 1–7 episodes apart, and also ran the clean version.

| Version | Planted errors found | Flags on clean script |
|---|---|---|
| v1 (extraction at low effort) | 9/12 (10/12 after correcting one of my gold labels) | 3 |
| Final, 5 runs (3 fully uncached) | 12, 9, 10, 12, 12 (≈92%) | 1, 0, 1, 0, 1 |

v1 failed because at low effort the extractor returned one fact for episode 2, which held the source of two planted errors. Raising effort, asking for exhaustive extraction, and making the model explain before giving a yes/no verdict fixed it. I tuned on this same set, so these numbers are optimistic.

On the unseen 12-episode AI-drafted series the tool raised 57 flags. I labelled each against the scripts: 53 real errors, 2 intentional twists correctly marked, 1 debatable, 1 not an issue. Recall there is unknown; nobody has read all 12 episodes line by line.

Failures: extraction varies between runs (one run never extracted "engaged for two years", so "four years" went unflagged); one planted error was weak ("four years of my life" can include dating before a two-year engagement, and the model said so); the model once read `MAYA: (whispering) Vanessa.` after a text from "her manager" as Vanessa being the manager; three drift flags cited an imprecise line; and one drifting fact yields a flag per episode pair, which the grouping table only partly tames.

With a real team I would track the share of flags editors mark Fix (well below half and they stop reading), continuity errors found after video generation per show, and editor time per pass.

## Cost and scale

Measured: a 10-episode run takes about 86k input and 16k output tokens, roughly $0.33 at Sonnet 5.5 list prices, in under a minute. Extrapolated: a 60-episode show should cost a few dollars, because each episode is checked only against earlier facts about its characters (capped at 300). In production, facts are extracted once as each episode lands and stored per show, a cheaper model can extract while a stronger one checks, and the same fact ledger can be fed into the script generator to prevent drift rather than catch it.

## AI tools

Claude Code (Claude Opus 5.5) helped me plan, write the code and test scripts, and run the evaluations; Claude Sonnet 5.5 runs inside the tool. Where it went wrong: its alias-merging code stripped titles, so "Mr. Ashford" and "Mrs. Ashford" both became "ashford" and the hero and his mother were silently merged. I caught it only because the grouped report showed "Celeste Ashford: age, 14 flags" and no row for Julian.
