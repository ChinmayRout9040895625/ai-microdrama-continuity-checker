# Problem 3 — Problem Analysis

> Status: planning document. No code written yet. Everything marked **[TO COLLECT]** is evidence we still have to gather ourselves; nothing here is invented user feedback.

---

## 1. What Kuku expects from Problem 3

From the brief (pp. 3–5):

| Requirement | What it means for us |
|---|---|
| "Pick a real problem in **making, adapting or promoting** AI microdramas" | Must sit inside the microdrama pipeline, not a generic AI tool. |
| "**Show it's real**" — watch shows, study promos, read reviews, talk to viewers | Need evidence we can point at: links, quotes, counts, or a reproducible experiment. No made-up research. |
| "Tell us **who** has the problem, **how you know**, and **why it matters more than Problems 1 and 2**" | One named role, an evidence trail, and an explicit comparison argument. |
| "Build the **smallest thing that helps**" — one person, one step, one output you can check | Narrow scope. The output must be *verifiable* by a reviewer. |
| "Tell us how you'd know it worked once a real team used it" | Production success metrics, not just offline accuracy. |
| Runs again on a **new input** in the interview; model **easy to swap** | Input-agnostic pipeline, model behind one config switch. |
| Free tiers only | Local model (Ollama) or free API tier. |
| Deliverables: 2-page PDF doc, prototype link/repo, **raw unedited outputs**, optional 3-min video | Plan for outputs folder and doc from day one. |
| Doc must say which AI tools were used and **one place they got it wrong** | Keep a running log while building. |

**Evaluation lenses (p. 5):** problem choice & framing · approach & scale (AI vs code vs human-in-loop, cost at volume) · quality checking (real runs, honest failures) · prototype runs on real inputs · clear, short communication.

**Key reading of the brief:** the *choice and justification* of the problem is itself graded. A checkable output and an honest failure analysis matter more than polish.

**Assumption:** the Kuku input pack is not in this folder, and it is confidential ("don't publish or share it"). We therefore build on **public / self-generated inputs** so that raw outputs can be shared freely. If the pack becomes available, the tool should run on it unchanged.

---

## 2. Three candidate problems

### Idea A — Continuity checker for AI-written multi-episode scripts
**Stage:** making (pre-production, script QA).
**User:** script editor / story QA on an AI-assisted writing team.
**Problem:** A microdrama runs 50–100+ episodes of 1–2 minutes. When scripts are drafted by LLMs (often episode by episode, with limited context), facts drift: a character's age, job, or relationship changes; a dead character reappears; someone "learns" a secret they already knew; a name is spelled two ways. A human editor has to hold the entire series in their head to catch this. If an error slips past script stage, it gets baked into generated video, which is far more expensive to redo.
**Output:** a continuity report — each flagged contradiction with both episode numbers and the exact quoted lines — plus an auto-built character/fact sheet ("series bible").

### Idea B — Cultural adaptation flagger for cross-market script localization
**Stage:** adapting.
**User:** localization writer adapting a show from one market to another (e.g. US English → Indian audience, or Chinese → US).
**Problem:** Literal translation/dubbing keeps culture-specific beats that don't land (names, places, gestures, social norms, legal/financial setups). Output would flag such elements per line, propose replacements, and check that rewritten lines stay within a dub-timing length budget.
**Output:** an annotated script with flags, suggested replacements, and length-ratio warnings.

### Idea C — Viewer-review miner for the content team
**Stage:** promoting / commissioning feedback loop.
**User:** content strategist.
**Problem:** Thousands of app-store and Trustpilot reviews per app; nobody reads them systematically to find content-level complaints (pacing, endings, translation, repetitive plots) versus billing complaints.
**Output:** a themed report with counts and representative quotes.

---

## 3. Evaluation of the three ideas

Scores are my judgement (1 = weak, 5 = strong), with the reason stated.

| Criterion | A. Continuity checker | B. Adaptation flagger | C. Review miner |
|---|---|---|---|
| Real-world relevance | **4** — consistency is named as an open problem in microdrama generation research and practitioner guides (see §5). Directly about *AI-generated* shows. | **5** — Kuku is explicitly multi-language; strong public evidence (MIT Tech Review). | **3** — useful, but most public complaints are about billing/paywalls, not content. |
| Feasible in 2–3 h | **4** — text-in, JSON-out; pipeline is extract → compare → verify. | **3** — "is this culturally off?" is subjective; needs target-market knowledge to judge outputs. | **5** — scrape + classify is simple. |
| Output is checkable | **5** — every flag cites two quotes; a reviewer can verify in seconds. Planted-error tests give a real recall number. | **3** — quality of a cultural replacement is a matter of opinion; length checks are objective but minor. | **3** — theme counts are checkable, insight value is not. |
| Usefulness to one person | **5** — replaces a manual cross-episode read-through. | **4** | **2** — produces a report, not a step in someone's daily work. |
| Impact at Kuku scale | **4** — catches errors *before* expensive video generation, on every show, every week. | **4** | **2** |
| Distinct from Problems 1 & 2 | **5** — upstream of promos; nothing to do with legal. | **5** | **4** — overlaps "promoting" thinking of P1. |
| **Total (/30)** | **27** | **24** | **19** |

---

## 4. Recommendation: Idea A — Script Continuity Checker

**One person:** the script editor reviewing AI-drafted episodes.
**One step:** the continuity pass before scripts go to video generation.
**One output:** a continuity report of contradictions, each backed by quoted evidence from two episodes.

