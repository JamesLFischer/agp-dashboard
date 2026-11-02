# AGP: Ready-to-Play gate
Live Clash Royale stays **PAUSED**. It resumes only when BOTH hold: (1) James says go in the AI Game Player chat, and (2) every gate below passes on the latest METRICS_HISTORY row. Checked automatically each cycle by `tools/ready_check.py`; nobody asks for go early.

| # | Gate | KPI key | Need | Baseline | Source |
|---|---|---|---|---|---|
| 1 | Spell hit on held-out offline clips | spell_hit | ≥ 60% | 48% (36/75); offline eval 49.5% (102/206) | SIM |
| 2 | Elixir waste | elixir_waste_s | ≤ 4 s/match | 8.9 (LOG); sim 2.04 | SIM |
| 3 | Ladder threat coverage (strict counter plans) | threat_coverage | ≥ 60% of top-20 | 20% | LOG+VOD |
| 4 | Strict counter success (trustworthy labels) | counter_success_strict | ≥ 70% | set in cycle 1 | LOG |
| 5 | Placement/imitation within-1 | bc_within1 | ≥ 0.45 | 0.23–0.31 | SIM |
| 6 | Deck-build meta alignment | deck_meta_alignment | ≥ 60% of top threats | set in cycle 1 | LOG+WEB |
| 7 | Tests green with leak gate | tests_pass | all pass | 65/65 now (60/65 at baseline) | SIM |
| 8 | Pro plays | pro_plays | ≥ 2,000 across ≥ 3 meta decks, OR a plateau with KEEP cycles | 221 | VOD |
| 9 | Sustained improvement | decision | ≥ 3 KEEP cycles, no regression vs baseline | 0 | history |

After go, the LIVE confirmation is tracked separately on the dashboard and never mixed with SIM: win rate ≥55% over 100 live matches, claim rate ≥95%, ≥1 deck upgrade/day.

## The one READY message (written by ready_check.py to READY_MESSAGE.md when every gate passes)
```
AGP READY TO PLAY (proposal, cycle N). All offline gates pass.
- <gate>: <value> (need <threshold>)   x9
Scorecard: scorecards/cycle_NNN.md · Dashboard: PERFORMANCE_DASHBOARD.md + dashboard.png
Evidence: evidence/cycle_NNN/contact_sheet.jpg
Live stays paused until James says go in the AI Game Player chat.
```
Until then, offline learning continues around the clock.
