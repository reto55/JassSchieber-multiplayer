# Schieber HTML5 Frontend — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a browser-playable Schieber card game (1 human + 3 AI) with a FastAPI WebSocket backend and a vanilla JS frontend using existing card assets in `ausbau/html5/`.

**Architecture:** FastAPI serves `game.html` at `/` and handles WebSocket sessions at `/ws`. Each connection creates a `GameSession` that wraps the existing `Play`/`Cards_refactored.py` logic. The session drives all game flow server-side, pushing state to the browser; the browser only sends player actions (`play_card`, `choose_trump`, `declare_weis`).

**Tech Stack:** Python 3.9+, FastAPI, uvicorn, vanilla JS (no framework), existing jQuery-free CSS sprite sheet (`Jasskarten.png` at 80×125px cards).

---

## File Map

| Action | Path |
|--------|------|
| Create | `ausbau/__init__.py` |
| Create | `ausbau/game_session.py` |
| Create | `ausbau/server.py` |
| Rewrite | `ausbau/html5/game.html` |
| Extend | `ausbau/html5/css/game.css` |
| Create | `ausbau/html5/js/schieber.js` |
| Create | `tests/test_game_session.py` |

Run the game from the project root:
```bash
cd /mnt/archive/Dokumente/Schieber_neu
python -m uvicorn ausbau.server:app --reload --port 8765
# Open http://localhost:8765
```

---

## Task 1: Project setup

**Files:**
- Create: `ausbau/__init__.py`
- Create: `requirements-html5.txt`

- [ ] **Step 1: Create ausbau package init**

```bash
touch /mnt/archive/Dokumente/Schieber_neu/ausbau/__init__.py
```

- [ ] **Step 2: Create requirements file**

Create `requirements-html5.txt`:
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
```

- [ ] **Step 3: Install dependencies**

```bash
cd /mnt/archive/Dokumente/Schieber_neu
pip install fastapi "uvicorn[standard]"
```

Expected: both packages install without error.

- [ ] **Step 4: Verify import works**

```bash
python -c "import fastapi, uvicorn; print('OK')"
```
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add ausbau/__init__.py requirements-html5.txt
git commit -m "chore: add FastAPI deps for HTML5 frontend"
```

---

## Task 2: Card utility functions

**Files:**
- Create: `ausbau/game_session.py`
- Create: `tests/test_game_session.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_game_session.py`:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Cards_refactored import Ass, Koenig, Ober, Under, Banner, Neun, Acht, Sieben, Sechs, SUITS
from ausbau.game_session import card_to_code, hand_to_codes, find_card_in_hand


def test_card_to_code_eicheln_ass():
    assert card_to_code(Ass(9, 'Eicheln')) == 'EA'

def test_card_to_code_schellen_koenig():
    assert card_to_code(Koenig(8, 'Schellen')) == 'SEK'

def test_card_to_code_schilten_under():
    assert card_to_code(Under(6, 'Schilten')) == 'SIU'

def test_card_to_code_rosen_sechs():
    assert card_to_code(Sechs(1, 'Rosen')) == 'R6'

def test_hand_to_codes_returns_all():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'].append(Ass(9, 'Eicheln'))
    hand['Rosen'].append(Koenig(8, 'Rosen'))
    codes = hand_to_codes(hand)
    assert 'EA' in codes
    assert 'RK' in codes
    assert len(codes) == 2

def test_find_card_in_hand_found():
    hand = {suit: [] for suit in SUITS}
    card = Ass(9, 'Eicheln')
    hand['Eicheln'].append(card)
    found, suit = find_card_in_hand('EA', hand)
    assert found is card
    assert suit == 'Eicheln'

def test_find_card_in_hand_not_found():
    hand = {suit: [] for suit in SUITS}
    found, suit = find_card_in_hand('RK', hand)
    assert found is None
    assert suit is None
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd /mnt/archive/Dokumente/Schieber_neu
python -m pytest tests/test_game_session.py -v
```
Expected: `ModuleNotFoundError: No module named 'ausbau.game_session'`

- [ ] **Step 3: Implement card utilities**

Create `ausbau/game_session.py`:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from typing import Optional
from Cards_refactored import (
    Play, SUITS, PLAY_MODES, Card,
    determine_trumpf, trumpfs, wiis, wiis_gleiche,
)
from utils.game_utils import check_game_end, get_winner

SUIT_PREFIX = {'Eicheln': 'E', 'Rosen': 'R', 'Schellen': 'SE', 'Schilten': 'SI'}
RANK_SUFFIX = {9: 'A', 8: 'K', 7: 'O', 6: 'U', 5: 'B', 4: '9', 3: '8', 2: '7', 1: '6'}

POSITION_NAMES = {'comps': 'Süd', 'compn': 'Nord', 'compo': 'Ost', 'compe': 'West'}
SN_PLAYERS = {'comps', 'compn'}
OW_PLAYERS = {'compo', 'compe'}
PLAYERS = ['comps', 'compo', 'compn', 'compe']


def card_to_code(card: Card) -> str:
    """Convert a Card object to its CSS code string, e.g. Ass(Eicheln) → 'EA'."""
    return SUIT_PREFIX[card.suit] + RANK_SUFFIX[card.rank]


def hand_to_codes(hand: dict) -> list:
    """Return list of card codes for all cards in a hand dict."""
    return [card_to_code(c) for suit in SUITS for c in hand[suit]]


def find_card_in_hand(code: str, hand: dict):
    """Find a card in a hand dict by code. Returns (Card, suit) or (None, None)."""
    for suit in SUITS:
        for card in hand[suit]:
            if card_to_code(card) == code:
                return card, suit
    return None, None
```

- [ ] **Step 4: Run tests — expect pass**

