# Evaluation: planted contradictions (S2)

- Planted run: `S2_planted_20261121-174434`, clean run: `S2_clean_20261121-174516`
- Model: extract=claude-sonnet-5-5@medium, check=claude-sonnet-5-5@medium

| Metric | Value |
|---|---|
| Recall on planted errors | **12/12 (100%)** |
| Flags on planted set not matching a planted error | 1 (see below; label by hand) |
| Flags on CLEAN set (false-alarm candidates) | 1 (0 marked 'could be intentional') |
| Facts extracted / dropped by quote check (planted) | 133 / 0 |
| Tokens in / out (planted run) | 85,784 / 15,893 |
| Wall time (planted run) | 40.8 s |

## Per planted error

| ID | Type | Episode gap | Found | Severity | Description |
|---|---|---|---|---|---|
| P01 | age | 6 | ✅ | high | Maya's age: 24 in ep1, says 22 in ep7 |
| P02 | status | 7 | ✅ | high | Adrian's father died in a crash (ep2) but Adrian plans to ask him tonight (ep9) |
| P03 | timeline | 2 | ✅ | medium | Vanessa's engagement: two years (ep3) vs four years (ep5) |
| P04 | knowledge | 3 | ✅ | high | Adrian learned about the blackmail and fired Vanessa (ep7) but is surprised by it in ep10 |
| P05 | occupation | 6 | ✅ | high | Vanessa was marketing director (ep3) but says she was head of legal (ep9) |
| P06 | possession | 1 | ✅ | high | Surgery cost: $80,000 (ep1/2/5) vs $120,000 (ep6) |
| P07 | location | 6 | ✅ | medium | Maya's apartment: Maple Street (ep2) vs Oak Avenue (ep8) |
| P08 | identity | 2 | ✅ | high | Richard's lost daughter: Mia (ep6/8) vs Emma (ep10) |
| P09 | relationship | 3 | ✅ | medium | Chloe is Adrian's sister (ep3) but called his cousin (ep6) |
| P10 | timeline | 4 | ✅ | high | Age when lost at the carnival: four (ep4) vs two (ep8) |
| P11 | relationship | 2 | ✅ | high | Vanessa met Maya in the diner (ep1) and confronted her at the office (ep3), but Adrian says she has never met Maya (ep5) |
| P12 | status | 2 | ✅ | high | Sam's surgery succeeded (ep7) but he is still waiting for it (ep9) |

## Extra flags on planted set

- **Ep8 vs Ep10** [medium/timeline] "You were only two years old when I lost you at that carnival." vs "A con artist doesn't carry her father's photograph for twenty years without knowing it.": Maya was lost at age two, so she could not have carried her father's photograph for twenty years. She also only learned Richard was her father in Ep8, and the photo was in a locket she had since being found. The line also conflicts with her having no memory/knowledge of her father.

## Flags on clean set

- **Ep5 vs Ep7** [low/knowledge] "Maya stares at her reflection. She tells no one." vs "CHLOE: She's been blackmailing Maya for a week. Maya made me promise not to tell you. I'm breaking that promise.": Ep5 shows Maya telling no one about Vanessa's blackmail, but Ep7 has Chloe claiming Maya told her and made her promise secrecy, so both cannot be true unless Maya told Chloe off-screen later.
