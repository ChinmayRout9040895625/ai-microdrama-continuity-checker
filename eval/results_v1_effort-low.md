# Evaluation: planted contradictions (S2)

- Planted run: `S2_planted_20261121-172354`, clean run: `S2_clean_20261121-172502`
- Model: extract=claude-sonnet-5-5@low, check=claude-sonnet-5-5@medium

| Metric | Value |
|---|---|
| Recall on planted errors | **9/12 (75%)** |
| Flags on planted set not matching a planted error | 12 (see below; label by hand) |
| Flags on CLEAN set (false-alarm candidates) | 3 (0 marked 'could be intentional') |
| Facts extracted / dropped by quote check (planted) | 96 / 0 |
| Tokens in / out (planted run) | 69,851 / 12,893 |
| Wall time (planted run) | 50.1 s |

## Per planted error

| ID | Type | Episode gap | Found | Severity | Description |
|---|---|---|---|---|---|
| P01 | age | 6 | ✅ | high | Maya's age: 24 in ep1, says 22 in ep7 |
| P02 | status | 7 | ❌ |  | Adrian's father died in a crash (ep2) but Adrian plans to ask him tonight (ep9) |
| P03 | timeline | 2 | ✅ | high | Vanessa's engagement: two years (ep3) vs four years (ep5) |
| P04 | knowledge | 3 | ✅ | high | Adrian learned about the blackmail and fired Vanessa (ep7) but is surprised by it in ep10 |
| P05 | occupation | 6 | ✅ | high | Vanessa was marketing director (ep3) but says she was head of legal (ep9) |
| P06 | possession | 1 | ✅ | medium | Surgery cost: $80,000 (ep1/2/5) vs $120,000 (ep6) |
| P07 | location | 6 | ❌ |  | Maya's apartment: Maple Street (ep2) vs Oak Avenue (ep8) |
| P08 | identity | 2 | ✅ | high | Richard's lost daughter: Mia (ep6/8) vs Emma (ep10) |
| P09 | relationship | 3 | ✅ | medium | Chloe is Adrian's sister (ep3) but called his cousin (ep6) |
| P10 | timeline | 4 | ✅ | high | Age when lost at the carnival: four (ep4) vs two (ep8) |
| P11 | relationship | 4 | ❌ |  | Vanessa insulted Maya in the diner (ep1) but Adrian says she has never met Maya (ep5) |
| P12 | status | 2 | ✅ | high | Sam's surgery succeeded (ep7) but he is still waiting for it (ep9) |

## Extra flags on planted set