```bash
python -m pytest tests/test_game_session.py -v
```
Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py tests/test_game_session.py
git commit -m "feat: add card utility functions for WebSocket serialisation"
```

---

## Task 3: Valid card logic and trick resolution

**Files:**
- Modify: `ausbau/game_session.py` (append functions)
- Modify: `tests/test_game_session.py` (append tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_game_session.py`:
```python
from ausbau.game_session import get_valid_cards, determine_trick_winner, trick_points


def test_valid_cards_leading_all_valid():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln'), Koenig(8, 'Eicheln')]
    codes = get_valid_cards(hand, None, 'Rosen')
    assert set(codes) == {'EA', 'EK'}


def test_valid_cards_must_follow_suit():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    hand['Rosen'] = [Koenig(8, 'Rosen')]
    codes = get_valid_cards(hand, 'Eicheln', 'Schellen')
    assert codes == ['EA']
    assert 'RK' not in codes


def test_valid_cards_cannot_follow_suit():
    hand = {suit: [] for suit in SUITS}
    hand['Rosen'] = [Koenig(8, 'Rosen')]
    codes = get_valid_cards(hand, 'Eicheln', 'Schellen')
    assert 'RK' in codes


def test_valid_cards_trump_under_always_playable():
    """Trump Under can always be played even when following a different suit."""
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln')]
    hand['Rosen'] = [Under(6, 'Rosen')]  # Rosen is trump
    codes = get_valid_cards(hand, 'Eicheln', 'Rosen')
    assert 'EA' in codes
    assert 'RU' in codes  # trump Under is always valid


def test_trick_winner_trump_beats_lead():
    folger = {'comps': 'compo', 'compo': 'compn', 'compn': 'compe', 'compe': 'comps'}
    trick = {
        'comps': Sechs(1, 'Eicheln'),
        'compo': Koenig(8, 'Eicheln'),
        'compn': Ass(9, 'Rosen'),    # Rosen is trump
        'compe': Banner(5, 'Eicheln'),
    }
    assert determine_trick_winner(trick, 'comps', 'Rosen', folger) == 'compn'


def test_trick_winner_highest_lead_suit_wins():
    folger = {'comps': 'compo', 'compo': 'compn', 'compn': 'compe', 'compe': 'comps'}
    trick = {
        'comps': Sechs(1, 'Eicheln'),
        'compo': Koenig(8, 'Eicheln'),
        'compn': Banner(5, 'Rosen'),   # off-suit, can't win
        'compe': Ober(7, 'Eicheln'),
    }
    assert determine_trick_winner(trick, 'comps', 'Schellen', folger) == 'compo'


def test_trick_points_oben_mode():
    trick = {
        'comps': Banner(5, 'Eicheln'),   # woben=10
        'compo': Koenig(8, 'Rosen'),     # woben=4
        'compn': Ass(9, 'Schellen'),     # woben=0 (Ass in Oben mode)
        'compe': Under(6, 'Schilten'),   # woben=2
    }
    assert trick_points(trick, 'Oben') == 16  # 10+4+0+2


def test_trick_points_trumpf_mode():
    trick = {
        'comps': Under(6, 'Eicheln'),   # Eicheln is trump → wtrumpf=20
        'compo': Ass(9, 'Rosen'),       # non-trump → wfarbe=11
        'compn': Banner(5, 'Eicheln'),  # trump → wtrumpf=10
        'compe': Koenig(8, 'Rosen'),    # non-trump → wfarbe=4
    }
    assert trick_points(trick, 'Eicheln') == 45  # 20+11+10+4
```

- [ ] **Step 2: Run tests — expect failure**

```bash
python -m pytest tests/test_game_session.py -v -k "valid_cards or trick_winner or trick_points"
```
Expected: `AttributeError` or `ImportError` for missing functions.

- [ ] **Step 3: Implement**

Append to `ausbau/game_session.py`:
```python
def get_valid_cards(hand: dict, lead_suit: Optional[str], operator: str) -> list:
    """Return card codes valid to play. lead_suit=None means player is leading."""
    all_cards = [c for suit in SUITS for c in hand[suit]]

    if lead_suit is None:
        return [card_to_code(c) for c in all_cards]

    follow_cards = hand.get(lead_suit, [])
    if not follow_cards:
        return [card_to_code(c) for c in all_cards]

    valid = list(follow_cards)
    # Trump Under (Bube) can always be played in a trump game
    if operator in SUITS:
        for c in hand.get(operator, []):
            if c.__class__.__name__ == 'Under' and c not in valid:
                valid.append(c)

    return [card_to_code(c) for c in valid]


def determine_trick_winner(trick: dict, first: str, operator: str, folger: dict) -> str:
    """Return the player key who wins the trick."""
    lead_suit = trick[first].suit

    def strength(card: Card):
        if operator in SUITS:
            if card.suit == operator:
                return (2, card.trumpf)
            elif card.suit == lead_suit:
                return (1, card.rank)
            return (0, 0)
        elif operator == 'Oben':
            return (1, card.oben) if card.suit == lead_suit else (0, 0)
        else:  # Unten
            return (1, card.unten) if card.suit == lead_suit else (0, 0)

    winner = first
    best = strength(trick[first])
    player = folger[first]
    for _ in range(3):
        s = strength(trick[player])
        if s > best:
            best = s
            winner = player
        player = folger[player]
    return winner


def trick_points(trick: dict, operator: str) -> int:
    """Sum point values of all cards in the trick for the given mode."""
    total = 0
    for card in trick.values():
        if operator in SUITS:
            total += card.wtrumpf if card.suit == operator else card.wfarbe
        elif operator == 'Oben':
            total += card.woben
        else:
            total += card.wunten
    return total
```

- [ ] **Step 4: Run tests — expect pass**

```bash
python -m pytest tests/test_game_session.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py tests/test_game_session.py
git commit -m "feat: add valid card logic and trick resolution"
```

---

## Task 4: AI card selection and Weis detection

**Files:**
- Modify: `ausbau/game_session.py`
- Modify: `tests/test_game_session.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_game_session.py`:
```python
from ausbau.game_session import ai_select_card, describe_weis, detect_stock


def test_ai_leads_plays_highest_value():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln'), Sechs(1, 'Eicheln')]
    card = ai_select_card(hand, None, 'Rosen')
    assert card_to_code(card) == 'EA'


def test_ai_follows_plays_lowest_value():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Ass(9, 'Eicheln'), Sechs(1, 'Eicheln')]
    card = ai_select_card(hand, 'Eicheln', 'Rosen')
    assert card_to_code(card) == 'E6'


def test_describe_weis_dreier():
    combos = [(0, 3, 7)]  # Eicheln, 3-sequence
    result = describe_weis(combos, [])
    assert result == [{'name': 'Dreier', 'suit': 'Eicheln', 'points': 20}]


def test_describe_weis_vierter():
    combos = [(2, 4, 8)]  # Schellen, 4-sequence
    result = describe_weis(combos, [])
    assert result == [{'name': 'Vierter', 'suit': 'Schellen', 'points': 50}]


def test_describe_weis_fuenfer():
    combos = [(1, 5, 9)]  # Rosen, 5-sequence
    result = describe_weis(combos, [])
    assert result == [{'name': '5er', 'suit': 'Rosen', 'points': 100}]


def test_describe_weis_viererle():
    result = describe_weis([], [18])  # Under in all suits
    assert result == [{'name': 'Viererle', 'suit': None, 'points': 100}]


def test_detect_stock_true():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Koenig(8, 'Eicheln'), Ober(7, 'Eicheln')]
    assert detect_stock(hand, 'Eicheln') is True


def test_detect_stock_false_wrong_suit():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Koenig(8, 'Eicheln'), Ober(7, 'Eicheln')]
    assert detect_stock(hand, 'Rosen') is False


def test_detect_stock_false_missing_ober():
    hand = {suit: [] for suit in SUITS}
    hand['Eicheln'] = [Koenig(8, 'Eicheln')]
    assert detect_stock(hand, 'Eicheln') is False
```

