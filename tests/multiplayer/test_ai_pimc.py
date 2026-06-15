"""PIMC engine (ausbau/ai_pimc.py) unit tests — seeded and deterministic."""
import random
import pytest

from Cards_refactored import SUITS, create_card, Under
from ausbau.game_session import RANK_SUFFIX, card_to_code, PLAYERS
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
