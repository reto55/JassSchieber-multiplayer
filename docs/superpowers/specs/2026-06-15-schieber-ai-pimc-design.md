# Sub-project D — Hard-AI PIMC trump-draw engine

**Date:** 2026-06-15
**Status:** Design (brainstorm output, pending implementation plan)
**Predecessor:** Tier 1 of the trump-draw refinement (commit `41852bd` —
"Hard AI stops leading trump at one outstanding when it lacks the boss").
This spec is **Tier 2**.

## 1. Purpose

The Hard AI's trump-leading decisions are currently a hand-crafted precedence
(`HardStrategy._lead` rule A / rule B) backed by ruff-blind heuristics. Tier 1
added a sound "stop drawing at one outstanding trump when we lack the boss"
rule, but explicitly left a residual: `_is_guaranteed_winner` does not know
whether a "winning" non-trump card can be **ruffed** by an opponent's trump.

Sub-project D replaces the leading decision in trump modes with a
**Perfect-Information Monte Carlo (PIMC)** engine that plays the odds: sample
deals consistent with everything observed, roll each out to the end of the
spiel, and lead the card with the best **expected** team score. This is the
"partner inference / minimax" direction CLAUDE.md filed under sub-project D.

### Explicit decisions carried in from brainstorming

| Decision | Choice |
|----------|--------|
| Scope of consumers | Engine + **trump-draw leading decision only**. No-trump modes, following-play, and Easy/Medium are out of scope. |
| Inference model | **Probabilistic** (play the odds), not a sound constraint solver. |
| Probability calc | **Monte Carlo** over feasible deals. |
| Decision rule | **Full expected-value maximization** (PIMC). |
| Per-deal evaluation | **Heuristic rollout** to spiel end using the existing `pick_card` as the playout policy. |
| Execution model | **Synchronous, time-boxed**, with heuristic fallback. |

## 2. Non-goals

- No double-dummy / alpha-beta solver (the rollout evaluator can be swapped for
  one later behind the same interface).
- No async/executor offload (documented upgrade path only).
- No change to no-trump (`Oben`/`Unten`) modes, the following-play logic, or the
  Easy/Medium strategies.
- No deletion of the Tier-1 sound rule — it is retained as the fallback.

## 3. Architecture

New standalone module `ausbau/ai_pimc.py`, independent of `HardStrategy`
internals. It takes a plain state struct + candidate leads and returns a card,
so it is unit-testable in isolation.

```
ausbau/ai_pimc.py
  EngineState           ← plain data: own hand, unseen cards, per-player hand
                          sizes, per-player per-suit void flags, operator,
                          partner/opponent positions, whose lead.
  DealSampler           ← samples full assignments of unseen cards to the three
                          other hands, honoring voids + capacities + Under
                          holdback. Seedable RNG.
  rollout(deal, lead)   ← plays the spiel to completion from the current
                          position with `lead` led, using existing heuristic
                          pick_card as the playout policy for all four hands.
                          Returns our team's points.
  pimc_choose_lead(state, candidate_leads, deadline, rng, *, min_samples, n)
                        ← averages rollout score per candidate lead across
                          samples; returns the max-EV card (or None to signal
                          "fall back to heuristic").
```

`HardStrategy` owns none of the engine logic; it only adapts its tracking into
`EngineState` and calls `pimc_choose_lead`.

## 4. Components

### 4.1 EngineState assembly (in `HardStrategy`)

Requires **generalizing** the existing per-spiel tracking:

- **Per-player remaining hand size** — new. Decrement on each `on_card_played`,
  accounting for current-trick position. Reset in `on_spiel_start`. Must also be
  seeded correctly when a strategy is constructed mid-spiel (see CLAUDE.md note
  on seeding AI tracking at mid-spiel construction — extend it to the new state).
- **Per-player per-suit void flags** — generalize the existing trump-only
  `_opp_void_trump` to all four suits, tracked for *all three* other players
  (partner included; partner can also be void). A flag sets when a player fails
  to follow the led suit.
- **Under-holdback nuance** — when a player discards a non-trump on a trump
  lead, record "no trump except possibly the Under" rather than full trump-void.

The unseen-card set is `36 − own − played` (derivable from existing
`_remaining_by_suit` plus own hand).

### 4.2 DealSampler

Constrained shuffle of the unseen cards into the three other hands:

- Candidate holders for a card = players not void in its suit. For trump cards,
  a player flagged "no trump except Under" is a candidate **only** for the trump
  Under, never for other trumps.
- Assign respecting each player's remaining capacity; on a dead-end (no legal
  holder for a remaining card), restart/repair with the seeded RNG.
- Every emitted deal satisfies all observed constraints. The distribution
  approximates uniform over feasible deals; the mild bias from constructive
  assignment is accepted for EV purposes and flagged as a future refinement
  (e.g., rejection sampling or KM-weighted assignment) if it proves to matter.