- **Ep3 vs Ep5** [high/knowledge] "So THIS is the mystery girl! I'm Chloe, Adrian's little sister." vs "Vanessa, you've never even met Maya. Stay away from her.}": Adrian says Vanessa has never met Maya, but Ep1 shows Vanessa sitting with Adrian at the diner where Maya served them, and Ep3 shows Vanessa confronting Maya at the office. Adrian was present at the diner, so he should know they have met.
- **Ep1 vs Ep7** [high/timeline] "Who's Sam?" vs "It stopped being a contract for me the night you threw coffee on me.": Ep1 shows Adrian meeting Maya at the diner, where he leaves a tip and asks 'Who's Sam?'. No coffee-throwing incident was shown, and the line implies a different first encounter.
- **Ep5 vs Ep7** [medium/timeline] "Three months. Eighty thousand dollars. Cute.}" vs "She's been blackmailing Maya for a week. Maya made me promise not to tell you. I'm breaking that promise.": Vanessa's blackmail began in Ep5 with a Friday deadline, and Ep6 refers to 'Friday' still ahead. Chloe now says it has been going on for a week with threatening texts, while Ep5 showed an in-person threat with photographed contract pages.
- **Ep6 vs Ep8** [medium/timeline] "My daughter Mia vanished twenty years ago, Martin." vs "You were only two years old when I lost you at that carnival.}": Mia vanished twenty years ago when Maya was 24 (or 22 per Ep7), so she would have been 4 (or 2) at the time. Ep1 and Ep4 give 24 and four, which are consistent, but Ep7 gives 22, which matches age two. The two ages for Maya conflict with each other and with the carnival age.
- **Ep8 vs Ep10** [medium/timeline] "You were only two years old when I lost you at that carnival.}" vs "A con artist doesn't carry her father's photograph for twenty years without knowing it.": Maya was lost at age two (Ep8) or found at age four (Ep4), and she is 22 or 24, so she cannot have carried her father's photo for twenty years. Also, she only learned Richard was her father in Ep8, so she cannot have known it for twenty years.
- **Ep7 vs Ep9** [medium/occupation ⚑intentional?] "Pack your things. You're fired. Security will walk you out." vs "When I was head of legal at Cross Capital, I read every contract he signed.": Ep7 says Vanessa worked in the marketing department at Cross Tower, so she cannot also have been head of legal reading every contract Adrian signed.
- **Ep3 vs Ep7** [low/occupation] "I'm the marketing director here, sweetheart, which means I know how to spot a cheap product." vs "Pack your things. You're fired. Security will walk you out.": Vanessa was established as the marketing director, but Ep7 describes her as working at a desk in the marketing department, implying a lower role.
- **Ep6 vs Ep7** [low/other] "A hundred and twenty thousand dollars, Sam. It's covered. You just focus on getting stronger." vs "Maya, Sam's surgery was a complete success.": Ep6 says Sam's care costs $120,000 and is covered, while Ep1 and Ep5 describe $80,000 as the need, and Ep6 has Maya telling Sam it's already covered, yet Ep7 has the surgery result arriving as a big reveal. This is a mild inconsistency in the cost and funding arc.
- **Ep1 vs Ep8** [low/location] "This trash has worked double shifts since my mom died eight years ago." vs "I drove past this building on Oak Avenue three times before I found the courage to knock.}": Maya's residence is never established elsewhere, but Richard says he drove past her building three times before knocking; the apartment is shown on Oak Avenue, which is not contradictory.
- **Ep4 vs Ep8** [low/possession] "I was wearing it when she found me alone at the Navy Pier carnival." vs "Inside, a tiny photo of a younger Richard holding a little girl.}": Maya said Grace found her wearing the locket, which she has kept, and it was engraved 'M.H.'. Now she opens it 'for the first time in years', implying it had been unopened, though she wore it constantly; this is minor and consistent with the engraving.
- **Ep4 vs Ep8** [low/knowledge ⚑intentional?] "I hope not. God, I hope not." vs "Your name is Mia Hale. I put that locket on you myself.}": Richard only learned Maya's name and was hoping she was not who he feared, but now he weeps with joy at the match. This could be an on-screen development after the DNA result.
- **Ep4 vs Ep10** [low/status ⚑intentional?] "My mother, Grace, said I was wearing it when she found me alone at the Navy Pier carnival." vs "Then ask her who really killed Grace Collins!": Grace was Maya's adoptive mother who died eight years ago (Ep1), but Derek's accusation presents her death as a recent murder and Maya as implicated, which is new and unexplained.

## Flags on clean set

- **Ep1 vs Ep7** [high/timeline] "Who's Sam?" vs "It stopped being a contract for me the night you threw coffee on me.": Ep1 shows Adrian and Maya meeting at the diner, where he leaves a tip and asks 'Who's Sam?', with no coffee-throwing incident. Ep7 says she threw coffee on him the night they met, which conflicts with the established first meeting.
- **Ep4 vs Ep10** [high/timeline] "I was four. I don't remember anything before that." vs "A con artist doesn't carry her father's photograph for twenty years without knowing it.": Maya was found at four and is now 24, so she could have carried the locket for at most about twenty years only if counted from age four; however Richard says he put the locket on her himself before she was lost, so the span would be roughly 20 years. This is consistent, but the established account that Grace found her wearing it conflicts with nothing here. No real conflict on duration.
- **Ep6 vs Ep7** [medium/timeline] "Friday. Tick tock." vs "She's been blackmailing Maya for a week.</br>": Ep5 and Ep6 show the blackmail beginning only recently, with a Friday deadline and a few days between the contract photographing and the confrontation. A week of threatening texts is hard to fit with that timeline.
