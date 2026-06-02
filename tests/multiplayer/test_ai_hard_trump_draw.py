"""HardStrategy trump-drawing ("Trumpf ziehen") leading-logic tests.

Sub-project C extension. Covers the LEADING branch of
`HardStrategy.pick_card` in trump modes only:

  A. Draw trump — lead highest trump while an opponent may still hold trump.
  B. Both opponents void in trump — stop leading trump; lead a guaranteed
     winner, else an opponent-shown side suit (so partner can trump in).
  C. Void-in-trump detection flips only the discarding opponent.
  D. Trick reconstruction resets across 4-card boundaries.

Following-suit behaviour is unchanged and is covered by the existing
`tests/multiplayer/test_ai_strategies.py` `test_hard_follow_*` tests.

Card codes follow the repo scheme (see ``SUIT_PREFIX`` / ``RANK_SUFFIX`` in
``ausbau.game_session``): Eicheln=E, Rosen=R, Schellen=SE, Schilten=SI; rank
suffixes 6 7 8 9 B U O K A (low→high). So the Schellen King is ``SEK``, the
Rosen Six ``R6``, the Schellen Under (top trump) ``SEU``.
"""
import pytest

from Cards_refactored import Play, SUITS, create_card
from ausbau.ai_strategies import HardStrategy
from ausbau.game_session import RANK_SUFFIX


# Map a code suffix ('A','K',…,'6') back to its 1-based rank index, the form
# create_card expects. Mirrors the helper in test_ai_strategies.py.
_INVERSE_RANK = {v: k for k, v in RANK_SUFFIX.items()}


def _set_hand(play, position, suit_to_suffixes):
    """Stuff a Play position's hand with specific cards by suit + code suffix."""
    hand = {s: [] for s in SUITS}
    for suit, suffixes in suit_to_suffixes.items():
        for suffix in suffixes:
            hand[suit].append(create_card(_INVERSE_RANK[suffix], suit))
    setattr(play, position, hand)


def _make(position, operator, suit_to_suffixes):
    play = Play(spiel=1)
    play.operator = operator
    _set_hand(play, position, suit_to_suffixes)
    strat = HardStrategy(position)
    strat.on_spiel_start(play)
    return play, strat


# comps's partner is compn; opponents are compo and compe.
def _drive_both_opponents_void(strat):
    """One trump-led trick where both opponents discard non-trump (Schellen
    trump). After this, _opp_void_trump is True for both compo and compe."""
    strat.on_card_played("comps", "SEK")   # trump led by us
    strat.on_card_played("compo", "R6")    # opponent discards → void; shows Rosen
    strat.on_card_played("compn", "SEA")   # partner follows trump
    strat.on_card_played("compe", "E6")    # opponent discards → void; shows Eicheln
    # 4 cards → running trick reset internally.


# ── Rule A: draw trump (lead highest trump) ──────────────────────────────────

def test_leads_highest_trump_fresh_spiel():
    # Schellen trump; comps holds three trumps. Highest by card.trumpf among
    # {Sechs=10, Acht=12, Koenig=15} is the Koenig (SEK).
    play, strat = _make("comps", "Schellen", {"Schellen": ["6", "K", "8"]})
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    assert action == {"type": "play_card", "card": "SEK"}


def test_drawing_takes_priority_over_guaranteed_side_winner():
    # Holds the trump Under (top trump, SEU) AND an off-suit Ass (RA) that
    # would also win. While drawing, the trump lead wins out.
    play, strat = _make("comps", "Schellen",
                        {"Schellen": ["U"], "Rosen": ["A"]})
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    assert action == {"type": "play_card", "card": "SEU"}


