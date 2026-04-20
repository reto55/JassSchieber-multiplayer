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
  // Running team totals are still optional fields used to refresh the scoreboard.
  if (typeof msg.points_sn === 'number') state.scores.sn = msg.points_sn;
  if (typeof msg.points_ow === 'number') state.scores.ow = msg.points_ow;
  renderScores();

  // Per-trick value (new required field per protocol skill). Be defensive:
  // older backends / test harnesses may omit it, in which case we log without it.
  const trickPts = msg.points;
  if (typeof trickPts === 'number') {
    appendLog(`Stich: ${msg.winner} (${trickPts} Punkte)`);
  } else {
    appendLog(`Stich: ${msg.winner}`);
  }

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

  // New protocol fields (batch C):
  //   winner_team: "sn" | "ow" | "tie" — which team led THIS round.
  //   target: game-end target; already initialized from game_start. We do NOT
  //   overwrite state.targetScore here; game_start is the single source of
  //   truth for the session-stable target. msg.target is ignored on purpose
  //   (values should match; silently trusting game_start keeps one owner).
  if (msg.winner_team === 'sn') {
    appendLog('Runde: Team SN');
  } else if (msg.winner_team === 'ow') {
    appendLog('Runde: Team OW');
  } else if (msg.winner_team === 'tie') {
    appendLog('Runde: Unentschieden');
  }
}

function onGameEnd(msg) {
  state.scores = msg.final_scores;
  renderScores();
  const teamLabel = msg.winner_team === 'sn' ? 'Team SN'
                  : msg.winner_team === 'ow' ? 'Team OW'
                  : msg.winner_team === 'tie' ? 'Unentschieden'
                  : msg.winner_team;
  appendLog(`🏆 Spiel vorbei! Gewinner: ${teamLabel}`);
  appendLog(`Endstand: SN ${msg.final_scores.sn} / OW ${msg.final_scores.ow}`);
}

// ─── Card play action ─────────────────────────────────────────────────────────

function playCard(code) {
  if (!state.validCards.includes(code)) return;
  state.validCards = [];
  renderHand();
  send({ type: 'play_card', card: code });
}
