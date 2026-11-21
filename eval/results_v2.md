# Evaluation: planted contradictions (S2)

- Planted run: `S2_planted_20261121-172732`, clean run: `S2_clean_20261121-172732`
- Model: extract=claude-sonnet-5-5@medium, check=claude-sonnet-5-5@medium

| Metric | Value |
|---|---|
| Recall on planted errors | **12/12 (100%)** |
| Flags on planted set not matching a planted error | 2 (see below; label by hand) |
| Flags on CLEAN set (false-alarm candidates) | 1 (1 marked 'could be intentional') |
| Facts extracted / dropped by quote check (planted) | 132 / 0 |
| Tokens in / out (planted run) | 86,443 / 15,952 |
| Wall time (planted run) | 49.1 s |

## Per planted error

| ID | Type | Episode gap | Found | Severity | Description |
|---|---|---|---|---|---|
| P01 | age | 6 | ✅ | high | Maya's age: 24 in ep1, says 22 in ep7 |
| P02 | status | 7 | ✅ | high | Adrian's father died in a crash (ep2) but Adrian plans to ask him tonight (ep9) |
| P03 | timeline | 2 | ✅ | medium | Vanessa's engagement: two years (ep3) vs four years (ep5) |
| P04 | knowledge | 3 | ✅ | high | Adrian learned about the blackmail and fired Vanessa (ep7) but is surprised by it in ep10 |
| P05 | occupation | 6 | ✅ | medium | Vanessa was marketing director (ep3) but says she was head of legal (ep9) |
| P06 | possession | 1 | ✅ | high | Surgery cost: $80,000 (ep1/2/5) vs $120,000 (ep6) |
| P07 | location | 6 | ✅ | medium | Maya's apartment: Maple Street (ep2) vs Oak Avenue (ep8) |
| P08 | identity | 2 | ✅ | high | Richard's lost daughter: Mia (ep6/8) vs Emma (ep10) |
| P09 | relationship | 3 | ✅ | medium | Chloe is Adrian's sister (ep3) but called his cousin (ep6) |
| P10 | timeline | 4 | ✅ | medium | Age when lost at the carnival: four (ep4) vs two (ep8) |
| P11 | relationship | 2 | ✅ | high | Vanessa met Maya in the diner (ep1) and confronted her at the office (ep3), but Adrian says she has never met Maya (ep5) |
| P12 | status | 2 | ✅ | high | Sam's surgery succeeded (ep7) but he is still waiting for it (ep9) |

## Extra flags on planted set

- **Ep6 vs Ep8** [medium/timeline] "My daughter Mia vanished twenty years ago, Martin." vs "You were only two years old when I lost you at that carnival.": Mia vanished twenty years ago, and Maya was 24 in Ep1, so she would have been about four then. Richard now says she was two when lost, which conflicts with the 24 or 22 age and the twenty-year timeline.
- **Ep8 vs Ep10** [medium/knowledge] "She opens the locket for the first time in years." vs "A con artist doesn't carry her father's photograph for twenty years without knowing it.": Maya says she carried her father's photo for twenty years, but she had not opened the locket in years and learned only recently that Richard is her father and the locket's photo is of him. She also claims to have had it since age 4, which is 20 years at 24, yet she is stated as 22 in Ep7.

## Flags on clean set

- **Ep1 vs Ep7** [low/timeline ⚑intentional?] "Hot coffee splashes across Adrian's jacket." vs "It stopped being a contract for me the night you threw coffee on me.": In Ep1 Maya spilled coffee on Adrian by accident when they first met, and the contract was only made in Ep2-3. Adrian now says it stopped being a contract the night she 'threw' coffee on him, but no contract existed that night. The coffee was also spilled, not thrown.