- [ ] **Step 2: Run tests — expect failure**

```bash
python -m pytest tests/test_game_session.py -v -k "ai_select or describe_weis or detect_stock"
```
Expected: `ImportError` for missing functions.

- [ ] **Step 3: Implement**

Append to `ausbau/game_session.py`:
```python
def ai_select_card(hand: dict, lead_suit: Optional[str], operator: str) -> Card:
    """Simple AI: lead=highest point value, follow=lowest point value."""
    valid_codes = get_valid_cards(hand, lead_suit, operator)
    valid_cards = [find_card_in_hand(code, hand)[0] for code in valid_codes]

    def point_value(card: Card) -> int:
        if operator in SUITS:
            return card.wtrumpf if card.suit == operator else card.wfarbe
        elif operator == 'Oben':
            return card.woben
        return card.wunten

    if lead_suit is None:
        return max(valid_cards, key=point_value)
    return min(valid_cards, key=point_value)


def describe_weis(weis_combos: list, weis_gleiche: list) -> list:
    """Convert raw wiis() / wiis_gleiche() output to human-readable dicts."""
    result = []
    SCORE_MAP = {3: ('Dreier', 20), 4: ('Vierter', 50)}
    for suit_idx, seq_len, _ in weis_combos:
        if seq_len is None or seq_len < 3:
            continue
        name, pts = SCORE_MAP.get(seq_len, (f'{seq_len}er', 100))
        result.append({'name': name, 'suit': SUITS[suit_idx], 'points': pts})
    if weis_gleiche:
        result.append({'name': 'Viererle', 'suit': None, 'points': 100})
    return result


def detect_stock(hand: dict, operator: str) -> bool:
    """True if hand has König + Ober of the trump suit (Stöck, 20pts)."""
    if operator not in SUITS:
        return False
    ranks = {c.__class__.__name__ for c in hand.get(operator, [])}
    return 'Koenig' in ranks and 'Ober' in ranks
```

- [ ] **Step 4: Run all tests — expect pass**

```bash
python -m pytest tests/test_game_session.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py tests/test_game_session.py
git commit -m "feat: add AI card selection and Weis detection"
```

---

## Task 5: GameSession — deal and initial state

**Files:**
- Modify: `ausbau/game_session.py`
- Modify: `tests/test_game_session.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_game_session.py`:
```python
from ausbau.game_session import GameSession


def test_initial_state_structure():
    session = GameSession(end_game=500)
    play = Play(1)
    state = session._initial_state(play)

    assert state['type'] == 'game_start'
    assert len(state['hand']) == 9
    assert state['scores'] == {'sn': 0, 'ow': 0}
    assert state['target'] == 500
    assert len(state['players']) == 3
    assert any(p['is_partner'] for p in state['players'])
    assert all('card_count' in p for p in state['players'])


def test_initial_state_scores_accumulate():
    session = GameSession(end_game=500)
    session.point_sn = 42
    session.point_ow = 17
    state = session._initial_state(Play(1))
    assert state['scores'] == {'sn': 42, 'ow': 17}
```

- [ ] **Step 2: Run failing tests**

```bash
python -m pytest tests/test_game_session.py -v -k "initial_state"
```
Expected: `ImportError` for `GameSession`.

- [ ] **Step 3: Implement**

Append to `ausbau/game_session.py`:
```python
class GameSession:
    def __init__(self, end_game: int = 1000):
        self.end_game = end_game
        self.point_sn = 0
        self.point_ow = 0

    def _initial_state(self, play: Play) -> dict:
        return {
            "type": "game_start",
            "hand": hand_to_codes(play.comps),
            "first_player": POSITION_NAMES[play.first],
            "players": [
                {
                    "name": POSITION_NAMES[p],
                    "position": p,
                    "is_partner": p == 'compn',
                    "card_count": 9,
                }
                for p in ['compe', 'compn', 'compo']
            ],
            "scores": {"sn": self.point_sn, "ow": self.point_ow},
            "target": self.end_game,
        }
```

- [ ] **Step 4: Run tests — expect pass**

```bash
python -m pytest tests/test_game_session.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py tests/test_game_session.py
git commit -m "feat: add GameSession with initial state serialisation"
```

---

## Task 6: GameSession — trump phase

**Files:**
- Modify: `ausbau/game_session.py`
- Modify: `tests/test_game_session.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_game_session.py`:
```python
import asyncio
from unittest.mock import AsyncMock


def test_trump_phase_human_leads_chooses():
    """When human (comps) leads, server asks and human responds choose_trump."""
    session = GameSession()
    play = Play(4)  # spiel 4 → comps leads

    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={"type": "choose_trump", "suit": "Eicheln"})
    asyncio.run(session._trump_phase(ws, play))

    assert play.operator == "Eicheln"
    calls = [c[0][0] for c in ws.send_json.call_args_list]
    assert calls[0]['type'] == 'trump_request'
    assert calls[0]['can_schieben'] is True
    assert calls[1]['type'] == 'trump_chosen'
    assert calls[1]['suit'] == 'Eicheln'


def test_trump_phase_human_leads_schiebt():
    """Human schiebt → partner Nord (AI) chooses via trumpfs()."""
    session = GameSession()
    play = Play(4)
    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={"type": "schieben"})
    asyncio.run(session._trump_phase(ws, play))

    assert play.operator in ['Eicheln', 'Rosen', 'Schellen', 'Schilten', 'Oben', 'Unten']
    assert play.starter == 'compn'
```

- [ ] **Step 2: Run failing tests**

```bash
python -m pytest tests/test_game_session.py -v -k "trump_phase"
```
Expected: `AttributeError` — `_trump_phase` not defined.

- [ ] **Step 3: Implement**

