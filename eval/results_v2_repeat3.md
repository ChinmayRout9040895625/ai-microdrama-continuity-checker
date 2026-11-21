# Evaluation: planted contradictions (S2)

- Planted run: `S2_planted_20261121-172842`, clean run: `S2_clean_20261121-172842`
- Model: extract=claude-sonnet-5-5@medium, check=claude-sonnet-5-5@medium

| Metric | Value |
|---|---|
| Recall on planted errors | **10/12 (83%)** |
| Flags on planted set not matching a planted error | 4 (see below; label by hand) |
| Flags on CLEAN set (false-alarm candidates) | 1 (0 marked 'could be intentional') |
| Facts extracted / dropped by quote check (planted) | 133 / 0 |
| Tokens in / out (planted run) | 86,442 / 15,945 |
| Wall time (planted run) | 47.7 s |

## Per planted error

| ID | Type | Episode gap | Found | Severity | Description |
|---|---|---|---|---|---|
| P01 | age | 6 | ✅ | high | Maya's age: 24 in ep1, says 22 in ep7 |
| P02 | status | 7 | ✅ | high | Adrian's father died in a crash (ep2) but Adrian plans to ask him tonight (ep9) |
| P03 | timeline | 2 | ❌ |  | Vanessa's engagement: two years (ep3) vs four years (ep5) |
| P04 | knowledge | 3 | ✅ | high | Adrian learned about the blackmail and fired Vanessa (ep7) but is surprised by it in ep10 |
| P05 | occupation | 6 | ✅ | high | Vanessa was marketing director (ep3) but says she was head of legal (ep9) |
| P06 | possession | 1 | ✅ | high | Surgery cost: $80,000 (ep1/2/5) vs $120,000 (ep6) |
| P07 | location | 6 | ✅ | medium | Maya's apartment: Maple Street (ep2) vs Oak Avenue (ep8) |
| P08 | identity | 2 | ✅ | high | Richard's lost daughter: Mia (ep6/8) vs Emma (ep10) |
| P09 | relationship | 3 | ✅ | high | Chloe is Adrian's sister (ep3) but called his cousin (ep6) |
| P10 | timeline | 4 | ✅ | high | Age when lost at the carnival: four (ep4) vs two (ep8) |
| P11 | relationship | 2 | ✅ | high | Vanessa met Maya in the diner (ep1) and confronted her at the office (ep3), but Adrian says she has never met Maya (ep5) |
| P12 | status | 2 | ❌ |  | Sam's surgery succeeded (ep7) but he is still waiting for it (ep9) |

## Extra flags on planted set

- **Ep6 vs Ep8** [medium/timeline] "My daughter Mia vanished twenty years ago, Martin." vs "You were only two years old when I lost you at that carnival.": Mia vanished twenty years ago; Maya is 24 (or 22), so she would have been 4 (or 2) then. With Maya at 24 the age two is inconsistent; with Ep7's age 22 it fits, but Maya's age is itself inconsistent.
- **Ep1 vs Ep2** [medium/occupation ⚑intentional?] "VANESSA: Since when do you tip waitresses?" vs "A text from her manager: "Customer complaint. Don't come back.": Ep1 showed Vanessa as Adrian's glamorous companion and a diner customer who insulted Maya, with no sign she manages the diner. Ep2 has Maya identify Vanessa as the manager who sent the firing text, so the roles conflict.
- **Ep1 vs Ep7** [low/other] "Maya trips on Vanessa's outstretched heel. Hot coffee splashes across Adrian's jacket." vs "the night you threw coffee on me.": In Ep1 Maya tripped on Vanessa's heel and coffee accidentally splashed on Adrian's jacket; Ep7 says Maya threw coffee on him, which describes the event differently.
- **Ep8 vs Ep10** [low/timeline] "You were only two years old when I lost you at that carnival." vs "doesn't carry her father's photograph for twenty years without knowing it.": Maya was lost at age two and is now about 24 (or 22 per Ep7), so she cannot have carried her father's photograph for twenty years from that age. She also learned in Ep8 that Richard was her father and only recently opened the locket photo. Twenty years is plausible only if counted from age four, and she did not know whose photo it was.

## Flags on clean set

- **Ep2 vs Ep3** [high/occupation] "A text from her manager: "Customer complaint. Don't come back." vs "I'm the marketing director here, sweetheart, which means I know how to spot a cheap product.": Ep2 identifies Vanessa as Maya's manager at the diner, but Ep3 says she is the marketing director at Cross Tower, which is a different job.
