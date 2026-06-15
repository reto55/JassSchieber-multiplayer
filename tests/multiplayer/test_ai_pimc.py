"""PIMC engine (ausbau/ai_pimc.py) unit tests — seeded and deterministic."""
import random
import pytest

from Cards_refactored import SUITS, create_card, Under
from ausbau.game_session import RANK_SUFFIX, card_to_code, code_to_card, PLAYERS
from ausbau import ai_pimc

_INVERSE_RANK = {v: k for k, v in RANK_SUFFIX.items()}


def _hand(suit_to_suffixes):
    """Build a {suit: [Card,...]} hand dict from {suit: 'AKO...'} suffixes."""
    h = {s: [] for s in SUITS}
    for suit, suffixes in suit_to_suffixes.items():
        for suf in suffixes:
            h[suit].append(create_card(_INVERSE_RANK[suf], suit))
    return h


def test_engine_state_holds_fields():
    state = ai_pimc.EngineState(
        me="comps",
        operator="Schellen",
        partner={"comps": "compn", "compn": "comps", "compo": "compe", "compe": "compo"},
        folger={"comps": "compo", "compo": "compn", "compn": "compe", "compe": "comps"},
        my_hand=_hand({"Schellen": "AK"}),
        others=["compo", "compn", "compe"],
        hand_sizes={"compo": 1, "compn": 1, "compe": 1},
        voids={"compo": set(), "compn": set(), "compe": set()},
        no_trump_except_under=set(),
        unseen=[create_card(_INVERSE_RANK["O"], "Schellen")],
    )
    assert state.me == "comps"
    assert state.operator == "Schellen"
    assert state.others == ["compo", "compn", "compe"]
    assert len(state.unseen) == 1


def _basic_state(my_hand, others, hand_sizes, voids=None,
                 no_trump_except_under=None, unseen=None,
                 operator="Schellen", me="comps"):
    partner = {"comps": "compn", "compn": "comps", "compo": "compe", "compe": "compo"}
    folger = {"comps": "compo", "compo": "compn", "compn": "compe", "compe": "comps"}
    return ai_pimc.EngineState(
        me=me, operator=operator, partner=partner, folger=folger,
        my_hand=my_hand, others=others, hand_sizes=hand_sizes,
        voids=voids or {p: set() for p in others},
        no_trump_except_under=no_trump_except_under or set(),
        unseen=unseen or [],
    )