Append inside the `GameSession` class in `ausbau/game_session.py`:
```python
    async def _trump_phase(self, websocket, play: Play) -> None:
        """Handle trump selection. Asks human if they are the lead or if AI schiebs to them."""
        if play.first == 'comps':
            # Human leads — let them choose
            await websocket.send_json({"type": "trump_request", "can_schieben": True})
            msg = await websocket.receive_json()
            if msg['type'] == 'schieben':
                play.operator = trumpfs(play.compn)
                play.starter = 'compn'
                chooser = 'Nord'
            else:
                play.operator = msg['suit']
                play.starter = 'comps'
                chooser = 'Du'
        elif play.operator == 'Schieben':
            # AI lead wants to pass — check if partner is human
            partner = play.partner[play.first]
            if partner == 'comps':
                await websocket.send_json({"type": "trump_request", "can_schieben": False})
                msg = await websocket.receive_json()
                play.operator = msg['suit']
                play.starter = 'comps'
                chooser = 'Du'
            else:
                play.operator = trumpfs(play.__dict__[partner])
                play.starter = partner
                chooser = POSITION_NAMES[partner]
        else:
            # AI already chose — just inform client
            chooser = POSITION_NAMES[play.first]

        await websocket.send_json({
            "type": "trump_chosen",
            "suit": play.operator,
            "by": chooser,
        })
```

- [ ] **Step 4: Run tests — expect pass**

```bash
python -m pytest tests/test_game_session.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py tests/test_game_session.py
git commit -m "feat: add trump selection phase to GameSession"
```

---

## Task 7: GameSession — Weis phase

**Files:**
- Modify: `ausbau/game_session.py`
- Modify: `tests/test_game_session.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_game_session.py`:
```python
def test_weis_phase_sends_result():
    """weis_result is always sent, even if no weis exist."""
    session = GameSession()
    play = Play(1)
    ws = AsyncMock()
    asyncio.run(session._weis_phase(ws, play))

    last = ws.send_json.call_args_list[-1][0][0]
    assert last['type'] == 'weis_result'
    assert 'announcements' in last
    assert 'scores' in last


def test_weis_phase_human_announces_adds_points():
    """If human announces weis, SN score increases."""
    session = GameSession()
    play = Play(1)

    # Force human to have a Dreier (20 pts)
    from ausbau.game_session import describe_weis
    from unittest.mock import patch

    fake_weis = [{'name': 'Dreier', 'suit': 'Eicheln', 'points': 20}]
    ws = AsyncMock()
    ws.receive_json = AsyncMock(return_value={
        "type": "declare_weis", "weis": ["Dreier"], "announce": True
    })

    with patch('ausbau.game_session.describe_weis', return_value=fake_weis):
        asyncio.run(session._weis_phase(ws, play))

    # Human (comps) is SN team — points should have increased
    assert session.point_sn >= 20
```

- [ ] **Step 2: Run failing tests**

```bash
python -m pytest tests/test_game_session.py -v -k "weis_phase"
```
Expected: `AttributeError` — `_weis_phase` not defined.

- [ ] **Step 3: Implement**

Append inside `GameSession` class:
```python
    async def _weis_phase(self, websocket, play: Play) -> None:
        """Handle weis declaration. Asks human if they have combinations; AI always announces."""
        human_weis = describe_weis(wiis(play.comps), wiis_gleiche(play.comps))
        weis_announce = {}

        if human_weis:
            await websocket.send_json({"type": "weis_request", "your_weis": human_weis})
            msg = await websocket.receive_json()
            if msg.get('announce'):
                weis_announce['comps'] = human_weis

        # AI players always announce if they have weis
        for player in ['compo', 'compn', 'compe']:
            pw = describe_weis(
                wiis(play.__dict__[player]),
                wiis_gleiche(play.__dict__[player]),
            )
            if pw:
                weis_announce[player] = pw

        sn_pts = sum(w['points'] for p in SN_PLAYERS if p in weis_announce
                     for w in weis_announce[p])
        ow_pts = sum(w['points'] for p in OW_PLAYERS if p in weis_announce
                     for w in weis_announce[p])
        self.point_sn += sn_pts
        self.point_ow += ow_pts

        announcements = [
            {
                "player": POSITION_NAMES[p],
                "weis": weis_announce[p],
                "points": sum(w['points'] for w in weis_announce[p]),
            }
            for p in PLAYERS if p in weis_announce
        ]
        await websocket.send_json({
            "type": "weis_result",
            "announcements": announcements,
            "scores": {"sn": self.point_sn, "ow": self.point_ow},
        })
```

- [ ] **Step 4: Run tests — expect pass**

```bash
python -m pytest tests/test_game_session.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py tests/test_game_session.py
git commit -m "feat: add weis declaration phase to GameSession"
```

---

## Task 8: GameSession — trick loop and run() method

**Files:**
- Modify: `ausbau/game_session.py`

No unit tests for this task (async WebSocket flow is covered by integration in Task 10). Manual test is the smoke test at the end.

- [ ] **Step 1: Implement `_play_trick`**

Append inside `GameSession` class:
```python
    async def _play_trick(self, websocket, play: Play) -> str:
        """Play one trick. Returns the winning player key."""
        trick = {}
        lead_suit = None
        player = play.first

        for i in range(4):
            card = None
            if player == 'comps':
                valid = get_valid_cards(play.comps, lead_suit, play.operator)
                await websocket.send_json({"type": "your_turn", "valid_cards": valid})
                while True:
                    msg = await websocket.receive_json()
                    if msg['type'] != 'play_card':
                        continue
                    found, suit = find_card_in_hand(msg['card'], play.comps)
                    if found is not None and msg['card'] in valid:
                        play.comps[suit].remove(found)
                        card = found
                        break
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Ungültige Karte: {msg.get('card')}",
                    })
                    await websocket.send_json({"type": "your_turn", "valid_cards": valid})
            else:
                card = ai_select_card(play.__dict__[player], lead_suit, play.operator)
                play.__dict__[player][card.suit].remove(card)
                await asyncio.sleep(0.8)

            if i == 0:
                lead_suit = card.suit
            trick[player] = card

            await websocket.send_json({
                "type": "card_played",
                "player": POSITION_NAMES[player],
                "player_key": player,
                "card": card_to_code(card),
            })
            player = play.folger[player]

        winner = determine_trick_winner(trick, play.first, play.operator, play.folger)
        pts = trick_points(trick, play.operator)
        if winner in SN_PLAYERS:
            self.point_sn += pts
        else:
            self.point_ow += pts
        return winner
```

- [ ] **Step 2: Implement `_run_spiel`**

