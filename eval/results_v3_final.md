# Evaluation: planted contradictions (S2)

- Planted run: `S2_planted_20261121-173418`, clean run: `S2_clean_20261121-173434`
- Model: extract=claude-sonnet-5-5@medium, check=claude-sonnet-5-5@medium

| Metric | Value |
|---|---|
| Recall on planted errors | **12/12 (100%)** |
| Flags on planted set not matching a planted error | 1 (see below; label by hand) |
| Flags on CLEAN set (false-alarm candidates) | 0 (0 marked 'could be intentional') |
| Facts extracted / dropped by quote check (planted) | 134 / 0 |
| Tokens in / out (planted run) | 64,008 / 4,316 |
| Wall time (planted run) | 15.1 s |

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

- **Ep8 vs Ep10** [medium/timeline] "She opens the locket for the first time in years." vs "A con artist doesn't carry her father's photograph for twenty years without knowing it.": Maya had not opened the locket in years and learned of her father only in Ep8, and was found at age four, so she cannot have carried her father's photo for twenty years knowingly; also the photo was only newly seen.

## Flags on clean set

_none_