### 4.3 rollout

From the current position, with the AI's `lead` card played first, continue the
spiel to completion. Every seat (including the AI and partner) plays via the
existing heuristic `pick_card` (the Medium/Hard policy), reusing the real
trick-resolution code path. Returns the AI team's accumulated points for the
remainder of the spiel. Deterministic given a fixed deal and policy.

### 4.4 pimc_choose_lead

```
for each candidate lead L:
    score[L] = 0; samples[L] = 0
loop until deadline or n samples reached:
    deal = sampler.sample()
    for each candidate lead L:
        score[L] += rollout(deal, L); samples[L] += 1
        if past deadline: break
if total completed samples < min_samples: return None   # → heuristic fallback
return argmax_L (score[L] / samples[L])
```

Time-boxed; returns best-so-far once `min_samples` is met. `None` signals the
caller to use the heuristic `_lead`.

## 5. Integration into `HardStrategy._lead`

```
def _lead(self, play, valid_cards):
    operator = play.operator
    if operator not in SUITS:
        return self._lead_legacy(play, valid_cards)        # no-trump unchanged
    if self._pimc_enabled:
        state = self._build_engine_state(play)
        pick = pimc_choose_lead(state, valid_cards, deadline=..., rng=self._rng,
                                min_samples=..., n=...)
        if pick is not None:
            return {"type": "play_card", "card": card_to_code(pick)}
    return self._lead_heuristic(play, valid_cards)          # = today's rule A/B
                                                            #   incl. Tier-1 stop
```

- PIMC **supersedes** rule A/B and the Tier-1 stop for the trump-mode leading
  decision when it runs.
- The current rule A/B body (including the Tier-1 lone-trump lack-boss stop) is
  renamed `_lead_heuristic` and kept as the fallback.
- `_pimc_enabled` defaults on for Hard; gives a kill-switch and a test hook.

## 6. Performance & time-boxing

- Deadline ~100–150 ms per leading decision (tunable module constant).
- `n` ~ 50–100 samples; cost ≈ `n × |candidate_leads| × rollout`.
- Rollout is ≤ 8 remaining tricks × 4 plays of heuristic `pick_card` — cheap.
- Deadline checked between samples; best-so-far returned at `min_samples`, else
  `None` → heuristic fallback.
- RNG injected and seedable for deterministic tests; entropy-seeded in prod.
- Risk: many concurrent rooms blocking the synchronous WS event loop. Mitigated
  by the time-box; **executor offload (`run_in_executor`) is the documented
  upgrade path**, built only if profiling shows real stalls.

## 7. Testing

- **DealSampler** (seeded): emitted deals never violate voids or hand sizes; a
  lone trump Under can land with a trump-discarder but no other trump can;
  per-player capacities exact.
- **Convergence:** under controlled constraints, estimated frequencies
  (P(opponent void in S), P(ruff)) approach analytic values at large `n`.
- **rollout:** fixed deal + policy → fixed score; total spiel points conserved.
- **pimc_choose_lead** (seeded, injected deals or small `n`):
  - Tier-1 scenario (1 trump out, lack boss) → PIMC prefers a non-trump lead.
  - Strong-trump scenario (2+ out, AI holds top trumps) → PIMC leads trump.
  - Same seed → same choice (determinism).
- **Fallback/regression:** `deadline=0` or `_pimc_enabled=False` → heuristic
  `_lead`; existing trump-draw, no-trump, and following-play tests still pass.

## 8. Known limitations (accepted for this version)

- **Strategy fusion / non-locality:** PIMC with independent per-deal rollouts
  cannot represent information-hiding or signalling and can misvalue plays whose
  worth depends on hidden state across deals. Accepted for v1; a true
  inference/minimax layer is future work.
- **Rollout-policy ceiling:** PIMC strength is bounded by the heuristic playout
  policy. Acceptable for v1; swap in a stronger evaluator later.
- **Sampler bias:** constructive assignment is not exactly uniform over feasible
  deals. Accepted; refine only if it measurably hurts decisions.

## 9. File-level change summary

- **New:** `ausbau/ai_pimc.py` (engine), `tests/multiplayer/test_ai_pimc.py`.
- **Modified:** `ausbau/ai_strategies.py` — generalized tracking
  (`on_spiel_start` / `on_card_played`), `_build_engine_state`, `_lead`
  refactor (`_lead_heuristic` + PIMC branch), `_rng`/`_pimc_enabled` fields,
  docstring.
- **Docs:** CLAUDE.md HardStrategy bullet (note PIMC supersedes the heuristic
  lead in trump modes; Tier-1 retained as fallback). **Not** a game-rules
  change — `schieber-game-rules` skill untouched.