def test_sampler_respects_capacities_and_partitions_unseen():
    # 2 unseen Schellen cards, two others each needing exactly 1 card.
    unseen = [create_card(_INVERSE_RANK["O"], "Schellen"),
              create_card(_INVERSE_RANK["U"], "Schellen")]
    state = _basic_state(
        my_hand=_hand({"Schellen": "AK"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        unseen=unseen,
    )
    sampler = ai_pimc.DealSampler(state)
    rng = random.Random(0)
    deal = sampler.sample(rng)
    # Each other gets exactly its capacity; all unseen placed exactly once.
    assert sum(len(cs) for h in deal.values() for cs in h.values()) == 2
    assert sum(len(cs) for cs in deal["compo"].values()) == 1
    assert sum(len(cs) for cs in deal["compe"].values()) == 1
    placed = {card_to_code(c) for h in deal.values() for cs in h.values() for c in cs}
    assert placed == {"SEO", "SEU"}


def test_sampler_respects_voids():
    unseen = [create_card(_INVERSE_RANK["6"], "Rosen"),
              create_card(_INVERSE_RANK["7"], "Rosen")]
    state = _basic_state(
        my_hand=_hand({"Schellen": "A"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        voids={"compo": {"Rosen"}, "compe": set()},
        unseen=unseen,
        operator="Schellen",
    )
    sampler = ai_pimc.DealSampler(state)
    # compo is void in Rosen, but capacity forces 1 Rosen each -> infeasible.
    with pytest.raises(ai_pimc.SamplingError):
        for _ in range(50):
            sampler.sample(random.Random(_))  # try several seeds


def test_sampler_under_holdback_only_under_to_voided_player():
    # compo discarded on a trump lead -> may hold ONLY the trump Under.
    under = create_card(_INVERSE_RANK["U"], "Schellen")   # SEU, the Under
    nine = create_card(_INVERSE_RANK["9"], "Schellen")    # SE9, not an Under
    state = _basic_state(
        my_hand=_hand({"Eicheln": "A"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        no_trump_except_under={"compo"},
        unseen=[under, nine],
        operator="Schellen",
    )
    sampler = ai_pimc.DealSampler(state)
    seen_under_with_compo = False
    for s in range(40):
        deal = sampler.sample(random.Random(s))
        compo_codes = {card_to_code(c) for cs in deal["compo"].values() for c in cs}
        # compo must never hold SE9 (a non-Under trump).
        assert "SE9" not in compo_codes
        if "SEU" in compo_codes:
            seen_under_with_compo = True
    assert seen_under_with_compo  # the Under CAN land with compo


def test_sampler_is_deterministic_under_seed():
    unseen = [create_card(_INVERSE_RANK["O"], "Schellen"),
              create_card(_INVERSE_RANK["U"], "Schellen")]
    state = _basic_state(
        my_hand=_hand({"Schellen": "AK"}),
        others=["compo", "compe"],
        hand_sizes={"compo": 1, "compe": 1},
        unseen=unseen,
    )
    sampler = ai_pimc.DealSampler(state)
    d1 = sampler.sample(random.Random(123))
    d2 = sampler.sample(random.Random(123))
    norm = lambda d: {p: sorted(card_to_code(c) for cs in h.values() for c in cs)
                      for p, h in d.items()}
    assert norm(d1) == norm(d2)


def test_rollout_is_deterministic():
    # 2-card endgame: I lead, everyone has 2 cards. Schellen trump.
    my_hand = _hand({"Schellen": "A", "Eicheln": "6"})  # SEA (boss), E6
    others = ["compo", "compn", "compe"]
    deal = {
        "compo": _hand({"Schellen": "9", "Rosen": "6"}),
        "compn": _hand({"Eicheln": "A", "Rosen": "7"}),   # partner
        "compe": _hand({"Schellen": "U", "Eicheln": "7"}),
    }
    state = _basic_state(
        my_hand=my_hand, others=others,
        hand_sizes={p: 2 for p in others},
        unseen=[c for h in deal.values() for cs in h.values() for c in cs],
        operator="Schellen", me="comps",
    )
    lead = create_card(_INVERSE_RANK["A"], "Schellen")    # lead SEA
    s1 = ai_pimc.rollout(state, deal, lead)
    s2 = ai_pimc.rollout(state, deal, lead)
    assert s1 == s2
    assert isinstance(s1, int)


def test_rollout_points_are_bounded_and_nonnegative():
    my_hand = _hand({"Schellen": "A", "Eicheln": "6"})
    others = ["compo", "compn", "compe"]
    deal = {
        "compo": _hand({"Schellen": "9", "Rosen": "6"}),
        "compn": _hand({"Eicheln": "A", "Rosen": "7"}),
        "compe": _hand({"Schellen": "U", "Eicheln": "7"}),
    }
    state = _basic_state(
        my_hand=my_hand, others=others,
        hand_sizes={p: 2 for p in others},
        unseen=[c for h in deal.values() for cs in h.values() for c in cs],
        operator="Schellen", me="comps",
    )
    lead = create_card(_INVERSE_RANK["A"], "Schellen")
    pts = ai_pimc.rollout(state, deal, lead)
    assert 0 <= pts <= 300   # sanity: never negative, never absurd


def _endgame_state():
    """I hold the boss trump (SEA) and a losing side card (E6). One trump
    (SE9) is outstanding with an OPPONENT (compo), who is void in Eicheln so
    they would ruff an Eicheln lead. Leading the boss trump should score
    better in EV than leading E6 into the ruff."""
    my_hand = _hand({"Schellen": "A", "Eicheln": "6"})   # SEA boss, E6
    others = ["compo", "compn", "compe"]
    state = _basic_state(
        my_hand=my_hand, others=others,
        hand_sizes={"compo": 2, "compn": 2, "compe": 2},
        voids={"compo": {"Eicheln"}, "compn": set(), "compe": set()},
        unseen=[
            create_card(_INVERSE_RANK["9"], "Schellen"),   # SE9 (opp trump)
            create_card(_INVERSE_RANK["6"], "Rosen"),
            create_card(_INVERSE_RANK["A"], "Eicheln"),
            create_card(_INVERSE_RANK["7"], "Rosen"),
            create_card(_INVERSE_RANK["K"], "Eicheln"),
            create_card(_INVERSE_RANK["7"], "Eicheln"),
        ],
        operator="Schellen", me="comps",
    )
    return state


def test_pimc_prefers_boss_trump_over_ruffable_side_lead():
    state = _endgame_state()
    leads = state.my_hand["Schellen"] + state.my_hand["Eicheln"]  # [SEA, E6]
    rng = random.Random(7)
    pick = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=5.0, rng=rng, min_samples=5, n=60)
    assert pick is not None
    assert card_to_code(pick) == "SEA"   # lead the boss trump, not E6


def test_pimc_returns_none_when_below_min_samples():
    state = _endgame_state()
    leads = state.my_hand["Schellen"] + state.my_hand["Eicheln"]
    # deadline_s=0 -> no samples complete -> fallback signal.
    pick = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=0.0, rng=random.Random(1), min_samples=5, n=60)
    assert pick is None


def test_pimc_is_deterministic_under_seed():
    state = _endgame_state()
    leads = state.my_hand["Schellen"] + state.my_hand["Eicheln"]
    p1 = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=5.0, rng=random.Random(42), min_samples=5, n=40)
    p2 = ai_pimc.pimc_choose_lead(
        state, leads, deadline_s=5.0, rng=random.Random(42), min_samples=5, n=40)
    assert card_to_code(p1) == card_to_code(p2)


# ── Task 5: HardStrategy generalized tracking ────────────────────────────
from Cards_refactored import Play
from ausbau.ai_strategies import HardStrategy


def _make_strat(position, operator, my_suit_to_suffixes):
    play = Play(spiel=1)
    play.operator = operator
    hand = {s: [] for s in SUITS}
    for suit, sufs in my_suit_to_suffixes.items():
        for suf in sufs:
            hand[suit].append(create_card(_INVERSE_RANK[suf], suit))
    setattr(play, position, hand)
    strat = HardStrategy(position)
    strat.on_spiel_start(play)
    return play, strat


def test_tracking_initializes_sizes_and_voids():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "AK"})
    for p in ("compo", "compn", "compe"):
        assert strat._hand_sizes[p] == 9
        assert strat._voids_all[p] == set()
    assert strat._no_trump_except_under == set()


def test_tracking_decrements_sizes_for_all_others():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "AK"})
    strat.on_card_played("compo", "R6")
    strat.on_card_played("compn", "R7")
    assert strat._hand_sizes["compo"] == 8
    assert strat._hand_sizes["compn"] == 8
    assert strat._hand_sizes["compe"] == 9   # untouched


