# AI Game Player: Performance Dashboard (for James)
Updated each learning cycle by AGP's script (tools/dashboard.py), with no chat or Grok turns. Live Clash Royale is **paused** until you say go in the AGP chat. Until then, the "current" column comes from offline sources: the replay sim, VOD learning, and recorded matches.
Baseline is the frozen snapshot of 2026-11-01 01:30 PT (agp/v4/METRICS.md). Full history is in agp/v4/METRICS_HISTORY.jsonl, one row per cycle.

## How to read it
- **▲ green** = better than baseline, **▼ red** = worse, **=** = within noise.
- The trend shows the last 5 cycles.
- The **Source** column says where each number came from: LIVE (real ladder matches), SIM (replays of saved matches / pro VODs), or LOG (recorded match data). Only LIVE numbers prove ladder strength. SIM numbers show whether the skills are improving before you greenlight.
- A change is kept only if it beats baseline under the gates in ops/QUALITY_DIRECTIVES_AI_GAME_PLAYER_V2.md. Every reverted change is listed as a REVERT row in the history.

## KPIs
| # | KPI | What it means | Baseline (from disk) | Target | Source now |
|---|---|---|---|---|---|
| 1 | Win rate | Ladder wins ÷ decided matches | **42.6%** (83–112); matches_v3 log 44.1% (n=281) | ≥55% over 100 live | LOG (LIVE after go) |
| 2 | Spell hit rate | Share of spells with an enemy in radius at impact | **48%** (36/75) | ≥60% offline, then live | SIM |
| 3 | Elixir waste | Seconds per match sitting at full elixir | **~8.9 s/match** | ≤4 s | SIM |
| 4 | Ladder threat coverage | Share of today's top-20 meta cards we have a proven counter plan for | **20%** (4/20) | ≥60% | LOG + VOD |
| 5 | Counter success | Share of counter plays that won the exchange (strict label: tower damage avoided + elixir trade ≥0) | 92.9% lenient label (**not trusted**); strict baseline set in cycle 1 | strict ≥70% | SIM/LIVE |
| 6 | Upgrades per day (deck cards) | Upgrades to cards in the current deck | **0** deck cards (33 non-deck total) | ≥1/day while gold > reserve | LIVE only |
| 7 | Reward claim rate | Claimed ÷ claimable rewards per session | **not measurable** (no "claimable" count was logged); the new RewardFSM logs it | ≥95% | LIVE only |
| 8 | Pro plays learned | Card placements extracted from top-ladder VODs | **221** (1 VOD; batch running) | ≥2,000 across ≥3 meta decks | VOD |
| 9 | Own-match sample | Our recorded matches available for training/scoring | **281** logged matches; 13 bot demos used for imitation | grows with live play | LOG |
| + | Decision match vs pros | How often our planner picks the same card/tile as the pro in replayed situations | set in cycle 1 | rising | SIM |
| + | Imitation accuracy (within-1 tile) | Model's placement accuracy on held-out data | **0.23–0.31** | ≥0.45 | SIM |

KPIs 6 and 7 stay blank until you greenlight, because they need the live game.

## Current snapshot (auto-regenerated below this line)
<!-- DASHBOARD:BEGIN -->
| KPI | Baseline | Current | Δ | Trend (last 5) | Source | Cycle |
|---|---|---|---|---|---|---|
| Win rate (LIVE/LOG) | 42.6% (n=195) | null | – | null → null → null → null → null | – | 25 (REVERT) |
| Win rate (SIM) | null | null | – | null → null → null → null → null | – | 25 (REVERT) |
| Wasted spells/match | 0.22 (n=206) @c1 | 0.22 (n=206) | = +0 | 0.22 → 0.22 → 0.22 → 0.22 → 0.22 | SIM | 25 (REVERT) |
| Placement vs pros (heatmap cos) | 45.0% (n=905) @c1 | 57.8% (n=5808) | ▲ +12.8 pp | 58.3% → 58.3% → 58.0% → 58.0% → 57.8% | SIM+VOD | 25 (REVERT) |
| Deck vs meta threats | 20.0% (n=20) @c1 | 60.0% (n=20) | ▲ +40.0 pp | 65.0% → 60.0% → 65.0% → 55.0% → 60.0% | LOG+WEB | 25 (REVERT) |
| Spell hit | 48.0% (n=75) | 60.2% (n=93) | ▲ +12.2 pp | 60.2% → 60.2% → 60.2% → 60.2% → 60.2% | SIM | 25 (REVERT) |
| Elixir waste s/match | 8.9 (n=263) | 1.96 (n=60) | ▲ -6.94 | 2.04 → 2.98 → 2.06 → 2.33 → 1.96 | SIM | 25 (REVERT) |
| Threat coverage | 20.0% (n=20) | 85.0% (n=20) | ▲ +65.0 pp | 85.0% → 85.0% → 85.0% → 85.0% → 85.0% | LOG+VOD | 25 (REVERT) |
| Counter success (strict) | 66.4% (n=3599) @c1 | 67.3% (n=4254) | = +0.9 pp | 66.4% → 66.5% → 66.8% → 67.3% → 67.3% | LOG | 25 (REVERT) |
| Deck upgrades/day | 0 | null | – | null → null → null → null → null | – | 25 (REVERT) |
| Claim rate | null | null | – | null → null → null → null → null | – | 25 (REVERT) |
| Pro plays | 221 | 5808 | ▲ +5587 | 4495 → 4505 → 4711 → 5494 → 5808 | VOD | 25 (REVERT) |
| Own matches | 281 | 339 | ▲ +58 | 281 → 287 → 307 → 337 → 339 | LOG | 25 (REVERT) |
| Decision match vs pros | 57.8% (n=325) @c1 | 55.2% (n=2712) | ▼ -2.6 pp | 55.4% → 55.1% → 54.9% → 55.3% → 55.2% | SIM | 25 (REVERT) |
| Imitation within-1 | 0.23–0.31 | 49.6% | – | 49.6% → 49.6% → 49.6% → 49.6% → 49.6% | – | 25 (REVERT) |

_Tests: 65/65 · last change: agp_loop pass (live) · 2026-11-02T12:21:02-08:00_
<!-- DASHBOARD:END -->
Chart: agp/v4/dashboard.png (matplotlib, one small panel per KPI, baseline drawn as a dashed line).