Append inside `GameSession` class:
```python
    async def _run_spiel(self, websocket, spiel_num: int) -> None:
        """Deal, trump, weis, then 9 tricks for one Spiel."""
        play = Play(spiel_num)
        await websocket.send_json(self._initial_state(play))
        await self._trump_phase(websocket, play)
        await self._weis_phase(websocket, play)

        for trick_num in range(9):
            winner = await self._play_trick(websocket, play)
            is_last = trick_num == 8
            if is_last:
                if winner in SN_PLAYERS:
                    self.point_sn += 5   # last trick bonus
                else:
                    self.point_ow += 5
            play.first = winner  # trick winner leads next
            await websocket.send_json({
                "type": "trick_end",
                "winner": POSITION_NAMES[winner],
                "winner_key": winner,
                "points_sn": self.point_sn,
                "points_ow": self.point_ow,
            })

        await websocket.send_json({
            "type": "round_end",
            "score_sn": self.point_sn,
            "score_ow": self.point_ow,
            "winner_team": get_winner(self.point_sn, self.point_ow),
        })
```

- [ ] **Step 3: Implement `run()`**

Append inside `GameSession` class:
```python
    async def run(self, websocket) -> None:
        """Main loop: cycles through 4 Spiele per round until end_game score is reached."""
        spiel_num = 0
        while True:
            spiel_num = (spiel_num % 4) + 1
            await self._run_spiel(websocket, spiel_num)
            if check_game_end(self.point_sn, self.point_ow, self.end_game):
                await websocket.send_json({
                    "type": "game_end",
                    "winner_team": get_winner(self.point_sn, self.point_ow),
                    "final_scores": {"sn": self.point_sn, "ow": self.point_ow},
                })
                return
            await asyncio.sleep(2)  # pause between Spiele
```

- [ ] **Step 4: Run existing tests to confirm no regression**

```bash
python -m pytest tests/test_game_session.py -v
```
Expected: all previously passing tests still PASS.

- [ ] **Step 5: Commit**

```bash
git add ausbau/game_session.py
git commit -m "feat: add trick loop and run() to GameSession"
```

---

## Task 9: FastAPI server

**Files:**
- Create: `ausbau/server.py`

- [ ] **Step 1: Create server.py**

```python
# ausbau/server.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ausbau.game_session import GameSession

app = FastAPI()

_BASE = os.path.dirname(os.path.abspath(__file__))
_HTML5 = os.path.join(_BASE, "html5")

app.mount("/static", StaticFiles(directory=_HTML5), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(_HTML5, "game.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = GameSession(end_game=1000)
    try:
        await session.run(websocket)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        # Log and close gracefully on unexpected errors
        print(f"Session error: {exc}")
        try:
            await websocket.close()
        except Exception:
            pass
```

- [ ] **Step 2: Verify server starts**

```bash
cd /mnt/archive/Dokumente/Schieber_neu
python -m uvicorn ausbau.server:app --port 8765 &
sleep 2
curl -s http://localhost:8765/ | head -5
kill %1
```
Expected: HTML output containing `<html` or `<!DOCTYPE`.

- [ ] **Step 3: Commit**

```bash
git add ausbau/server.py
git commit -m "feat: add FastAPI server with WebSocket endpoint"
```

---

## Task 10: Frontend — game.html

**Files:**
- Rewrite: `ausbau/html5/game.html`

- [ ] **Step 1: Rewrite game.html**

Replace the full content of `ausbau/html5/game.html`:
```html
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Schieber</title>
  <link rel="stylesheet" href="/static/css/game.css">
</head>
<body>
<div id="game">

  <!-- ① AI Bar -->
  <div id="ai-bar">
    <div class="ai-player" id="player-compe">
      <div class="ai-avatar">W</div>
      <div class="ai-info">
        <div class="ai-name">West</div>
        <div class="ai-cards" id="cards-compe"></div>
      </div>
    </div>
    <div class="ai-player partner" id="player-compn">
      <div class="ai-avatar">N</div>
      <div class="ai-info">
        <div class="ai-name">Nord ★</div>
        <div class="ai-cards" id="cards-compn"></div>
      </div>
    </div>
    <div class="ai-player" id="player-compo">
      <div class="ai-avatar">O</div>
      <div class="ai-info">
        <div class="ai-name">Ost</div>
        <div class="ai-cards" id="cards-compo"></div>
      </div>
    </div>
    <div id="score-panel">
      <div class="score-label">PUNKTE</div>
      <div class="score-row">
        <div class="score-team">
          <span class="team-label sn-label">SN</span>
          <span class="team-score" id="score-sn">0</span>
        </div>
        <div class="score-divider"></div>
        <div class="score-team">
          <span class="team-label ow-label">OW</span>
          <span class="team-score" id="score-ow">0</span>
        </div>
      </div>
      <div class="score-target" id="score-target">Ziel: 1000</div>
    </div>
  </div>

  <!-- ② Table -->
  <div id="table">
    <div id="trump-badge" class="hidden">
      <span class="trump-label">Trumpf</span>
      <span id="trump-value"></span>
    </div>
    <div id="round-info">
      <span id="active-player"></span>
    </div>

    <!-- ③ Trick area -->
    <div id="trick-area">
      <div class="trick-slot" id="trick-compn">
        <span class="trick-label">Nord</span>
      </div>
      <div id="trick-middle-row">
        <div class="trick-slot" id="trick-compe">
          <span class="trick-label">West</span>
        </div>
        <div class="trick-slot" id="trick-comps">
          <span class="trick-label">Du</span>
        </div>
        <div class="trick-slot" id="trick-compo">
          <span class="trick-label">Ost</span>
        </div>
      </div>
    </div>

    <!-- ④ Game log -->
    <div id="game-log">
      <div id="log-entries"></div>
    </div>
  </div>

  <!-- ⑤ Human hand -->
  <div id="hand-area">
    <div id="hand-label">Deine Hand</div>
    <div id="hand-cards"></div>
  </div>

</div>

<!-- Trump modal -->
<div id="trump-modal" class="modal hidden">
  <div class="modal-overlay"></div>
  <div class="modal-box">
    <h3>Trumpf wählen</h3>
    <div id="trump-options" class="suit-grid"></div>
    <button id="schieben-btn" class="hidden schieben-btn">↩ Schieben</button>
  </div>
</div>

<!-- Weis modal -->
<div id="weis-modal" class="modal hidden">
  <div class="modal-overlay"></div>
  <div class="modal-box">
    <h3>Weis ansagen?</h3>
    <div id="weis-list"></div>
    <div class="modal-actions">
      <button id="weis-announce-btn" class="btn-primary">✓ Ansagen</button>
      <button id="weis-pass-btn" class="btn-secondary">Schweigen</button>
    </div>
  </div>
</div>

<script src="/static/js/schieber.js"></script>
</body>
</html>
```

- [ ] **Step 2: Verify the file exists and has the expected structure**