### Why this one
1. **It targets something specific to AI microdramas.** LLM-drafted serials with many short episodes are exactly where long-range drift happens; a human writer's room has a bible and memory, an episode-by-episode generator often doesn't.
2. **Output is objectively checkable.** A flag is right or wrong, and the evidence is in the flag itself. This is the strongest possible position for the "Quality checking" lens.
3. **We can measure it honestly.** Plant known contradictions into a script set → measure recall. Run on a clean set → measure false alarms. These are real numbers, not vibes.
4. **Clear human-in-the-loop design.** The tool flags; the editor decides (fix / intentional twist / ignore). Microdrama plots rely on deliberate reversals (hidden identity, amnesia, secret twins), so a human must stay in the loop. We say so plainly.
5. **Cheap to scale:** incremental per-episode checks against a stored fact ledger, not re-reading the whole series every time.

### Why it matters more than Problems 1 and 2 (the argument we'll make)
- **vs Problem 1 (promos):** promos sell a show that already exists. A continuity error caught at script stage costs an edit to a text file. The same error found after video generation means re-generating clips. One practitioner guide reports keeping roughly a quarter of generated clips (41 of 164) for one episode, so generation is already the costly, wasteful step. Upstream QA protects every downstream step, including promos: a promo stitched from episodes that contradict each other is weaker. *(Caveat: that figure comes from a vendor/partner blog. Cite it as "reported", not as fact.)*
- **vs Problem 2 (AI lawyer):** it's outside Kuku's core business; Problem 3 improves the product Kuku actually ships.
- **Honest counterpoint:** Problem 1 has a direct revenue link (user acquisition). Our argument is about *preventing cost and quality loss upstream at volume*, not about bigger revenue. We should say this openly.

### Runner-up
Idea B (adaptation flagger) has stronger public evidence but a less checkable output. It's a good "next step" to mention in the doc: the same fact-ledger architecture could flag culture-specific elements.

---

## 5. Target user, their difficulty, and evidence

### Target user
**Script editor / story QA** on a team producing AI-generated microdrama scripts. *(Assumption: Kuku's AI pipeline produces scripts that a human reviews before video generation. The brief doesn't say this directly; we assume it because the input pack contains "detailed screenplays with timestamps", which implies a script stage exists.)*

### Their current difficulty (stated as hypotheses to verify)
- 50+ episodes per show × new shows every week (brief, p. 2) → too much text to hold in memory.
- Contradictions are spread across distant episodes (ep 3 vs ep 41), which is exactly where manual review is weakest.
- No structured series bible exists if the scripts were generated rather than written by a room.

### Evidence we already found (public; verify each link before citing)

| Source | What it supports | Strength |
|---|---|---|
| [Techloy — "How to maintain character consistency across an AI microdrama series"](https://www.techloy.com/how-to-maintain-character-consistency-across-an-ai-microdrama-series/) | Small deviations "accumulate fast" across tightly connected episodes; recommends a human review pass **at episode boundaries**; reports one episode used 41 of 164 generated clips. | Medium-low (partner/vendor content) |
| [Morphic — "Keep the same cast across 60 episodes"](https://morphic.com/resources/use-cases/episodic-character-consistency) | Vendor treats cross-episode consistency as a product-worthy problem. | Low (vendor marketing), but shows market demand |
| [arXiv 2605.22144](https://arxiv.org/pdf/2605.22144) (short-drama generation paper) | Search summary says it lists errors in character consistency, prop states and action continuity as open issues. | Medium — **[TO VERIFY]**: I have not read the paper; confirm the exact claim before citing. |
| [DramaBench (arXiv 2512.19012)](https://arxiv.org/pdf/2512.19012) and [DraMaze (arXiv 2610.32002)](https://arxiv.org/pdf/2610.32002) | Academic work on evaluating/generating drama scripts, where consistency is treated as an evaluation dimension. | Medium — **[TO VERIFY]**: read abstracts before citing. |
| [Unstar — short-drama apps ranked from 1–3★ reviews](https://unstar.app/blog/reelshort-dramabox-shortmax-goodshort-flextv-short-drama-apps-ranked-2026) | Viewers complain of repetitive plots and translations "so bad you lose the plot". | Low-medium (blog aggregator) |

**Honest gap:** viewer reviews mostly complain about **billing and paywalls**, not plot holes. Searching turned up few direct viewer complaints about continuity. So we should **not** claim "viewers are angry about continuity". The stronger claim is about **production**: continuity is a known failure mode of AI generation, and catching it early is cheaper.

### Evidence we will generate ourselves (reproducible, cheap)
1. **Drift experiment [DONE, 2026-11-21]:** Claude Sonnet 5.5 drafted a 12-episode original microdrama, one episode per call, seeing only the premise and the previous episode's summary. Result: heavy drift. All six characters' ages changed between episodes, plus the wedding date, venue, eye colour, hospital name and "how many years ago", and one knowledge regression. Of the checker's 57 flags, 53 were labelled real errors (see `eval/results_S1.md`). Caveat: no fixed character sheet was provided, so the age drift is partly induced by the setup.
2. **Review sample [TO COLLECT]:** read ~30 recent 1–3★ Play Store reviews of 2–3 microdrama apps; tag each as billing / content / translation / other. Report the actual split. This shows we checked, even if continuity complaints turn out rare.
3. **Viewing log [TO COLLECT, optional]:** watch the first ~10 free episodes of 1–2 shows and note any continuity slips with timestamps.

---

## 6. Assumptions (to restate in the final doc)
1. Kuku's AI microdrama workflow has a text-script stage reviewed by a human before video generation.
2. Episodes are available as text (screenplay or transcript), one per episode, in order.
3. Deliberate twists (lies, hidden identities, amnesia) are common. The tool flags them as candidates and the human labels them; it cannot tell twist from error on its own.
4. English scripts for the prototype; multilingual is a scale-up item.
5. Visual continuity (faces, costumes) is out of scope: text only.
6. Input pack unavailable/confidential → public and self-generated inputs.