def test_tracking_marks_hard_void_on_nontrump_lead_discard():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "A"})
    # Rosen led; compe discards Eicheln -> compe void in Rosen.
    strat.on_card_played("compn", "R6")   # lead Rosen (partner)
    strat.on_card_played("compe", "E6")   # discard -> void in Rosen
    assert "Rosen" in strat._voids_all["compe"]
    assert "compe" not in strat._no_trump_except_under


def test_tracking_marks_under_holdback_on_trump_lead_discard():
    _, strat = _make_strat("comps", "Schellen", {"Schellen": "A"})
    # Schellen (trump) led; compo discards Rosen -> "no trump except Under".
    strat.on_card_played("comps", "SEA")  # trump led by us
    strat.on_card_played("compo", "R6")   # discard on trump lead
    assert "compo" in strat._no_trump_except_under
    # NOT recorded as a hard trump void (they may still hold the Under):
    assert "Schellen" not in strat._voids_all["compo"]


# ── Task 6: HardStrategy._build_engine_state ─────────────────────────────
def _remove_from_live_hand(play, position, code):
    """Drop `code` from a live Play hand to mirror a real card being played."""
    card = code_to_card(code)
    bucket = getattr(play, position)[card.suit]
    for i, c in enumerate(bucket):
        if card_to_code(c) == code:
            del bucket[i]
            return