```bash
grep -c "trick-slot" /mnt/archive/Dokumente/Schieber_neu/ausbau/html5/game.html
```
Expected: `4` (four trick slots).

- [ ] **Step 3: Commit**

```bash
git add ausbau/html5/game.html
git commit -m "feat: rewrite game.html with 5-component layout"
```

---

## Task 11: Frontend CSS — layout and new components

**Files:**
- Modify: `ausbau/html5/css/game.css` (append at end — existing card sprite rules stay)

- [ ] **Step 1: Append layout CSS to game.css**

Append the following to the end of `ausbau/html5/css/game.css`:
```css
/* ─────────────────────────────────────────
   Schieber — Wide/Compact Layout
   ───────────────────────────────────────── */

*, *::before, *::after { box-sizing: border-box; }

html, body {
  margin: 0; padding: 0;
  height: 100%; overflow: hidden;
  font-family: system-ui, sans-serif;
  background: #111; color: #ccc;
}

#game {
  display: flex; flex-direction: column;
  height: 100vh;
  background: #2d5a27;
}

/* ① AI Bar */
#ai-bar {
  display: flex; align-items: center; gap: 12px;
  background: #111; padding: 8px 16px;
  border-bottom: 2px solid #333; flex-shrink: 0;
}

.ai-player { display: flex; align-items: center; gap: 8px; flex: 1; }
.ai-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: #333; border: 2px solid #555;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: bold; color: #aaa;
}
.ai-player.partner .ai-avatar { border-color: #3a8a3a; color: #7fc47f; }
.ai-name { font-size: 10px; color: #aaa; margin-bottom: 3px; }
.ai-player.partner .ai-name { color: #7fc47f; }
.ai-cards { display: flex; gap: 1px; flex-wrap: wrap; }
.ai-card-back {
  width: 9px; height: 14px;
  background: #8b0000; border: 1px solid #600; border-radius: 1px;
}

#score-panel {
  background: #1a1a1a; border-radius: 8px;
  padding: 6px 14px; border: 1px solid #333;
  text-align: center; min-width: 110px; flex-shrink: 0;
}
.score-label { font-size: 9px; color: #666; margin-bottom: 3px; }
.score-row { display: flex; align-items: center; justify-content: center; gap: 10px; }
.score-team { display: flex; flex-direction: column; align-items: center; }
.team-label { font-size: 9px; }
.sn-label { color: #7fc47f; }
.ow-label { color: #e88; }
.team-score { font-size: 20px; font-weight: bold; color: #fff; line-height: 1; }
.score-divider { width: 1px; height: 28px; background: #333; }
.score-target { font-size: 9px; color: #666; margin-top: 3px; }

/* ② Table */
#table {
  flex: 1; position: relative;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}

#trump-badge {
  position: absolute; top: 10px; left: 14px;
  background: #3a2200; border: 1px solid #a06000;
  border-radius: 6px; padding: 5px 10px; z-index: 5;
}
#trump-badge.hidden { display: none; }
.trump-label { font-size: 9px; color: #f0c050; display: block; }
#trump-value { font-size: 12px; color: #fff; }

#round-info {
  position: absolute; top: 10px; right: 14px;
  background: rgba(0,0,0,.4); border-radius: 6px;
  padding: 5px 10px; font-size: 10px; color: #aaa;
}

/* ③ Trick area */
#trick-area {
  display: flex; flex-direction: column;
  align-items: center; gap: 6px;
}
#trick-middle-row { display: flex; align-items: center; gap: 6px; }

.trick-slot {
  width: 56px; min-height: 84px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: flex-end;
  gap: 3px;
}
.trick-label { font-size: 9px; color: #666; }
.trick-slot .card {
  cursor: default;
  position: relative;   /* overrides position:absolute so card stays in slot */
}
.trick-slot .card .face.front { display: none; }     /* hide card-back pattern */
.trick-slot .card .face.back { transform: none; position: absolute; z-index: 1; }

/* ④ Game log */
#game-log {
  position: absolute; bottom: 10px; right: 14px;
  width: 200px; max-height: 160px;
  background: rgba(0,0,0,.5); border-radius: 6px;
  padding: 6px; overflow-y: auto; font-size: 10px;
}
.log-entry { padding: 1px 0; color: #aaa; }
.log-entry.error { color: #f88; }

/* ⑤ Human hand */
#hand-area {
  background: rgba(0,0,0,.4); border-top: 2px solid #3a5a3a;
  padding: 10px 16px 12px; flex-shrink: 0;
}
#hand-label { font-size: 9px; color: #666; margin-bottom: 6px; }
#hand-cards { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }

/* Hand card overrides */
#hand-cards .card {
  position: relative;  /* overrides position:absolute so card stays in flex flow */
  -webkit-perspective: none; perspective: none;
  transition: transform .15s;
}
/* Show card face (the .back div holds the sprite), hide the card-back design (.front) */
#hand-cards .card .face.front { display: none; }
#hand-cards .card .face.back { transform: none; z-index: 1; position: absolute; }

#hand-cards .card.valid {
  border: 2px solid #ffcc00 !important;
  box-shadow: 0 0 10px #ffcc0088;
  transform: translateY(-5px);
  cursor: pointer;
}
#hand-cards .card.invalid {
  opacity: 0.4; cursor: not-allowed;
}
#hand-cards .card.valid:hover { transform: translateY(-9px); }

/* Modals */
.modal {
  position: fixed; inset: 0;
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}
.modal.hidden { display: none; }
.modal-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,.55);
}
.modal-box {
  position: relative; z-index: 1;
  background: #1e1e1e; border-radius: 12px;
  padding: 20px 24px; border: 1px solid #444;
  min-width: 270px; max-width: 340px;
}
.modal-box h3 { color: #fff; text-align: center; margin-bottom: 14px; font-size: 15px; }

/* Trump suit grid */
.suit-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 8px; margin-bottom: 10px;
}
.suit-btn {
  background: #6a1a1a; color: #fff; border: none;
  border-radius: 7px; padding: 9px 6px;
  font-size: 12px; cursor: pointer; transition: background .15s;
}
.suit-btn:nth-child(5), .suit-btn:nth-child(6) { background: #1a3a7a; }
.suit-btn:hover { filter: brightness(1.2); }
.schieben-btn {
  width: 100%; background: #444; color: #ccc;
  border: none; border-radius: 7px; padding: 8px;
  font-size: 12px; cursor: pointer; margin-top: 4px;
}
.schieben-btn:hover { background: #555; }

/* Weis list */
.weis-item {
  display: flex; justify-content: space-between; align-items: center;
  background: #2a2a2a; border-radius: 6px;
  padding: 7px 10px; margin-bottom: 6px;
}
.weis-name { color: #f0c050; font-size: 12px; font-weight: bold; }
.weis-suit { color: #aaa; font-size: 11px; }
.weis-pts { color: #7fc47f; font-size: 12px; font-weight: bold; }

.modal-actions { display: flex; gap: 8px; margin-top: 12px; }
.btn-primary {
  flex: 2; background: #2a6a2a; color: #fff;
  border: none; border-radius: 7px; padding: 9px; font-size: 12px; cursor: pointer;
}
.btn-secondary {
  flex: 1; background: #444; color: #ccc;
  border: none; border-radius: 7px; padding: 9px; font-size: 12px; cursor: pointer;
}
.btn-primary:hover { background: #3a8a3a; }
.btn-secondary:hover { background: #555; }

.hidden { display: none !important; }
```

