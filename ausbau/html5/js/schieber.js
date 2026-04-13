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