def test_keeps_drawing_while_one_opponent_may_hold_trump():
    # Only ONE opponent has shown void; the other might still hold trump.
    play, strat = _make("comps", "Schellen",
                        {"Schellen": ["6"], "Rosen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    strat.on_card_played("comps", "SEK")
    strat.on_card_played("compo", "R6")    # void
    strat.on_card_played("compn", "SEA")   # partner follows
    strat.on_card_played("compe", "SE9")   # opponent follows trump (not void)
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    # compe not void → keep drawing → lead our remaining trump SE6.
    assert action == {"type": "play_card", "card": "SE6"}


# ── Rule B: both opponents void → stop drawing ───────────────────────────────

def test_stops_trump_and_leads_guaranteed_winner():
    # After drawing, lead the guaranteed off-suit winner (Rosen Ass) rather
    # than the low trump.
    play, strat = _make("comps", "Schellen",
                        {"Schellen": ["6"], "Rosen": ["A"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    _drive_both_opponents_void(strat)
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    assert action == {"type": "play_card", "card": "RA"}


def test_stops_trump_and_leads_opponent_shown_side_suit():
    # No guaranteed winner; dump into a non-trump suit an opponent has shown
    # so partner (still holding trump) can trump in. Never lead the trump Six.
    play, strat = _make("comps", "Schellen",
                        {"Schellen": ["6"], "Rosen": ["6"], "Eicheln": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    _drive_both_opponents_void(strat)
    # compo showed Rosen, compe showed Eicheln while driving the voids.
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    assert action["type"] == "play_card"
    assert action["card"] in {"R6", "E6"}
    assert action["card"] != "SE6"  # never the trump


def test_both_void_unshown_suit_never_leads_trump():
    # Regression: both opponents void, no guaranteed winner, and our only
    # non-trump card is in a suit NO opponent has shown (so the shown-suit
    # dump filter finds nothing). The fallback must still pick the non-trump
    # card, never re-open with trump. compo shows Rosen, compe shows Eicheln
    # while driving voids; our side suit is Schilten (unshown).
    play, strat = _make("comps", "Schellen",
                        {"Schellen": ["K", "9"], "Schilten": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    _drive_both_opponents_void(strat)
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    assert action == {"type": "play_card", "card": "SI6"}


def test_both_void_all_trump_hand_leads_trump():
    # Edge: both opponents void AND our whole hand is trump — no non-trump card
    # to lead, so leading trump is the only legal option.
    play, strat = _make("comps", "Schellen", {"Schellen": ["6", "7"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    _drive_both_opponents_void(strat)
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    assert action["type"] == "play_card"
    assert action["card"] in {"SE6", "SE7"}


def test_does_not_lead_trump_when_both_void():
    # Even with two trumps in hand, never open with trump once drawn.
    play, strat = _make("comps", "Schellen",
                        {"Schellen": ["6", "7"], "Rosen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    _drive_both_opponents_void(strat)
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    # compo showed Rosen → dump R6 (the only opponent-shown non-trump card).
    assert action == {"type": "play_card", "card": "R6"}


# ── Rule C: no trump in hand → falls through to B ─────────────────────────────

def test_no_trump_in_hand_leads_guaranteed_winner():
    play, strat = _make("comps", "Schellen",
                        {"Rosen": ["A"], "Eicheln": ["6"]})
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    # No trump → rule A can't fire; RA is a guaranteed winner.
    assert action == {"type": "play_card", "card": "RA"}


# ── Void-in-trump detection ──────────────────────────────────────────────────

def test_only_discarding_opponent_flagged_void():
    play, strat = _make("comps", "Schellen", {"Schellen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    strat.on_card_played("comps", "SEK")   # trump led by us
    strat.on_card_played("compo", "R6")    # void
    strat.on_card_played("compn", "SEA")   # partner follows
    strat.on_card_played("compe", "SE9")   # opponent follows trump
    assert strat._opp_void_trump["compo"] is True
    assert strat._opp_void_trump["compe"] is False
    # Partner is never an opponent key.
    assert "compn" not in strat._opp_void_trump


def test_partner_discard_does_not_flag_opponent():
    play, strat = _make("comps", "Schellen", {"Schellen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    strat.on_card_played("compo", "SEK")   # opponent leads trump
    strat.on_card_played("compn", "R6")    # partner discards — must be ignored
    assert strat._opp_void_trump["compo"] is False
    assert strat._opp_void_trump["compe"] is False


def test_non_trump_lead_does_not_flag_void():
    play, strat = _make("comps", "Schellen", {"Schellen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    strat.on_card_played("compo", "RA")    # opponent leads Rosen (non-trump)
    strat.on_card_played("compe", "E6")    # can't follow Rosen — not a void
    assert strat._opp_void_trump["compe"] is False


# ── Trick reconstruction ─────────────────────────────────────────────────────

def test_trick_resets_after_four_cards():
    play, strat = _make("comps", "Schellen", {"Schellen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    strat.on_card_played("comps", "SEK")
    strat.on_card_played("compo", "R6")
    strat.on_card_played("compn", "SEA")
    strat.on_card_played("compe", "SE9")
    assert strat._running_trick == []      # reset after the 4th card

    # New trick: the first card defines the new lead.
    strat.on_card_played("compe", "EA")
    assert len(strat._running_trick) == 1
    assert strat._running_trick[0][0] == "compe"


def test_shown_suits_tracked_for_opponents_not_self():
    play, strat = _make("comps", "Schellen", {"Schellen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    strat.on_card_played("compe", "RA")    # opponent shows Rosen
    strat.on_card_played("comps", "SE6")   # our own play (not tracked)
    assert "Rosen" in strat._opp_shown_suits["compe"]
    assert "Schellen" not in strat._opp_shown_suits.get("comps", set())


# ── Per-spiel state reset ────────────────────────────────────────────────────

def test_on_spiel_start_resets_trump_draw_state():
    play, strat = _make("comps", "Schellen", {"Schellen": ["6"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator
    strat.on_card_played("comps", "SEK")
    strat.on_card_played("compo", "R6")    # flips compo void, populates trick
    assert strat._opp_void_trump["compo"] is True
    # New spiel resets everything.
    strat.on_spiel_start(play)
    assert strat._opp_void_trump == {"compo": False, "compe": False}
    assert strat._running_trick == []
    assert all(v == set() for v in strat._opp_shown_suits.values())


# ── Trump stopping when all outstanding trumps played ──────────────────────────

def test_stops_trump_when_all_outstanding_trumps_played():
    # If all outstanding trumps (outside our hand) are gone/played,
    # the AI must stop leading trump, even if no opponent has been
    # flagged void through a non-trump discard on a trump lead.
    # Schellen trump. comps holds Schellen 6, plus Rosen Ass.
    play, strat = _make("comps", "Schellen",
                        {"Schellen": ["6"], "Rosen": ["A"]})
    strat.pick_card(play, lead_suit=None, trick_so_far=[])  # cache operator

    # Simulate that all other Schellen (trumps) were played.
    # Initially 8 trumps outside our hand: U, 9, A, K, O, B, 8, 7.
    # Let's say all of them are played by other players.
    for code in ["SEU", "SE9", "SEA", "SEK", "SEO", "SEB", "SE8", "SE7"]:
        strat.on_card_played("compe", code)

    # Outstanding Schellen (trumps) is now empty
    assert len(strat._remaining_by_suit["Schellen"]) == 0

    # We are leading. Since all outstanding trumps are gone, the AI should NOT
    # lead its remaining trump (SE6). Instead, it should lead the guaranteed
    # winner (Rosen Ass, RA).
    action = strat.pick_card(play, lead_suit=None, trick_so_far=[])
    assert action == {"type": "play_card", "card": "RA"}


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