def test_build_engine_state_is_consistent():
    # A balanced, real 9-card hand (the invariant only holds for consistent
    # deals, exactly as in live play). One full trump-led trick is simulated
    # in lockstep with our own hand shrinking, so the unseen set tracks the
    # three hidden hands exactly.
    play, strat = _make_strat(
        "comps", "Schellen",
        {"Schellen": "AKO", "Eicheln": "AK", "Rosen": "AK", "Schilten": "AK"})
    # We lead trump SEA (remove it from our live hand); opponents discard on
    # the trump lead (-> Under-holdback), partner follows trump.
    _remove_from_live_hand(play, "comps", "SEA")
    strat.on_card_played("comps", "SEA")  # trump led by us
    strat.on_card_played("compo", "R6")   # discard on trump lead -> holdback
    strat.on_card_played("compn", "SE9")  # partner follows trump (not in our hand)
    strat.on_card_played("compe", "E6")   # discard on trump lead -> holdback
    state = strat._build_engine_state(play)
    assert state.me == "comps"
    assert state.operator == "Schellen"
    assert set(state.others) == {"compo", "compn", "compe"}
    # Invariant: unseen card count equals sum of the 3 hidden hand sizes.
    assert len(state.unseen) == sum(state.hand_sizes[p] for p in state.others)
    assert "compo" in state.no_trump_except_under
    assert "compe" in state.no_trump_except_under


# ── MINOR #1: rollout raises a descriptive error on unbalanced EngineState
def test_rollout_raises_descriptive_error_on_empty_hand():
    # Unbalanced: a non-self seat has an empty hand while cards remain
    # elsewhere, so a seat is eventually asked to play from nothing.
    my_hand = _hand({"Schellen": "AK"})           # me holds 2 cards
    others = ["compo", "compn", "compe"]
    deal = {
        "compo": _hand({"Schellen": "9"}),        # only 1 card (unbalanced)
        "compn": _hand({}),                        # EMPTY hand
        "compe": _hand({"Eicheln": "7"}),          # only 1 card
    }
    state = _basic_state(
        my_hand=my_hand, others=others,
        hand_sizes={"compo": 1, "compn": 0, "compe": 1},
        unseen=[c for h in deal.values() for cs in h.values() for c in cs],
        operator="Schellen", me="comps",
    )
    lead = create_card(_INVERSE_RANK["A"], "Schellen")
    with pytest.raises(ValueError, match="empty hand"):
        ai_pimc.rollout(state, deal, lead)


# ── Task 7: wire PIMC into HardStrategy._lead ────────────────────────────
def test_lead_uses_pimc_when_enabled(monkeypatch):
    play, strat = _make_strat("comps", "Schellen", {"Schellen": "A", "Eicheln": "6"})
    strat._pimc_enabled = True
    sentinel = create_card(_INVERSE_RANK["A"], "Schellen")  # SEA

    called = {}
    def fake_choose(state, leads, **kw):
        called["yes"] = True
        return sentinel
    monkeypatch.setattr("ausbau.ai_pimc.pimc_choose_lead", fake_choose)

    valid = play.comps["Schellen"] + play.comps["Eicheln"]
    result = strat._lead(play, valid)
    assert called.get("yes") is True
    assert result == {"type": "play_card", "card": "SEA"}


def test_lead_falls_back_to_heuristic_when_pimc_disabled():
    play, strat = _make_strat("comps", "Schellen", {"Schellen": "AK9"})
    strat._pimc_enabled = False
    valid = play.comps["Schellen"]
    result = strat._lead(play, valid)
    # Heuristic rule A draws the HIGHEST trump by card.trumpf with trumps
    # outstanding. Among A/K/9 the Schellen Nine (SE9, trumpf=17) outranks the
    # Ace (SEA, trumpf=16) and Koenig (SEK, trumpf=15) in trump strength.
    assert result["type"] == "play_card"
    assert result["card"] == "SE9"


def test_lead_falls_back_when_pimc_returns_none(monkeypatch):
    play, strat = _make_strat("comps", "Schellen", {"Schellen": "AK9"})
    strat._pimc_enabled = True
    monkeypatch.setattr("ausbau.ai_pimc.pimc_choose_lead",
                        lambda state, leads, **kw: None)
    valid = play.comps["Schellen"]
    result = strat._lead(play, valid)
    assert result["card"] == "SE9"   # heuristic fallback fired (rule A, top trump)