- [ ] **Step 2: Commit**

```bash
git add ausbau/html5/css/game.css
git commit -m "feat: add layout CSS for Schieber game UI"
```

---

## Task 12: Frontend JS — WebSocket client and state

**Files:**
- Create: `ausbau/html5/js/schieber.js`

- [ ] **Step 1: Create schieber.js with connection and dispatch**

Create `ausbau/html5/js/schieber.js`:
```javascript
'use strict';

// ─── Constants ───────────────────────────────────────────────────────────────
const WS_URL = `ws://${location.host}/ws`;

const SUIT_EMOJI = {
  Eicheln: '🌳', Rosen: '🌹', Schellen: '🔔', Schilten: '🛡',
  Oben: '⬆', Unten: '⬇',
};

// Server uses 'player_key' strings like 'comps'; position label → key map
const LABEL_TO_KEY = { Süd: 'comps', Nord: 'compn', Ost: 'compo', West: 'compe' };

// ─── Game state ───────────────────────────────────────────────────────────────
const state = {
  hand: [],               // card codes for human's 9 cards
  scores: { sn: 0, ow: 0 },
  targetScore: 1000,
  cardCounts: { compe: 0, compn: 0, compo: 0 },
  trick: { comps: null, compn: null, compo: null, compe: null },
  validCards: [],
  operator: null,
};

// ─── WebSocket ────────────────────────────────────────────────────────────────
let ws = null;

function connect() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => appendLog('Verbunden — Karten werden verteilt…');
  ws.onmessage = (e) => dispatch(JSON.parse(e.data));
  ws.onclose = () => appendLog('Verbindung getrennt.');
  ws.onerror = () => appendLog('Verbindungsfehler.', 'error');
}

function send(msg) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
}

function dispatch(msg) {
  const handlers = {
    game_start:    onGameStart,
    trump_request: onTrumpRequest,
    trump_chosen:  onTrumpChosen,
    weis_request:  onWeisRequest,
    weis_result:   onWeisResult,
    your_turn:     onYourTurn,
    card_played:   onCardPlayed,
    trick_end:     onTrickEnd,
    round_end:     onRoundEnd,
    game_end:      onGameEnd,
    error:         (m) => appendLog(`Fehler: ${m.message}`, 'error'),
  };
  const fn = handlers[msg.type];
  if (fn) fn(msg);
}

connect();
```

- [ ] **Step 2: Commit**

```bash
git add ausbau/html5/js/schieber.js
git commit -m "feat: add WebSocket client skeleton to schieber.js"
```

---

## Task 13: Frontend JS — render functions

**Files:**
- Modify: `ausbau/html5/js/schieber.js` (append)

- [ ] **Step 1: Append render functions**

Append to `ausbau/html5/js/schieber.js`:
```javascript
// ─── Render ───────────────────────────────────────────────────────────────────

function renderScores() {
  document.getElementById('score-sn').textContent = state.scores.sn;
  document.getElementById('score-ow').textContent = state.scores.ow;
}

function renderAIBar() {
  ['compe', 'compn', 'compo'].forEach(key => {
    const el = document.getElementById(`cards-${key}`);
    el.innerHTML = '';
    const count = state.cardCounts[key] ?? 0;
    for (let i = 0; i < count; i++) {
      const d = document.createElement('div');
      d.className = 'ai-card-back';
      el.appendChild(d);
    }
  });
  renderScores();
}

function renderHand() {
  const container = document.getElementById('hand-cards');
  container.innerHTML = '';
  state.hand.forEach(code => {
    const card = document.createElement('div');
    card.className = 'card';
    const face = document.createElement('div');
    // The existing CSS uses class 'face back cardXX' for the visible side
    face.className = `face back card${code}`;
    card.appendChild(face);

    if (state.validCards.length > 0) {
      if (state.validCards.includes(code)) {
        card.classList.add('valid');
        card.addEventListener('click', () => playCard(code));
      } else {
        card.classList.add('invalid');
      }
    }
    container.appendChild(card);
  });
}

function renderTrickArea() {
  ['comps', 'compn', 'compo', 'compe'].forEach(key => {
    const slot = document.getElementById(`trick-${key}`);
    const existing = slot.querySelector('.card');
    if (existing) existing.remove();
    const code = state.trick[key];
    if (code) {
      const card = document.createElement('div');
      card.className = 'card';
      const face = document.createElement('div');
      face.className = `face back card${code}`;
      card.appendChild(face);
      slot.appendChild(card);
    }
  });
}

function appendLog(text, cls = '') {
  const entries = document.getElementById('log-entries');
  const div = document.createElement('div');
  div.className = `log-entry${cls ? ' ' + cls : ''}`;
  div.textContent = text;
  entries.appendChild(div);
  entries.scrollTop = entries.scrollHeight;
  // Keep at most 80 log lines
  while (entries.children.length > 80) entries.removeChild(entries.firstChild);
}
```

- [ ] **Step 2: Commit**

```bash
git add ausbau/html5/js/schieber.js
git commit -m "feat: add render functions to schieber.js"
```

---

## Task 14: Frontend JS — message handlers

**Files:**
- Modify: `ausbau/html5/js/schieber.js` (append)

- [ ] **Step 1: Append game_start, trump, weis handlers**

Append to `ausbau/html5/js/schieber.js`:
```javascript
// ─── Message handlers ─────────────────────────────────────────────────────────

function onGameStart(msg) {
  state.hand = msg.hand;
  state.scores = msg.scores;
  state.targetScore = msg.target;
  state.cardCounts = { compe: 9, compn: 9, compo: 9 };
  state.trick = { comps: null, compn: null, compo: null, compe: null };
  state.validCards = [];
  state.operator = null;
  document.getElementById('score-target').textContent = `Ziel: ${msg.target}`;
  document.getElementById('trump-badge').classList.add('hidden');
  document.getElementById('active-player').textContent = `Führt: ${msg.first_player}`;
  renderAIBar();
  renderHand();
  renderTrickArea();
  appendLog(`--- Neues Spiel — ${msg.first_player} führt ---`);
}

