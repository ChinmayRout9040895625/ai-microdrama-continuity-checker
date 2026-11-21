# Evaluation: planted contradictions (S2)

- Planted run: `S2_planted_20261121-172842`, clean run: `S2_clean_20261121-172842`
- Model: extract=claude-sonnet-5-5@medium, check=claude-sonnet-5-5@medium

| Metric | Value |
|---|---|
| Recall on planted errors | **9/12 (75%)** |
| Flags on planted set not matching a planted error | 4 (see below; label by hand) |
| Flags on CLEAN set (false-alarm candidates) | 0 (0 marked 'could be intentional') |
| Facts extracted / dropped by quote check (planted) | 120 / 0 |
| Tokens in / out (planted run) | 80,393 / 15,153 |
| Wall time (planted run) | 48.3 s |

## Per planted error

| ID | Type | Episode gap | Found | Severity | Description |
|---|---|---|---|---|---|
| P01 | age | 6 | ✅ | high | Maya's age: 24 in ep1, says 22 in ep7 |
| P02 | status | 7 | ✅ | high | Adrian's father died in a crash (ep2) but Adrian plans to ask him tonight (ep9) |
| P03 | timeline | 2 | ❌ |  | Vanessa's engagement: two years (ep3) vs four years (ep5) |
| P04 | knowledge | 3 | ✅ | high | Adrian learned about the blackmail and fired Vanessa (ep7) but is surprised by it in ep10 |
| P05 | occupation | 6 | ❌ |  | Vanessa was marketing director (ep3) but says she was head of legal (ep9) |
| P06 | possession | 1 | ✅ | high | Surgery cost: $80,000 (ep1/2/5) vs $120,000 (ep6) |
| P07 | location | 6 | ✅ | medium | Maya's apartment: Maple Street (ep2) vs Oak Avenue (ep8) |
| P08 | identity | 2 | ✅ | high | Richard's lost daughter: Mia (ep6/8) vs Emma (ep10) |
| P09 | relationship | 3 | ❌ |  | Chloe is Adrian's sister (ep3) but called his cousin (ep6) |
| P10 | timeline | 4 | ✅ | high | Age when lost at the carnival: four (ep4) vs two (ep8) |
| P11 | relationship | 2 | ✅ | high | Vanessa met Maya in the diner (ep1) and confronted her at the office (ep3), but Adrian says she has never met Maya (ep5) |
| P12 | status | 2 | ✅ | high | Sam's surgery succeeded (ep7) but he is still waiting for it (ep9) |

## Extra flags on planted set

- **Ep5 vs Ep7** [medium/occupation] "Vanessa, you've never even met Maya. Stay away from her." vs "Adrian walks up to Vanessa's desk in front of the whole floor.": Vanessa was introduced as a wealthy socialite and Adrian's partner of four years, not as a marketing employee. She is now fired from a desk job at Cross Tower, which conflicts with that. This could be explained if she took the job on screen, but no such explanation is given.
- **Ep8 vs Ep10** [medium/timeline] "You were only two years old when I lost you at that carnival." vs "A con artist doesn't carry her father's photograph for twenty years without knowing it.": Maya was lost at age 2 (or found at age 4) about 20 years ago, but she is 22 or 24; her carrying the photo for twenty years conflicts with her having no memory before 4 and learning only recently that Richard is her father.
- **Ep7 vs Ep9** [medium/occupation ⚑intentional?] "Adrian walks up to Vanessa's desk in front of the whole floor." vs "When I was head of legal at Cross Capital, I read every contract he signed.": Ep7 shows Vanessa worked in the marketing department at Cross Tower, but Ep9 says she was head of legal at Cross Capital.
- **Ep1 vs Ep7** [low/timeline] "ADRIAN: Who's Sam?" vs "the night you threw coffee on me": In Episode 1 Maya did not throw coffee on Adrian. He left her a tip, and the two scenes shown contain no coffee-throwing. Episode 7 refers to 'the night you threw coffee on me' as if it were an established event. It may have happened off screen, so this is a low-confidence flag.

## Flags on clean set

_none_