function onTrumpChosen(msg) {
  state.operator = msg.suit;
  const badge = document.getElementById('trump-badge');
  badge.classList.remove('hidden');
  document.getElementById('trump-value').textContent =
    `${SUIT_EMOJI[msg.suit] ?? ''} ${msg.suit}`;
  appendLog(`Trumpf: ${msg.suit} (${msg.by})`);
}

function onTrumpRequest(msg) {
  const modal = document.getElementById('trump-modal');
  const grid = document.getElementById('trump-options');
  const schiebenBtn = document.getElementById('schieben-btn');
  grid.innerHTML = '';

  ['Eicheln', 'Rosen', 'Schellen', 'Schilten', 'Oben', 'Unten'].forEach(mode => {
    const btn = document.createElement('button');
    btn.className = 'suit-btn';
    btn.textContent = `${SUIT_EMOJI[mode] ?? ''} ${mode}`;
    btn.onclick = () => {
      send({ type: 'choose_trump', suit: mode });
      modal.classList.add('hidden');
    };
    grid.appendChild(btn);
  });

  schiebenBtn.classList.toggle('hidden', !msg.can_schieben);
  schiebenBtn.onclick = () => {
    send({ type: 'schieben' });
    modal.classList.add('hidden');
  };

  modal.classList.remove('hidden');
}

function onWeisRequest(msg) {
  const modal = document.getElementById('weis-modal');
  const list = document.getElementById('weis-list');
  list.innerHTML = '';
  let totalPts = 0;

  msg.your_weis.forEach(w => {
    totalPts += w.points;
    const div = document.createElement('div');
    div.className = 'weis-item';
    div.innerHTML =
      `<span class="weis-name">${w.name}</span>` +
      `<span class="weis-suit">${w.suit ?? ''}</span>` +
      `<span class="weis-pts">${w.points} Pkt</span>`;
    list.appendChild(div);
  });

  const announceBtn = document.getElementById('weis-announce-btn');
  announceBtn.textContent = `✓ Ansagen (${totalPts} Pkt)`;
  announceBtn.onclick = () => {
    send({ type: 'declare_weis', weis: msg.your_weis.map(w => w.name), announce: true });
    modal.classList.add('hidden');
  };
  document.getElementById('weis-pass-btn').onclick = () => {
    send({ type: 'declare_weis', weis: [], announce: false });
    modal.classList.add('hidden');
  };

  modal.classList.remove('hidden');
}

function onWeisResult(msg) {
  state.scores.sn = msg.scores.sn;
  state.scores.ow = msg.scores.ow;
  renderScores();
  if (msg.announcements.length === 0) {
    appendLog('Kein Weis im Spiel.');
  } else {
    msg.announcements.forEach(a => {
      const names = a.weis.map(w => w.name).join(', ');
      appendLog(`${a.player} Weis: ${names} → ${a.points} Pkt`);
    });
  }
}

function onYourTurn(msg) {
  state.validCards = msg.valid_cards;
  renderHand();
  document.getElementById('active-player').textContent = 'Am Zug: Du';
  appendLog('Dein Zug.');
}

function onCardPlayed(msg) {
  const key = msg.player_key;
  state.trick[key] = msg.card;

  if (key === 'comps') {
    state.hand = state.hand.filter(c => c !== msg.card);
    state.validCards = [];
  } else {
    if (state.cardCounts[key] !== undefined) state.cardCounts[key]--;
  }

  renderTrickArea();
  renderAIBar();
  renderHand();
  appendLog(`${msg.player} spielt ${msg.card}.`);
  document.getElementById('active-player').textContent = '';
}

function onTrickEnd(msg) {
  state.scores.sn = msg.points_sn;
  state.scores.ow = msg.points_ow;
  renderScores();
  appendLog(`Stich → ${msg.winner}  (SN ${msg.points_sn} / OW ${msg.points_ow})`);
  setTimeout(() => {
    state.trick = { comps: null, compn: null, compo: null, compe: null };
    renderTrickArea();
  }, 1200);
}

function onRoundEnd(msg) {
  state.scores.sn = msg.score_sn;
  state.scores.ow = msg.score_ow;
  renderScores();
  appendLog(`=== Rundenende: SN ${msg.score_sn} / OW ${msg.score_ow} ===`);
}

function onGameEnd(msg) {
  state.scores = msg.final_scores;
  renderScores();
  appendLog(`🏆 Spiel vorbei! Gewinner: ${msg.winner_team}`);
  appendLog(`Endstand: SN ${msg.final_scores.sn} / OW ${msg.final_scores.ow}`);
}

// ─── Card play action ─────────────────────────────────────────────────────────

function playCard(code) {
  if (!state.validCards.includes(code)) return;
  state.validCards = [];
  renderHand();
  send({ type: 'play_card', card: code });
}
```

- [ ] **Step 2: Commit**

```bash
git add ausbau/html5/js/schieber.js
git commit -m "feat: add all message handlers and card play to schieber.js"
```

---

## Task 15: End-to-end smoke test

**Files:** none (manual test)

- [ ] **Step 1: Start the server**

```bash
cd /mnt/archive/Dokumente/Schieber_neu
python -m uvicorn ausbau.server:app --port 8765
```

- [ ] **Step 2: Open in browser**

Navigate to `http://localhost:8765`. Expected:
- Green table visible with AI bar at top and empty hand area
- Connection message appears in game log: "Verbunden — Karten werden verteilt…"
- 9 card backs appear in your hand

- [ ] **Step 3: Play a full Spiel**

- Trump modal appears (if you are first player in Spiel 4) or trump is auto-chosen
- Click a suit to choose trump
- Your valid cards glow gold
- Click a gold card — it moves to the trick center (your slot)
- AI players play their cards in sequence (0.8s delay each)
- After 4 cards: trick clears after 1.2s, scores update
- After 9 tricks: round_end message in log

- [ ] **Step 4: Verify AI cycles all 4 Spiele**

Wait for Spiele 1–4 to complete (AI leads first three). Score accumulates.

- [ ] **Step 5: Run all unit tests one final time**

```bash
cd /mnt/archive/Dokumente/Schieber_neu
python -m pytest tests/test_game_session.py -v
```
Expected: all tests PASS.

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat: complete Schieber HTML5 frontend with FastAPI WebSocket backend"
```
